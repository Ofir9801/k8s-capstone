# Stage 4.1: API layer

Add the manifests needed to deploy a `todolist-api` service alongside the
completed data layer.

Create a `todolist-api` Deployment and Service. Use the
`ghcr.io/<you>/todolist-api:1.0` image, where `<you>` is your GitHub user in lower
case, and expose its HTTP port `8080`. Build and push that image yourself from the
[provided Go/Fiber source](../../src/todolist-api/README.md), which listens on that
port and implements the required routes.

The Deployment should:

- connect to MariaDB through the `backend` Service in the `todolist` namespace;
- load `MYSQL_DB`, `MYSQL_HOST`, `MYSQL_USER`, and `MYSQL_TABLE` from
  `todolist-config`;
- load `MYSQL_PASSWORD` from `todolist-secret` key `MYSQL_ROOT_PASSWORD`;
- wait for the database and the `todos` table before the API starts (this part
  is provided, see below); and
- expose the API's `GET`/`POST /todos`, `GET`/`PUT`/`PATCH`/`DELETE /todos/:id`
  operations through a `LoadBalancer` Service on port `8080`; and
- reserve `GET /livez` and `GET /readyz` for the probes added in the
  reliability stage.

The source requires `MYSQL_DB`, `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`,
and `MYSQL_TABLE` at startup. `PORT` defaults to `8080`; `LOG_LEVEL` is
optional.

### Provided: wait-for-db init container

Waiting for MariaDB is not the focus of this stage, so it is provided:

- `wait-for-db.sh` is the script the init container runs;
- `wait-for-db-patch.yaml` adds a `wait-for-db` init container (and the volume
  holding the script) to your Deployment; and
- `kustomization.yaml` already turns the script into a ConfigMap
  (`configMapGenerator`) and applies the patch (`patches`).

Keep those entries in `kustomization.yaml` and name your Deployment
`todolist-api` in the `todolist` namespace, otherwise the patch has nothing to
attach to and `kubectl apply -k .` fails. Do not add an `initContainers`
section to your own Deployment.

Include the [data-layer overlay](../4.0-data/README.md) as a resource so that this stage can be deployed
with:

```bash
kubectl apply -k .
```
