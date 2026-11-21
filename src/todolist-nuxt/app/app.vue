<template>
    <div class="app">
        <header class="app-header">
            <div class="header-title">
                <img
                    :src="titleImage"
                    alt="Title icon"
                    class="title-image"
                />
                <h1>{{ appTitle }}</h1>
            </div>
            <div class="header-actions">
                <button class="btn" @click="reload" :disabled="loading">
                    Reload
                </button>
                <button
                    class="icon-btn"
                    @click="toggleTheme"
                    :title="
                        theme === 'dark'
                            ? 'Switch to light theme'
                            : 'Switch to dark theme'
                    "
                    aria-label="Toggle theme"
                >
                    <!-- Sun/Moon icon -->
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="18"
                        height="18"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    >
                        <circle
                            v-if="theme === 'light'"
                            cx="12"
                            cy="12"
                            r="5"
                        ></circle>
                        <path
                            v-else
                            d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"
                        ></path>
                    </svg>
                </button>
                <span v-if="loading" class="hint">Loading…</span>
                <span v-if="error" class="error">{{ error }}</span>
            </div>
        </header>

        <section class="card">
            <h2 class="card-title">Add Todo</h2>
            <div class="form-row">
                <input
                    class="input task-input"
                    v-model="newTask"
                    type="text"
                    placeholder="What needs doing?"
                    @keyup.enter="addTodo"
                    aria-label="New todo task"
                />
                <button
                    class="btn primary"
                    @click="addTodo"
                    :disabled="loading"
                >
                    Add
                </button>
            </div>
        </section>

        <section class="toolbar">
            <label for="filter" class="label">Filter:</label>
            <select
                id="filter"
                class="select"
                v-model="filterStatus"
                aria-label="Filter by status"
            >
                <option value="">All</option>
                <option v-for="s in STATUS_OPTIONS" :key="s" :value="s">
                    {{ s }}
                </option>
            </select>
            <label for="sort" class="label">Sort:</label>
            <select
                id="sort"
                class="select"
                v-model="sortBy"
                aria-label="Sort by field"
            >
                <option value="">None</option>
                <option value="id">ID</option>
                <option value="status">Status</option>
            </select>
            <button
                class="btn"
                @click="sortReverse = !sortReverse"
                :title="sortReverse ? 'Ascending' : 'Descending'"
                aria-label="Toggle sort order"
            >
                {{ sortReverse ? "↓" : "↑" }}
            </button>
        </section>

        <div v-if="filteredTodos.length === 0" class="empty">
            No todos to show. Add one above!
        </div>

        <ul class="todo-list">
            <li v-for="todo in filteredTodos" :key="todo.id" class="todo-item">
                <div class="todo-content">
                    <div class="todo-main">
                        <div class="todo-id">#{{ todo.id }}</div>
                        <input
                            class="input task-input"
                            :value="todo.task"
                            @change="updateTodoTask(todo, $event.target.value)"
                            aria-label="Edit task"
                        />
                    </div>
                    <div class="todo-meta">
                        <label class="label">Status</label>
                        <!-- :selected on each option (not :value on the
                             select) so the server-rendered HTML already
                             shows each todo's status before JavaScript runs -->
                        <select
                            class="select"
                            @change="
                                updateTodoStatus(todo, $event.target.value)
                            "
                            aria-label="Edit status"
                        >
                            <option
                                v-for="s in STATUS_OPTIONS"
                                :key="s"
                                :value="s"
                                :selected="s === todo.status"
                            >
                                {{ s }}
                            </option>
                        </select>
                        <button
                            class="icon-btn danger"
                            @click="deleteTodo(todo.id)"
                            :disabled="loading"
                            aria-label="Delete todo"
                            title="Delete"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                width="18"
                                height="18"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="2"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                            >
                                <polyline points="3 6 5 6 21 6"></polyline>
                                <path
                                    d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"
                                ></path>
                                <path d="M10 11v6"></path>
                                <path d="M14 11v6"></path>
                                <path
                                    d="M9 6V4a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"
                                ></path>
                            </svg>
                        </button>
                    </div>
                </div>
            </li>
        </ul>
    </div>
</template>

<script setup>
const STATUS_OPTIONS = ["Todo", "In Progress", "Complete"];

