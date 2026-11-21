# Stage 4.0: Data Layer

This first stage creates the persistent MariaDB foundation for the todolist
application. It includes the shared `todolist` namespace from `base/`.

## Included Resources

| Resource | Purpose |
| --- | --- |
| `todolist-config` ConfigMap | Database name, table name, host, and user settings. |
| `todolist-secret` Secret | MariaDB root password. |
| `mariadb-initdb` ConfigMap | Initializes the `todos` table when the database is first created. |
| `mariadb` StatefulSet | Runs one MariaDB pod with a 1 Gi persistent volume claim. |
| `backend` headless Service | Provides stable in-cluster DNS for MariaDB. |

Scheduled backups are added later, in the 8.1 backup layer.

MariaDB is available only inside the cluster at the `backend` hostname on port
3306. The StatefulSet stores its data in a `mariadb-data` volume claim.

## Deploy

```bash
kubectl apply -k .
```

## Verify the Data Layer

There is no API or UI yet, so three one-off Jobs (Session 2) check the
database directly. Each one runs the `mariadb` client against the `backend`
Service, reading the password from `todolist-secret` and the database and table
names from `todolist-config`.

| File | What the Job does |
| --- | --- |
| `test-db-validate-and-populate-job.yaml` | Fails if the `todos` table is missing, otherwise inserts three sample tasks. |
| `test-db-retrieve-job.yaml` | Prints every row of the `todos` table. |
| `test-db-cleanup-job.yaml` | Deletes every row, leaving an empty table. |

They are not listed in `kustomization.yaml`, so `kubectl apply -k .` does not
run them. Each uses `metadata.generateName`, so it gets a new name every
time it runs. Because of that, start them with `kubectl create`, not
`kubectl apply`:

```bash
kubectl create -f test-db-validate-and-populate-job.yaml
kubectl create -f test-db-retrieve-job.yaml
kubectl get jobs -n todolist                  # wait for COMPLETIONS 1/1
kubectl logs -n todolist job/<test-db-retrieve-xxxxx>   # the rows
```

To see that the data is persistent, delete the MariaDB Pod with
`kubectl delete pod mariadb-0 -n todolist`. Wait for the StatefulSet to
recreate it, then run the retrieve Job again: the rows are still there. Use
the cleanup Job to start over, and remove finished Jobs with
`kubectl delete jobs -n todolist -l app=todolist,tier=test`.

The test Pods are labelled `tier: test`, not `tier: backend`: the headless
`backend` Service selects `tier: backend`, so with that label it would also
resolve to the test Pods, which do not run a database.

The next stage, [4.1 API layer](../4.1-api/README.md), adds the service
that uses this database.
