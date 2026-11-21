# Stage 5.0: Gateway API layer

Extend the [web UI overlay](../4.2-webui/README.md) so users reach the
Todo List application through one entry point, using the Kubernetes Gateway API
(Envoy Gateway, as in the Week 5 hands-on).

Add a Gateway and an HTTPRoute that:

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
