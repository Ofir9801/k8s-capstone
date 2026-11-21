# Stage 5.1: HTTPS

Build on the [Gateway API overlay](../5.0-gateway-api/README.md) and serve
the application over HTTPS. The main path continues from 5.0 with
6.0-hpa, so this stage is a side branch. In the final
project, HTTPS becomes a chart option; its status is set in Week 8.

- Create a self-signed certificate for your host name, `todolist.<name-or-github-id>.local`
  (the same name the Gateway listens on: the certificate's CN and subjectAltName must match it) (with `openssl`, or with
  `openssl` in the course [toolbox image](../../../toolbox/README.md)) and store it in a
  `kubernetes.io/tls` Secret in the `todolist` namespace with `kubectl create secret tls`.
  Don't commit the key.
- Add an `https` listener on port 443 to the Gateway that terminates TLS with that Secret.
- Serve `/` (web UI) and `/api/v1` (API) on the `https` listener only.
- On the `http` listener, redirect every request to HTTPS (`RequestRedirect` filter, 301).

Check it with `curl -i http://todolist.<name>.local/` (a 301 to HTTPS),
`curl -k https://todolist.<name>.local/` and
`curl --cacert tls.crt https://todolist.<name>.local/api/v1/todos`.

Make this stage deployable with:

```bash
kubectl apply -k .
```
