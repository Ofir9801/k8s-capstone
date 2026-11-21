# Todo List capstone

This directory is the starting point for the course capstone: a three-tier,
web-based Todo List application deployed with Kustomize. Students build the
application in stages, retaining the completed data layer while adding each
subsequent layer.

`base/` defines the shared `todolist` namespace and a `todolist` ServiceAccount that carries
the `regcred` image-pull Secret, so Pods can pull private images (create the Secret in the
namespace first: `./scripts/create-ghcrio-secret -u <github-user> -p <token> -- -n todolist`). The data-layer overlay is
complete; students make each later overlay deployable as they add its resources.

> **Note: ServiceAccount and image pulls.** The provided `kustomization.yaml` files of
> 4.0, 4.1 and 4.2 include the `components/todolist-sa` component, which sets
> `serviceAccountName: todolist` on every Deployment, StatefulSet and Job. Keep that
> `components:` entry, and don't set `serviceAccountName` in your own workloads (until
> 7.0). Without it your Pods run as the namespace's `default` ServiceAccount, which has
> no pull Secret, and private images end in `ImagePullBackOff`.

The application source is included in this repository:
[`src/todolist-api`](src/todolist-api/README.md) is the Go/Fiber REST API
and [`src/todolist-nuxt`](src/todolist-nuxt/README.md) is the web UI, a Vue app rendered on the server with Nuxt (the earlier [`src/todolist-vue`](src/todolist-vue/README.md) single-page app is kept only for reference). Your YAML
refers to their images as `ghcr.io/<you>/todolist-api:1.0` and
`ghcr.io/<you>/todolist-nuxt:1.0`, where `<you>` is your GitHub user in lower case:
build and push your own images first (see each source README).

Optional desktop clients run on your laptop against the API:

- [`src/todolist-tk`](src/todolist-tk/README.md): Python with Tkinter

The main path adds the API, web UI, Gateway API routing, autoscaling, probes,
RBAC, NetworkPolicies, personalization, and scheduled backups.

Overlay names are `<session>.<step>-<topic>`, the same scheme as
[`classroom-samples/helloworld`](../classroom-samples/helloworld/README.md).

| Overlay | Status and expected addition |
| --- | --- |
| [`4.0-data`](overlays/4.0-data/README.md) | Complete starting layer: MariaDB, initialization SQL, persistent storage, and database verification jobs. |
| [`4.1-api`](overlays/4.1-api/README.md) | Exercise: add a Todo List API that connects to the `backend` MariaDB Service and implements task create, read, update, and delete operations. |
| [`4.2-webui`](overlays/4.2-webui/README.md) | Exercise: add a web UI Service and Deployment that uses the Todo List API. |
| [`5.0-gateway-api`](overlays/5.0-gateway-api/README.md) | Exercise: add a Gateway and an HTTPRoute that expose the web UI at `/` and the API at `/api/v1`. |
| [`5.1-https`](overlays/5.1-https/README.md) | On top of `5.0-gateway-api` (a side branch, not on the main path): serve the web UI and the API over HTTPS with a self-signed certificate and redirect HTTP to HTTPS. |

### Generating the final-project Helm chart from your overlays

Generating the chart from your overlays (for example with an AI assistant) is the
recommended approach. Overlays are cumulative: each one includes every overlay before it
(`6.1-probes` includes `6.0-hpa`, `8.1-backup` the whole main path), and `5.1-https`
branches off `5.0-gateway-api`, so `6.0-hpa` and later do not include it.

Choose the base overlay to match the features you built. API and web UI are mandatory;
the rest is optional (grading: Week 8, slide 34). If you skip a feature, every later
overlay still contains it, so remove it from the generated chart, or keep it behind a
values toggle that is off by default. If you built HTTPS, add the `5.1-https` changes on top.

