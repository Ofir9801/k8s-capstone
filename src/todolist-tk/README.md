# Desktop (fat client) frontend for the Todo List API

A desktop app that talks directly to the [todolist API](../todolist-api/README.md)
over HTTP. Unlike the [web UI](../todolist-nuxt/README.md), nothing is
deployed to the cluster for it: it runs on your laptop and only needs the API's
URL.

It is a single Python file that uses only the standard library (`tkinter` for
the window, `urllib` for HTTP), so there is nothing to `pip install`, and the
same file runs on Linux, macOS and Windows.

## Requirements

Python 3.8 or newer with Tk support:

| OS | What to install |
| --- | --- |
| Windows | Python from [python.org](https://www.python.org/downloads/) (Tk is included) |
| macOS | Python from python.org (Tk included), or with Homebrew: `brew install python python-tk` |
| Debian / Ubuntu | `sudo apt install python3 python3-tk` |
| Fedora | `sudo dnf install python3 python3-tkinter` |

Check with `python3 -m tkinter` — a small test window should open.

## Running

Point the app at the API. With the `todolist-api` `LoadBalancer` Service from
stage [4.1-api](../../overlays/4.1-api/README.md):

```bash
kubectl get svc todolist-api -n todolist
```

```bash
python3 todolist.py --api-url http://<EXTERNAL-IP>:8080
```

Without a load balancer (e.g. on a local cluster), port-forward the Service and
use the default URL `http://localhost:8080`:

```bash
kubectl port-forward -n todolist svc/todolist-api 8080:8080
```

```bash
python3 todolist.py
```

The URL can also be set with the `TODO_API_URL` environment variable, or
changed at any time in the **API** field at the top of the window (press
Enter or **Connect**). On Windows use `py todolist.py` if `python3` is not on
the `PATH`.

## Running in a container (Linux)

The [Dockerfile](Dockerfile) packages the app with Python and Tk, so the host
needs no Python at all. Because it is a GUI app, the container draws on the
host's X11 display: mount the X socket and pass `DISPLAY`. `--network host`
lets the container reach `localhost:8080` (e.g. a port-forward) on the host.

```bash
podman build -t todolist-tk src/todolist-tk
```

```bash
podman run --rm --userns=keep-id --network host \
  -e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
  -e TODO_API_URL=http://localhost:8080 \
  todolist-tk
```

With `docker`, replace `--userns=keep-id` with `--user $(id -u):$(id -g)`.
If the window does not open (`couldn't connect to display`), allow local
containers to use the display with `xhost +local:` and retry. On a Wayland
desktop this works through XWayland, which is on by default in GNOME and KDE.

On macOS and Windows a container needs an extra X server (XQuartz, or WSLg on
Windows 11), so running `todolist.py` directly is simpler there.

## Using the app

- Type a task and press Enter (or **Add**) to create it.
- Select one or more rows (Ctrl/Shift-click) and use **Mark Todo / In
  Progress / Complete**, or press Space to move a task to its next status.
- Double-click a row (or **Edit…**) to rename it; press Delete (or **Delete**)
  to remove the selection.
- **Show** filters by status; click a column header to sort, click it again to
  reverse.
- **Reload** re-reads the list, e.g. after another client changed it. The
  status bar at the bottom shows what the app is doing and any API errors.

## How it works

`todolist.py` has two parts:

- `TodoApi` — a small REST client with one method per API route
  (`list`, `create`, `update`, `delete`). It has no GUI dependency and can be
  reused from scripts:

  ```python
  from todolist import TodoApi
  api = TodoApi("http://localhost:8080")
  api.create("Write the Ingress")
  print(api.list())
  ```

- `TodoApp` — the Tk window. API calls run on a background thread so the
  window stays responsive while the cluster answers; results are handed back to
  the Tk thread through a queue.

Because the browser is not involved, CORS does not apply to this client.

## Why Tkinter?

The goal was a client that students can run on any laptop with minimal setup.
Alternatives considered:

| Option | Pros | Cons |
| --- | --- | --- |
| **Python + Tkinter** (chosen) | Standard library only, one file, readable code | Plain look; Linux needs the `python3-tk` package |
| Python + [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) | Modern look, same Tk code style | One extra `pip` dependency |
| [Tauri](https://tauri.app) / [Wails](https://wails.io) | Reuse the web UI's Vue code as a native app, small binaries | Rust or Go toolchain plus Node to build |

## License

[MIT License](../todolist-api/LICENSE)
