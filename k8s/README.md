# Kubernetes manifests

Plain `kubectl apply -f k8s/` deploy of Codeplex AI plus a self-contained Prometheus + Grafana stack. No operators required, no Helm needed — just a working cluster (`kubectl get nodes` returns nodes).

## What's in here

```
k8s/
├── 00-namespace.yaml
├── 10-configmap.yaml              # non-secret env (model names, log format, Redis URL, …)
├── 11-secret.example.yaml         # template — copy to 11-secret.yaml and fill in real keys
├── 20-redis.yaml                  # Redis (cache + rate limiter backend)
├── 30-app-deployment.yaml         # Codeplex AI Deployment (+ ServiceAccount)
├── 31-app-service.yaml
├── 32-app-hpa.yaml                # CPU/memory-based autoscaling (2–10 replicas)
├── 33-app-pdb.yaml                # PodDisruptionBudget
├── 34-app-ingress.yaml            # Ingress template — edit host + class for your cluster
├── 40-prometheus-rbac.yaml        # ServiceAccount + Role for pod discovery
├── 41-prometheus-config.yaml
├── 42-prometheus.yaml             # Prometheus Deployment + Service
├── 50-grafana-secret.yaml         # admin login (default admin/admin — CHANGE IT)
├── 51-grafana-provisioning.yaml   # auto-provisioned datasource + dashboard provider
├── 52-grafana-dashboard.yaml      # Codeplex AI dashboard (request rate, latency, errors)
└── 53-grafana.yaml                # Grafana Deployment + Service
```

## Apply

```bash
# 1. Provide your API keys (at least one provider must be real)
cp k8s/11-secret.example.yaml k8s/11-secret.yaml
${EDITOR:-nano} k8s/11-secret.yaml

# 2. Apply everything — files are numbered so lexical ordering = correct apply order
kubectl apply -f k8s/

# 3. Watch the rollout
kubectl -n codeplex-ai rollout status deploy/codeplex-ai
kubectl -n codeplex-ai get pods
```

## Reach the services

The Service objects are all `ClusterIP`. For local poking, port-forward:

```bash
kubectl -n codeplex-ai port-forward svc/codeplex-ai 8000:8000   # web playground + API
kubectl -n codeplex-ai port-forward svc/prometheus  9090:9090   # Prometheus UI
kubectl -n codeplex-ai port-forward svc/grafana     3000:3000   # Grafana (admin/admin)
```

Then:

| URL                              | What                                                          |
| -------------------------------- | ------------------------------------------------------------- |
| http://localhost:8000/           | Codeplex AI web playground                                    |
| http://localhost:8000/metrics    | Prometheus metrics endpoint                                   |
| http://localhost:8000/readyz     | 200 if at least one provider key is configured, else 503      |
| http://localhost:9090/           | Prometheus UI — check Status → Targets to see scrape health    |
| http://localhost:3000/           | Grafana — Dashboards → Codeplex → "Codeplex AI"                |

For external access, edit `k8s/34-app-ingress.yaml` (set host + ingress class) and apply.

## How metrics flow

```
codeplex-ai pods (gunicorn, 2 replicas)
        │     ├── /metrics (prometheus-flask-exporter, multiproc-aware)
        │     └── annotations: prometheus.io/scrape=true, port=8000, path=/metrics
        ▼
prometheus  (kubernetes_sd_configs + relabeling — auto-discovers annotated pods)
        ▼
grafana     (datasource provisioned to http://prometheus:9090; dashboard auto-loaded)
```

The dashboard panels use `flask_http_request_total`, `flask_http_request_duration_seconds_bucket`, `process_resident_memory_bytes`, `process_cpu_seconds_total`, and `codeplex_ai_build_info` — all auto-emitted by `app/metrics.py`.

## Production gotchas

| What                                                                     | Recommendation                                                                                              |
| ------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| `emptyDir` on Prometheus and Grafana — data is lost on pod restart.      | Swap for a `PersistentVolumeClaim` once you settle on a storage class.                                      |
| `admin/admin` Grafana login.                                             | Replace `50-grafana-secret.yaml` with a strong random password before exposing.                              |
| Ingress is templated for nginx-ingress — edit the class for your cluster. | Set `ingressClassName` and the controller-specific annotations.                                              |
| SQLite on a per-pod `emptyDir`.                                          | The DB is currently unused (see README "Known limitations"). When you wire it up, switch to PostgreSQL.     |
| Redis runs as a single replica with no persistence.                      | Fine for a cache, but operators wanting durability should swap for a Redis StatefulSet or managed instance. |
| Prometheus scrapes only the `codeplex-ai` namespace.                     | Edit the Role + `namespaces.names` in `41-prometheus-config.yaml` if you want broader discovery.            |

## Removing everything

```bash
kubectl delete namespace codeplex-ai
```
