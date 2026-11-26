# Stage 5.1: HTTPS

Build on the [Gateway API overlay](../5.0-gateway-api/README.md) and serve
the application over HTTPS. The main path continues from 5.0 with
[6.0-hpa](../6.0-hpa/README.md), so this stage is a side branch. In the final
project, HTTPS becomes a chart option; its status is set in Week 8.

- Create a self-signed certificate for your host name, `todolist.<name-or-github-id>.local`
  (the same name the Gateway listens on: the certificate's CN and subjectAltName must match it) (with `openssl`, or with
  `openssl` in the course [toolbox image](../../../toolbox/README.md)) and store it in a
  `kubernetes.io/tls` Secret in the `todolist` namespace with `kubectl create secret tls`.
  Once you know the manual steps, the utility script does both:
  `./scripts/create-tls-secret -n todolist --name todolist-tls-secret --host todolist.<name>.local`.
  Don't commit the key.
- Add an `https` listener on port 443 to the Gateway that terminates TLS with that Secret.
- Serve **both** paths, `/` (web UI) and `/api/v1` (API), on the `https` listener only:
  no path may answer over plain HTTP.
- On the `http` listener, redirect every request to HTTPS (`RequestRedirect` filter, 301),
  for both paths.

Check both paths, over HTTP and HTTPS:

```bash
curl -i http://todolist.<name>.local/                  # 301, Location: https://todolist.<name>.local/
curl -i http://todolist.<name>.local/api/v1/todos      # 301 too, not the list of todos
curl -k https://todolist.<name>.local/                 # the web UI (-k: self-signed)
curl --cacert tls.crt https://todolist.<name>.local/api/v1/todos   # the API, trusting your certificate
```

If the second command returns todos instead of a 301, the API path is still attached to the
`http` listener: plain HTTP to `/api/v1` reaches the API and skips the redirect.

Make this stage deployable with:

```bash
kubectl apply -k .
```
