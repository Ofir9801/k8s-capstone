import type { H3Event } from "h3";

export interface Todo {
  id: number;
  task: string;
  status: string;
}

interface ApiRequest {
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  body?: Record<string, unknown>;
}

// URL of the API's /todos collection, built from runtime config
// (NUXT_API_BASE_URL). Both "http://host:8080" and "http://host:8080/todos"
// are accepted, like the desktop clients do.
function todosUrl(event: H3Event): string {
  const base = useRuntimeConfig(event)
    .apiBaseUrl.replace(/\/+$/, "")
    .replace(/\/todos$/, "");
  return `${base}/todos`;
}

// Call the todolist API from the Nuxt server. The API's {"error": "..."}
// replies become Nuxt errors with the same status code and message, so the
// page can show them; a connection failure becomes a 502 Bad Gateway.
export async function todoApi<T>(
  event: H3Event,
  path: string,
  request: ApiRequest = {},
): Promise<T> {
  const url = todosUrl(event) + path;
  try {
    return await $fetch<T>(url, request);
  } catch (err: any) {
    throw createError({
      statusCode: err.response?.status ?? 502,
      message: err.data?.error ?? `Cannot reach the API at ${url}`,
    });
  }
}
