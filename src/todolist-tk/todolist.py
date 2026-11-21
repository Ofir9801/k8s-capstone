#!/usr/bin/env python3
"""Fat-client desktop frontend for the todolist API.

Uses only the Python standard library (tkinter + urllib), so it runs on
Linux, macOS and Windows with no `pip install`.

    python3 todolist.py                              # http://localhost:8080
    python3 todolist.py --api-url http://1.2.3.4:8080
    TODO_API_URL=http://1.2.3.4:8080 python3 todolist.py
"""

import argparse
import json
import os
import queue
import threading
import urllib.error
import urllib.request

try:
    import tkinter as tk
    from tkinter import messagebox, simpledialog, ttk
except ImportError:  # e.g. Debian/Ubuntu without the python3-tk package
    tk = None

STATUS_OPTIONS = ("Todo", "In Progress", "Complete")
DEFAULT_API_URL = "http://localhost:8080"


# --------------------------------------------------------------------------
# API client
# --------------------------------------------------------------------------


class ApiError(Exception):
    pass


class TodoApi:
    """Thin client for the todolist REST API (see ../todolist-api/README.md)."""

    def __init__(self, base_url, timeout=5):
        # Accept the API's own /todos URL too (the $API the slides set, or the
        # Vue UI's API_BASE_URL): the routes below add /todos themselves.
        base_url = base_url.rstrip("/")
        if base_url.endswith("/todos"):
            base_url = base_url[: -len("/todos")]
        self.base_url = base_url
        self.timeout = timeout

    def _request(self, method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(
            self.base_url + path,
            data=data,
            method=method,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read()
        except urllib.error.HTTPError as e:
            # The API returns {"error": "..."} on failures
            try:
                msg = json.loads(e.read()).get("error", e.reason)
            except Exception:
                msg = e.reason
            raise ApiError(f"{method} {path}: {e.code} {msg}") from None
        except (urllib.error.URLError, OSError) as e:
            reason = getattr(e, "reason", e)
            raise ApiError(f"Cannot reach {self.base_url}: {reason}") from None
        return json.loads(raw) if raw else None

    def list(self):
        return self._request("GET", "/todos")

    def create(self, task):
        return self._request("POST", "/todos", {"task": task})

    def update(self, todo_id, task=None, status=None):
        body = {}
        if task is not None:
            body["task"] = task
        if status is not None:
            body["status"] = status
        return self._request("PATCH", f"/todos/{todo_id}", body)

    def delete(self, todo_id):
        return self._request("DELETE", f"/todos/{todo_id}")


# --------------------------------------------------------------------------
# GUI
# --------------------------------------------------------------------------


class TodoApp:
    """Main window. Network calls run on a worker thread so the UI never freezes;
    their results come back to the Tk thread through a queue polled with after()."""

    COLUMNS = (("id", "ID", 60), ("task", "Task", 380), ("status", "Status", 110))

    def __init__(self, root, api_url):
        self.root = root
        self.api = TodoApi(api_url)
        self.todos = []
        self.results = queue.Queue()
        self.busy = 0

        root.title("Todo List")
        root.geometry("640x480")
        root.minsize(480, 320)

        self.url_var = tk.StringVar(value=api_url)
        self.task_var = tk.StringVar()
        self.filter_var = tk.StringVar(value="All")
        self.status_var = tk.StringVar(value="")

        self._build()
        self._poll_results()
        self.reload()

    # ---- layout --------------------------------------------------------

    def _build(self):
        pad = {"padx": 6, "pady": 4}
        main = ttk.Frame(self.root, padding=8)
        main.pack(fill="both", expand=True)

        # API URL row
        row = ttk.Frame(main)
        row.pack(fill="x")
        ttk.Label(row, text="API:").pack(side="left")
        url = ttk.Entry(row, textvariable=self.url_var)
        url.pack(side="left", fill="x", expand=True, **pad)
        url.bind("<Return>", lambda e: self.connect())
        ttk.Button(row, text="Connect", command=self.connect).pack(side="left")
        ttk.Button(row, text="Reload", command=self.reload).pack(side="left", padx=(6, 0))

        # Add-todo row
        row = ttk.Frame(main)
        row.pack(fill="x", pady=(8, 0))
        entry = ttk.Entry(row, textvariable=self.task_var)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        entry.bind("<Return>", lambda e: self.add())
        entry.focus_set()
        ttk.Button(row, text="Add", command=self.add).pack(side="left")

        # Filter row
        row = ttk.Frame(main)
        row.pack(fill="x", pady=(8, 0))
        ttk.Label(row, text="Show:").pack(side="left")
        for value in ("All",) + STATUS_OPTIONS:
            ttk.Radiobutton(
                row, text=value, value=value, variable=self.filter_var, command=self.render
            ).pack(side="left", padx=4)

        # Todo table
        frame = ttk.Frame(main)
        frame.pack(fill="both", expand=True, pady=(8, 0))
        self.tree = ttk.Treeview(
            frame, columns=[c[0] for c in self.COLUMNS], show="headings", selectmode="extended"
        )
        for key, title, width in self.COLUMNS:
            self.tree.heading(key, text=title, command=lambda k=key: self.sort_by(k))
            self.tree.column(key, width=width, stretch=(key == "task"),
                             anchor="center" if key != "task" else "w")
        scroll = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.tree.tag_configure("Complete", foreground="gray")
        self.tree.tag_configure("In Progress", foreground="#b36b00")
        self.tree.bind("<Double-1>", lambda e: self.edit_task())
        self.tree.bind("<Delete>", lambda e: self.delete())
        self.tree.bind("<space>", lambda e: self.cycle_status())

        # Action buttons
        row = ttk.Frame(main)
        row.pack(fill="x", pady=(8, 0))
        for status in STATUS_OPTIONS:
            ttk.Button(row, text=f"Mark {status}",
                       command=lambda s=status: self.set_status(s)).pack(side="left", padx=(0, 6))
        ttk.Button(row, text="Edit…", command=self.edit_task).pack(side="left", padx=(0, 6))
        ttk.Button(row, text="Delete", command=self.delete).pack(side="right")

        # Status bar
        ttk.Label(main, textvariable=self.status_var, anchor="w").pack(fill="x", pady=(6, 0))

        self.sort_key, self.sort_reverse = "id", True

    # ---- background work -------------------------------------------------

    def run_async(self, fn, on_done, message):
        """Run fn() on a worker thread; call on_done(result) on the Tk thread."""
        self.busy += 1
        self.status_var.set(message)
        self.root.configure(cursor="watch")

        def worker():
            try:
                self.results.put((on_done, fn(), None))
            except ApiError as e:
                self.results.put((on_done, None, e))

        threading.Thread(target=worker, daemon=True).start()

    def _poll_results(self):
        try:
            while True:
                on_done, result, error = self.results.get_nowait()
                self.busy -= 1
                if not self.busy:
                    self.root.configure(cursor="")
                if error:
                    self.status_var.set(f"Error: {error}")
                else:
                    on_done(result)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_results)

    # ---- actions ---------------------------------------------------------

    def connect(self):
        self.api = TodoApi(self.url_var.get().strip() or DEFAULT_API_URL)
        self.reload()

    def reload(self):
        def done(todos):
            self.todos = todos or []
            self.render()
            self.status_var.set(f"{len(self.todos)} todos from {self.api.base_url}")

        self.run_async(self.api.list, done, f"Loading from {self.api.base_url}…")

    def add(self):
        task = self.task_var.get().strip()
        if not task:
            return
        self.task_var.set("")
        self.run_async(lambda: self.api.create(task), lambda _: self.reload(), "Adding…")

    def selected_ids(self):
        return [int(iid) for iid in self.tree.selection()]

    def set_status(self, status, ids=None):
        ids = ids or self.selected_ids()
        if not ids:
            self.status_var.set("Select one or more todos first")
            return

        def work():
            for todo_id in ids:
                self.api.update(todo_id, status=status)

        self.run_async(work, lambda _: self.reload(), f"Marking {len(ids)} as {status}…")

    def cycle_status(self):
        by_id = {t["id"]: t for t in self.todos}
        for todo_id in self.selected_ids():
            current = by_id[todo_id].get("status") or "Todo"
            nxt = STATUS_OPTIONS[(STATUS_OPTIONS.index(current) + 1) % len(STATUS_OPTIONS)] \
                if current in STATUS_OPTIONS else "Todo"
            self.set_status(nxt, [todo_id])

    def edit_task(self):
        ids = self.selected_ids()
        if len(ids) != 1:
            self.status_var.set("Select exactly one todo to edit")
            return
        todo = next(t for t in self.todos if t["id"] == ids[0])
        text = simpledialog.askstring("Edit todo", f"Task #{todo['id']}:",
                                      initialvalue=todo["task"], parent=self.root)
        if text and text.strip() and text.strip() != todo["task"]:
            self.run_async(lambda: self.api.update(todo["id"], task=text.strip()),
                           lambda _: self.reload(), "Saving…")

    def delete(self):
        ids = self.selected_ids()
        if not ids or not messagebox.askyesno(
                "Delete", f"Delete {len(ids)} todo(s)?", parent=self.root):
            return

        def work():
            for todo_id in ids:
                self.api.delete(todo_id)

        self.run_async(work, lambda _: self.reload(), f"Deleting {len(ids)}…")

    # ---- rendering -------------------------------------------------------

    def sort_by(self, key):
        if self.sort_key == key:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_key, self.sort_reverse = key, False
        self.render()

    def render(self):
        selected = set(self.tree.selection())
        self.tree.delete(*self.tree.get_children())
        wanted = self.filter_var.get()
        rows = [t for t in self.todos if wanted == "All" or t.get("status") == wanted]
        sort_keys = {
            "id": lambda t: t["id"],
            "task": lambda t: t["task"].lower(),
            # Workflow order, unknown statuses last
            "status": lambda t: (STATUS_OPTIONS.index(t.get("status"))
                                 if t.get("status") in STATUS_OPTIONS else len(STATUS_OPTIONS)),
        }
        rows.sort(key=sort_keys[self.sort_key], reverse=self.sort_reverse)
        for t in rows:
            iid = str(t["id"])
            status = t.get("status") or ""
            self.tree.insert("", "end", iid=iid, values=(t["id"], t["task"], status),
                             tags=(status,))
            if iid in selected:
                self.tree.selection_add(iid)
        for key, title, _ in self.COLUMNS:
            arrow = (" ▼" if self.sort_reverse else " ▲") if key == self.sort_key else ""
            self.tree.heading(key, text=title + arrow)


def main():
    parser = argparse.ArgumentParser(description="Todolist desktop client")
    parser.add_argument(
        "--api-url",
        default=os.environ.get("TODO_API_URL", DEFAULT_API_URL),
        help=f"todolist API base URL (env TODO_API_URL, default {DEFAULT_API_URL})",
    )
    args = parser.parse_args()

    if tk is None:
        raise SystemExit(
            "tkinter is not installed. Debian/Ubuntu: sudo apt install python3-tk | "
            "Fedora: sudo dnf install python3-tkinter | macOS (Homebrew): brew install python-tk"
        )
    root = tk.Tk()
    TodoApp(root, args.api_url)
    root.mainloop()


if __name__ == "__main__":
    main()
