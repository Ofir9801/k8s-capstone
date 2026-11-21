// DELETE /api/todos/{id} -> DELETE {API}/todos/{id}
export default defineEventHandler(async (event) => {
  const id = encodeURIComponent(getRouterParam(event, "id")!);
  await todoApi(event, `/${id}`, { method: "DELETE" });
  setResponseStatus(event, 204);
  return null;
});
