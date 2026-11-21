// Nuxt configuration for the TodoList SSR frontend.
//
// Everything under runtimeConfig can be overridden when the server starts,
// with an environment variable named after the key (NUXT_ + SNAKE_CASE), so
// one image works in any cluster:
//   apiBaseUrl  -> NUXT_API_BASE_URL   (server only, never sent to the browser)
//   public.user -> NUXT_PUBLIC_USER    (also available in the browser)
export default defineNuxtConfig({
  compatibilityDate: "2026-11-01",
  devtools: { enabled: false },

  runtimeConfig: {
    // Where the Nuxt server reaches the todolist API, e.g. the in-cluster
    // Service http://todolist-api:8080. A trailing /todos is accepted too.
    apiBaseUrl: "http://localhost:8080",
    public: {
      // Optional; the page title becomes "{user}'s TODOS".
      user: "",
    },
  },

  app: {
    head: {
      title: "TodoList Nuxt",
      link: [{ rel: "icon", type: "image/x-icon", href: "/favicon.ico" }],
    },
  },
});
