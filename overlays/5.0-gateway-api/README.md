# Stage 5.0: Gateway API layer

Extend the [web UI overlay](../4.2-webui/README.md) so users reach the
Todo List application through one entry point, using the Kubernetes Gateway API
(Envoy Gateway, as in the Week 5 hands-on).

Add a Gateway and **one** HTTPRoute that:

- listen for HTTP traffic for your own host name, `todolist.<name-or-github-id>.local`
  (lowercase, e.g. `todolist.dana-levi.local`), mapped to the Gateway's address in `/etc/hosts`;
- route `/api/v1` to the `todolist-api` Service on port 8080, rewriting the
  prefix to `/` with a `URLRewrite` filter: the API serves `/todos`, so
  `http://todolist.<name>.local/api/v1/todos` must reach it as `/todos` (for the desktop
  clients, whose API URL becomes `http://todolist.<name>.local/api/v1`);
- route all other paths to the web UI Service on port 80; and
- patch the API and web UI Services to `ClusterIP`, leaving the Gateway as the
  public entry point.

The web UI does not use `/api/v1`: its server keeps calling the API at
`http://todolist-api:8080` inside the cluster, so `todolist-nuxt-config` does not
change.

Include the web UI, API, and data layers so the complete
application can be deployed with:

```bash
kubectl apply -k .
```

## Think about it: one HTTPRoute or two?

In the Week 5 hands-on, helloworld and hellocolors each had their own HTTPRoute
on one shared Gateway. You could do the same here, with one route for the web UI
(`/`) and one for the API (`/api/v1`). Submit a single HTTPRoute as asked above,
and be ready to discuss these questions in class:

1. Why did helloworld and hellocolors get separate routes? Does the same reason
   apply to the Todo List?
2. Both routes would use the same host name. How would the Gateway decide where
   `/api/v1/todos` goes? Would the order of the routes, or of the files in
   `kustomization.yaml`, matter?
3. In stage 5.1 (HTTPS), what would you have to change for each route? What would
   happen to `http://todolist.<name>.local/api/v1/todos` if you forgot one of them?
4. What could you do with a separate API route that is awkward with a single one?
5. What would the split cost you?