const { user } = useRuntimeConfig().public;
const appTitle = user ? `${user}'s TODOS` : "My TODOS";
// Served by server/routes/title-image.png.ts, not bundled from public/.
const titleImage = "/title-image.png";

// The theme is kept in a cookie (not localStorage) because the browser sends
// cookies with every request: the server already renders the chosen theme,
// so the page does not flash dark-then-light while it loads.
const theme = useCookie("theme", {
    default: () => "dark",
    maxAge: 60 * 60 * 24 * 365,
});
useHead({ htmlAttrs: { "data-theme": theme } });

function toggleTheme() {
    theme.value = theme.value === "dark" ? "light" : "dark";
}

// Server-side rendering: on the first page load this runs on the Nuxt server,
// which calls GET /api/todos (our server route, which calls the API) and puts
// the todos into the HTML. The browser receives the list ready-made and does
// not fetch it again. Later calls (Reload) go from the browser to /api/todos.
const {
    data: todos,
    error: fetchError,
    refresh,
} = await useFetch("/api/todos", {
    default: () => [],
    transform: (list) => list.map((t) => ({ ...t, status: t.status || "Todo" })),
});

const loading = ref(false);
const error = ref(errorMessage(fetchError.value, "Failed to load todos"));
const newTask = ref("");
const filterStatus = ref("");
const sortBy = ref("");
const sortReverse = ref(false);

const filteredTodos = computed(() => {
    let result = todos.value;

    if (filterStatus.value) {
        result = result.filter((t) => t.status === filterStatus.value);
    }

    if (sortBy.value) {
        const key = sortBy.value;
        result = [...result].sort((a, b) => {
            const aVal = key === "id" ? Number(a.id) : a.status;
            const bVal = key === "id" ? Number(b.id) : b.status;
            if (aVal < bVal) return sortReverse.value ? 1 : -1;
            if (aVal > bVal) return sortReverse.value ? -1 : 1;
            return 0;
        });
    }

    return result;
});

// Our server routes answer errors with {"message": "..."}; show that text.
function errorMessage(err, fallback) {
    if (!err) return null;
    return err.data?.message || err.message || fallback;
}

// Run one API call from the browser with the shared loading/error handling.
async function run(fallback, action) {
    loading.value = true;
    error.value = null;
    try {
        await action();
    } catch (err) {
        error.value = errorMessage(err, fallback);
    } finally {
        loading.value = false;
    }
}

function reload() {
    return run("Failed to load todos", async () => {
        await refresh();
        if (fetchError.value) throw fetchError.value;
    });
}

function addTodo() {
    const task = newTask.value.trim();
    if (!task) {
        error.value = "Task cannot be empty";
        return;
    }
    return run("Failed to add todo", async () => {
        const created = await $fetch("/api/todos", {
            method: "POST",
            body: { task },
        });
        todos.value.unshift(created);
        newTask.value = "";
    });
}

function updateTodoStatus(todo, status) {
    if (!STATUS_OPTIONS.includes(status)) {
        error.value = "Invalid status";
        return;
    }
    return run("Failed to update status", async () => {
        await $fetch(`/api/todos/${todo.id}`, {
            method: "PATCH",
            body: { status },
        });
        todo.status = status;
    });
}

function updateTodoTask(todo, newText) {
    const task = String(newText || "").trim();
    if (!task) {
        error.value = "Task cannot be empty";
        return;
    }
    return run("Failed to update task", async () => {
        await $fetch(`/api/todos/${todo.id}`, {
            method: "PATCH",
            body: { task },
        });
        todo.task = task;
    });
}

function deleteTodo(id) {
    return run("Failed to delete todo", async () => {
        await $fetch(`/api/todos/${id}`, { method: "DELETE" });
        todos.value = todos.value.filter((t) => t.id !== id);
    });
}
</script>

<style>
:root {
    /* Dark theme (default) */
    --bg: #0f172a;
    --panel: #111827;
    --muted: #6b7280;
    --text: #e5e7eb;
    --primary: #2563eb;
    --danger: #dc2626;
    --border: #1f2937;
    --accent: #374151;

    /* Controls */
    --control-bg: #0b1220;
    --control-border: var(--accent);
    --control-hover-bg: #0d1426;
}

