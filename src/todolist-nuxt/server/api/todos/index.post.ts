// POST /api/todos {"task"} -> POST {API}/todos
export default defineEventHandler(async (event) => {
  const { task } = await readBody(event);
  const created = await todoApi<Todo>(event, "", {
    method: "POST",
    body: { task },
  });
  setResponseStatus(event, 201);
  return created;
});
