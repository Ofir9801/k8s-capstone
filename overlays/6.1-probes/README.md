# Stage 6.1: Health probes

Extend the [Horizontal Pod Autoscaler](../6.0-hpa/README.md) overlay with
runtime health checks for the Todo List API.

The `todolist-api` image exposes `/readyz` and
`/livez` on port `8080`. Add a readiness probe for `/readyz` with a 5-second
initial delay, 5-second period, 3-second timeout, and failure threshold of 3.
Add a liveness probe for `/livez` with a 15-second initial delay, 20-second
period, 2-second timeout, and failure threshold of 3.

The readiness endpoint verifies the MariaDB connection; liveness only verifies
that the API process is running. Retain the database-waiting initialization
behavior so the API does not start before MariaDB is available.

## MariaDB probes (no change to the image)

Add probes to the MariaDB StatefulSet as well, without building a new image. The official
`mariadb` image already contains a health-check script, `/usr/local/bin/healthcheck.sh`:
read its options in the
[MariaDB documentation](https://mariadb.com/docs/server/server-management/automated-mariadb-deployment-and-administration/docker-and-mariadb/using-healthcheck-sh)
or in the script itself (`kubectl -n todolist exec mariadb-0 -- cat /usr/local/bin/healthcheck.sh`).
Run it by hand first: `kubectl -n todolist exec mariadb-0 -- healthcheck.sh <tests>; echo $?`.

- It needs no password in your YAML: it uses the credentials of a dedicated healthcheck user
  in `/var/lib/mysql/.my-healthcheck.cnf`, which the image creates when it first initializes
  the database. So the probes can be plain `exec` probes in your overlay.
- Decide which of its tests suits a **startup**, a **readiness** and a **liveness** probe, and how
  patient each one should be. Remember what each probe makes Kubernetes do, and that the first
  start also runs the initialization SQL.
- If a test fails with an access error, your volume was initialized by an older image without
  the healthcheck user: set `MARIADB_AUTO_UPGRADE=1` on the container once, or start from a
  fresh PVC.