:root[data-theme="light"] {
    /* Light theme */
    --bg: #f8fafc;
    --panel: #ffffff;
    --muted: #6b7280;
    --text: #0f172a;
    --primary: #2563eb;
    --danger: #dc2626;
    --border: #e5e7eb;
    --accent: #d1d5db;

    /* Controls */
    --control-bg: #ffffff;
    --control-border: var(--accent);
    --control-hover-bg: #f3f4f6; /* light hover */
}

* {
    box-sizing: border-box;
}

html,
body {
    margin: 0;
    padding: 0;
    background: var(--bg);
    color: var(--text);
    font-family:
        system-ui,
        -apple-system,
        Segoe UI,
        Roboto,
        sans-serif;
}

.app {
    max-width: 840px;
    margin: 32px auto;
    padding: 0 16px;
}

.app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 16px;
}

.header-title {
    display: flex;
    align-items: center;
    gap: 10px;
}

.title-image {
    height: 64px;
    width: 64px;
    object-fit: contain;
    flex-shrink: 0;
}

.app-header h1 {
    margin: 0;
    font-size: 28px;
    letter-spacing: 0.2px;
}

.header-actions {
    display: flex;
    gap: 12px;
    align-items: center;
}

.card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
    margin: 12px 0 20px;
    box-shadow: 0 1px 0 rgba(0, 0, 0, 0.15);
}

.card-title {
    margin: 0 0 12px;
    font-size: 18px;
    color: var(--text);
}

.toolbar {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 8px 0 16px;
}

.form-row {
    display: flex;
    gap: 10px;
    align-items: center;
    flex-wrap: wrap;
}
.form-row .task-input {
    flex: 1;
    min-width: 320px;
}

.input,
.select {
    background: var(--control-bg);
    color: var(--text);
    border: 1px solid var(--control-border);
    border-radius: 8px;
    padding: 8px 10px;
    outline: none;
}

.input:focus,
.select:focus {
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2);
}

.task-input {
    flex: 1;
    min-width: 240px;
}

.btn {
    appearance: none;
    border: 1px solid var(--control-border);
    background: var(--control-bg);
    color: var(--text);
    padding: 8px 12px;
    border-radius: 8px;
    cursor: pointer;
    transition:
        transform 0.05s ease,
        background 0.2s ease,
        border-color 0.2s ease;
}

.btn:hover {
    background: var(--control-hover-bg);
    border-color: var(--text);
}

.btn:active {
    transform: translateY(1px);
}

.btn.primary {
    background: var(--primary);
    border-color: var(--primary);
    color: #fff; /* ensure readable text in both themes */
}

.btn.primary:hover {
    background: #1f57d0;
    border-color: #1f57d0;
}

.btn.danger {
    background: var(--danger);
    border-color: var(--danger);
}

/* Icon button style for inline delete */
.icon-btn {
    appearance: none;
    border: 1px solid var(--control-border);
    background: var(--control-bg);
    color: var(--text);
    padding: 6px;
    border-radius: 8px;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    transition:
        transform 0.05s ease,
        background 0.2s ease,
        border-color 0.2s ease;
}

.icon-btn:hover {
    background: var(--control-hover-bg);
    border-color: var(--text);
}

.icon-btn.danger {
    color: #fca5a5;
    border-color: var(--danger);
}

.icon-btn.danger:hover {
    background: #b91c1c;
    color: #fff;
    border-color: #b91c1c;
}

.btn.danger:hover {
    background: #b91c1c;
    border-color: #b91c1c;
}

.label {
    color: var(--muted);
    font-size: 14px;
}

.hint {
    color: var(--muted);
}

.error {
    color: #fca5a5;
}

.empty {
    color: var(--muted);
    font-style: italic;
    padding: 16px;
    text-align: center;
}

.todo-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.todo-item {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 10px;
}

.todo-content {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    justify-content: space-between;
    flex-wrap: wrap;
}

.todo-main {
    display: flex;
    gap: 10px;
    align-items: center;
    flex: 1;
}

.todo-id {
    font-weight: 600;
    color: var(--muted);
}

.todo-meta {
    display: flex;
    gap: 8px;
    align-items: center;
}

.todo-actions {
    margin-top: 8px;
    display: flex;
    justify-content: flex-end;
}
.app-footer {
    margin-top: 24px;
    color: var(--muted);
    text-align: center;
}
</style>
