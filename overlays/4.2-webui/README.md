# Stage 4.2: Web UI layer

Extend the [API-layer overlay](../4.1-api/README.md) with the browser-facing Todo List application.

Add a `todolist-nuxt` Deployment and `LoadBalancer` Service. Use the
`ghcr.io/<you>/todolist-nuxt:1.0` image (your GitHub user, as in
[4.1](../4.1-api/README.md)), expose Service port `80`, and
target the container's port `3000`. Build and push that image yourself from the
[provided Nuxt source](../../src/todolist-nuxt/README.md), which serves the UI on
port `3000`.

The `todolist-nuxt-config` ConfigMap is provided in [`cm.yaml`](cm.yaml) (`NUXT_API_BASE_URL` and
`NUXT_PUBLIC_USER`). Add your Deployment and Service to `kustomization.yaml`, and configure the web UI to:

- present the Todo List tasks and their status;
- send task create, update, and delete requests to `todolist-api`;
- read `NUXT_API_BASE_URL` from the ConfigMap as a container environment variable; and
- read `NUXT_PUBLIC_USER` from the ConfigMap as a container environment variable for the
  personalization stage.

The web UI is rendered on the server: its Pod, not the browser, calls the API. That
is why `NUXT_API_BASE_URL` is the API Service's DNS name, `http://todolist-api:8080`,
which works in any cluster.

Keep the API and data-layer resources included so the complete application can
be deployed with:

```bash
kubectl apply -k .
```
