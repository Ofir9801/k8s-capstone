# Stage 6.0: Horizontal Pod Autoscaler

Extend the [Gateway API layer](../5.0-gateway-api/README.md) with
CPU-based autoscaling for the Todo List API.

Add resource requests and limits for the API and web UI containers, then create
a `todolist-api-hpa` HorizontalPodAutoscaler. Configure it with a minimum of 2
replicas, a maximum of 8, and a 50% average CPU-utilization target. Configure
scale-up to allow a 100% increase every 15 seconds and scale-down to allow a
50% decrease every 15 seconds after a 60-second stabilization window.

This stage requires Metrics Server to provide resource metrics. Include the
Gateway API, web UI, API, and data layers so the autoscaled
application can be deployed with:

```bash
kubectl apply -k .
```

## Test the autoscaler

Needs Metrics Server (`minikube addons enable metrics-server`).

**1. Configuration** (about a minute after `kubectl apply -k`):

```bash
kubectl -n todolist get hpa todolist-api-hpa        # MINPODS 2, MAXPODS 8, TARGETS cpu: N%/50% (not <unknown>)
kubectl -n todolist describe hpa todolist-api-hpa   # Conditions: AbleToScale True, ScalingActive True
kubectl -n todolist get deployment todolist-api     # 2/2 while idle
```

If `ScalingActive` is `False`, its reason says why: `missing request for cpu` (no CPU request
on the API container), `failed to get cpu utilization` (Metrics Server missing or not ready
yet), or a target that can't be found (wrong `scaleTargetRef`).

**2. Behavior under load** (about five minutes). [`test-api-load-job.yaml`](test-api-load-job.yaml)
runs 4 Pods with 16 threads each that call `GET /todos` for three minutes. Like the 4.1 test
Jobs, it is not in `kustomization.yaml`; start it with `kubectl create`:

```bash
kubectl -n todolist get hpa todolist-api-hpa -w                 # second terminal: watch REPLICAS
kubectl create -f overlays/6.0-hpa/test-api-load-job.yaml
kubectl -n todolist describe hpa todolist-api-hpa               # Events: New size: ...; cpu ... above target
kubectl -n todolist logs -l app=todolist,tier=test --tail 1     # requests/s each load Pod reached
kubectl delete jobs -n todolist -l app=todolist,tier=test
```

Pass: REPLICAS rises above 2 within about two minutes, and drops back to 2 within about two
minutes after the Job ends (60-second window, then halving every 15 seconds). If it doesn't
scale out, the load is too light for your machine: raise `parallelism` or `THREADS` in the Job.
The final-project script (`scripts/test-final-project.sh`) repeats the configuration check on
your Helm release.
