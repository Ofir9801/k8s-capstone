# Server-side rendered (Nuxt) frontend for the Todo List API

The Todo List web UI used in the capstone from stage
[4.2](../../overlays/4.2-webui/README.md) on. It is built with
[Nuxt](https://nuxt.com), so the page is **rendered on the server**: the
browser never calls the [todolist API](../todolist-api/README.md) itself, it
only talks to the Nuxt server, which calls the API inside the cluster.

It replaces the earlier [Vue web UI](../todolist-vue/README.md) (same features,
same look), which is kept only for reference.

It always runs as a container: the [Dockerfile](Dockerfile) installs Node.js
and the dependencies and builds the app inside the image, so you need only
`podman` (or `docker`), not Node.js.

## Building the image

From the capstone project folder (the one that contains `src/`):

```bash
podman build -t todolist-nuxt src/todolist-nuxt
```

The [Dockerfile](Dockerfile) has two stages: the first runs `npm ci` and
`npm run build`; the second copies only the built `.output/` folder (a
self-contained server, no `npm install` needed) into a clean Node image and
runs it as the unprivileged `node` user on port `3000`.

To push it to a registry for the cluster, see
[Push the image to a registry](#push-the-image-to-a-registry).

## Running locally

To try the image on your laptop, port-forward the API Service from stage
[4.1-api](../../overlays/4.1-api/README.md) so it answers on
`http://localhost:8080`, the default API URL:

```bash
kubectl port-forward -n todolist svc/todolist-api 8080:8080
```

In a second terminal run the container. `--network host` lets it reach
`localhost:8080` on the host:

```bash
podman run --rm --network host -e NUXT_PUBLIC_USER=benny todolist-nuxt
```

Open http://localhost:3000. `docker` works the same way. Change the API URL
or the title with the variables in [Runtime configuration](#runtime-configuration).

## Server-side rendering compared with the Vue SPA

The Vue UI is a *single-page application* (SPA). Its server only hands out an
empty page (`<div id="app"></div>`) plus JavaScript. The browser runs the
JavaScript, which then calls `GET /todos` on the API and draws the list.

With Nuxt the first `GET /todos` happens **on the server**:

```
Vue SPA:   browser ──GET /──▶ server            (empty HTML + JS)
           browser ──GET /todos──▶ API          (browser calls the API)

Nuxt SSR:  browser ──GET /──▶ Nuxt server ──GET /todos──▶ API
                     ◀── HTML with the todos already in it
           browser ──POST /api/todos──▶ Nuxt server ──POST /todos──▶ API
```

You can see the difference without any tools: open the page, then **View Page
Source** (Ctrl+U). In the Nuxt UI the source already contains every task;
in the Vue UI it contains only the empty `<div id="app">`. From the command
line:

```bash
curl -s http://localhost:3000/ | grep -o 'value="[^"]*" aria-label="Edit task"'
```

After the HTML arrives, the browser loads the JavaScript and *hydrates* the
page: Vue attaches its event handlers to the HTML that is already there,
without fetching the list again. From then on the app behaves like the SPA.

What this means for deployment:

| | Vue SPA | Nuxt SSR |
| --- | --- | --- |
| Who calls the API | the browser | the Nuxt server |
| API URL | must be reachable **from the browser** (a LoadBalancer IP, or `/todos` behind an Ingress) | only needs to be reachable **from the Nuxt Pod** (`http://todolist-api:8080`) |
| CORS | needed when the API is on another host | not needed: the browser only talks to the Nuxt server |
| API exposed outside the cluster | yes | not for the web UI (the course still routes `/todos` for the [desktop clients](../todolist-tk/README.md)) |
| First page | empty until the JavaScript has run | complete HTML, also without JavaScript |
| Theme | read from `localStorage` after load | read from a cookie, so the server renders it (no flash) |

The price is a real server process per request instead of static files, and a
bit more to understand about what runs where.

## Runtime configuration

Nuxt reads its settings from `runtimeConfig` in [`nuxt.config.ts`](nuxt.config.ts).
Each key can be overridden **when the server starts** by an environment variable
named `NUXT_` plus the key in `SNAKE_CASE`, so one image works in any cluster:

| Variable | Meaning | Default |
| --- | --- | --- |
| `NUXT_API_BASE_URL` | Where the **Nuxt server** reaches the API. A trailing `/todos` is accepted (`http://todolist-api:8080/todos` works too). Never sent to the browser. | `http://localhost:8080` |
| `NUXT_PUBLIC_USER` | Optional name; the title becomes "{USER}'s TODOS". `public` keys are also available in the browser. | empty ("My TODOS") |
| `PORT` | Port the server listens on | `3000` |

In the cluster these come from the `todolist-nuxt-config` ConfigMap, loaded
with `envFrom` (see [4.2-webui](../../overlays/4.2-webui/README.md)). Its keys
are the variable names, so no mapping is needed:

```yaml
data:
  NUXT_API_BASE_URL: "http://todolist-api:8080"   # the API Service's DNS name
  NUXT_PUBLIC_USER: ""
```

Because the URL is the Service's in-cluster DNS name, it is the same in every
cluster: unlike the Vue UI, there is no external IP to look up.

A title image mounted at `/opt/images/title-image.png` (stage
8.0-personalize) is shown next to
the title, as in the Vue UI; without one the TodoList icon is shown.

## Push the image to a registry

Build and push with `docker` or `podman` (the commands are the same), from the
capstone project folder (the one that contains `src/`):

```bash
docker build -t ghcr.io/<you>/todolist-nuxt:1.0 src/todolist-nuxt
docker push ghcr.io/<you>/todolist-nuxt:1.0
```

Or use the [`Makefile`](Makefile) in this folder, which runs the same two
commands (`podman` by default, `CONTAINER_TOOL=docker` to switch):

```bash
OWNER=<you> VERSION=1.0 make -C src/todolist-nuxt push     # build + push
OWNER=<you> VERSION=1.0 make -C src/todolist-nuxt build    # build only
make -C src/todolist-nuxt                                  # show settings and targets
```

The image is tagged `$REGISTRY/$OWNER/todolist-nuxt:$VERSION`, e.g.
`ghcr.io/<you>/todolist-nuxt:1.0`.

## Using the app

- Type a task and press Enter (or **Add**) to create it.
- Change a task's **Status** with its drop-down.
- Edit a task's text in place; the change is saved when you press Enter or
  leave the field.
- The trash button deletes a task.
- **Filter** shows one status; **Sort** orders by ID or status, and the arrow
  button reverses the order.
- **Reload** re-reads the list, e.g. after another client changed it. The
  moon/sun button switches between dark and light themes.

## How it works

| File | Runs on | What it does |
| --- | --- | --- |
| [`app/app.vue`](app/app.vue) | server, then browser | The page. `useFetch("/api/todos")` loads the list during server rendering; the add/edit/delete handlers call `/api/todos` from the browser with `$fetch`. |
| [`server/api/todos/`](server/api/todos) | server | One file per route and method (`index.get.ts`, `index.post.ts`, `[id].patch.ts`, `[id].delete.ts`): the Nuxt server routes the browser calls. Each one forwards the request to the API. |
| [`server/utils/todoApi.ts`](server/utils/todoApi.ts) | server | Builds the API URL from `NUXT_API_BASE_URL` and turns the API's `{"error": "..."}` replies into errors the page can show. |
| [`server/routes/title-image.png.ts`](server/routes/title-image.png.ts) | server | Serves the mounted title image, or redirects to the icon. |
| [`nuxt.config.ts`](nuxt.config.ts) | build time | Runtime config keys and their defaults, page title and icon. |

Nuxt finds these files by their folder and name, so there is no router or
server setup code: `server/api/todos/[id].patch.ts` *is* the handler for
`PATCH /api/todos/:id`.

The server routes map one-to-one to the API:

| Browser calls (Nuxt server) | Nuxt server calls (API) |
| --- | --- |
| `GET /api/todos` | `GET /todos` |
| `POST /api/todos` `{"task"}` | `POST /todos` |
| `PATCH /api/todos/{id}` `{"task"?, "status"?}` | `PATCH /todos/{id}` |
| `DELETE /api/todos/{id}` | `DELETE /todos/{id}` |

Supported statuses: `Todo`, `In Progress`, `Complete`.

## Troubleshooting

**"Cannot reach the API at …" next to the title**
- The Nuxt **server** could not connect to the API. Check `NUXT_API_BASE_URL`
  from the server's point of view: `localhost` inside a container or Pod is the
  container itself, so in the cluster use the Service name
  (`http://todolist-api:8080`).
- Locally, check that the `kubectl port-forward` is still running.

**The page shows the list but buttons do nothing**
- The JavaScript did not load (look in the browser console). The list itself
  comes from the server, so it is visible even without JavaScript.

## License

[MIT License](../todolist-api/LICENSE)
