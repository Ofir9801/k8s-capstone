// GET /api/todos -> GET {API}/todos
export default defineEventHandler((event) => todoApi<Todo[]>(event, ""));
