// PATCH /api/todos/{id} {"task"?, "status"?} -> PATCH {API}/todos/{id}
export default defineEventHandler(async (event) => {
  const id = encodeURIComponent(getRouterParam(event, "id")!);
  const { task, status } = await readBody(event);
  return todoApi<Todo>(event, `/${id}`, {
    method: "PATCH",
    body: { task, status },
  });
});
