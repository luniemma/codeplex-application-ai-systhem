# codeplex-ai (Helm chart)

Helm chart for [Codeplex AI](../../README.md) — a Flask service fronting OpenAI / Anthropic / Google Gemini.

This chart deploys the **app** (and optionally a small bundled Redis). It does **not** deploy Prometheus or Grafana itself; instead it integrates with [kube-prometheus-stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack) by emitting:

- a **ServiceMonitor** so the Prometheus Operator scrapes `/metrics` automatically,
- a **Grafana dashboard ConfigMap** with the standard `grafana_dashboard: "1"` label so the kube-prometheus-stack Grafana sidecar auto-imports it.

If you don't run kube-prometheus-stack, the [raw `k8s/` manifests](../../k8s/README.md) include a self-contained Prometheus + Grafana stack instead.

## TL;DR

```bash
# 1. Install kube-prometheus-stack (if you don't already run it)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace

# 2. Install Codeplex AI with metrics + dashboard wired in
helm install codeplex-ai ./helm/codeplex-ai \
  --namespace codeplex-ai --create-namespace \
  --set secrets.values.GOOGLE_API_KEY=AIza... \
  --set serviceMonitor.enabled=true \
  --set serviceMonitor.labels.release=monitoring \
  --set grafanaDashboard.enabled=true
```

The `serviceMonitor.labels.release=monitoring` makes the ServiceMonitor match kube-prometheus-stack's default `serviceMonitorSelector`. Adjust if your release name differs.

## Configuration

The full set of values is documented in [values.yaml](values.yaml). Highlights:

| Key                                | Default                    | Notes                                                                              |
| ---------------------------------- | -------------------------- | ---------------------------------------------------------------------------------- |
| `image.repository`                 | `luniemma/codeplex-ai`     | Set to your registry path if using GHCR or a private registry                      |
| `image.tag`                        | `""` (chart `appVersion`)  |                                                                                    |
| `replicaCount`                     | `2`                        | Ignored when `autoscaling.enabled = true`                                          |
| `autoscaling.enabled`              | `true`                     | HPA on CPU 70% / memory 80%, 2–10 replicas                                         |
| `secrets.create`                   | `true`                     | If false, set `secrets.existingSecret` to the name of an externally-managed Secret |
| `secrets.values.*`                 | empty                      | OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY, SECRET_KEY, JWT_SECRET           |
| `redis.enabled`                    | `true`                     | Bundled single-replica Redis. Disable to BYO Redis (set `config.REDIS_URL`)        |
| `serviceMonitor.enabled`           | `false`                    | Requires the prometheus-operator ServiceMonitor CRD                                |
| `serviceMonitor.labels.release`    | unset                      | kube-prometheus-stack matches ServiceMonitors with `release=<install-name>`        |
| `grafanaDashboard.enabled`         | `false`                    | Emits a `grafana_dashboard: "1"` ConfigMap for the Grafana sidecar                 |
| `ingress.enabled`                  | `false`                    | Set hosts + className for your cluster                                             |
| `podDisruptionBudget.enabled`      | `true`                     | minAvailable: 1                                                                    |

### Managing secrets out-of-band

Plaintext keys in `values.yaml` are convenient for local installs but a bad idea in CI. Recommended:

```bash
# Create the Secret yourself (from .env, sops, External Secrets, Sealed Secrets, …)
kubectl -n codeplex-ai create secret generic codeplex-ai-keys \
  --from-env-file=.env

# Tell the chart to use it
helm install codeplex-ai ./helm/codeplex-ai \
  --set secrets.create=false \
  --set secrets.existingSecret=codeplex-ai-keys
```

## Validating before deploy

```bash
helm lint ./helm/codeplex-ai
helm template ./helm/codeplex-ai --debug | kubectl apply --dry-run=client -f -
```

## Uninstall

```bash
helm uninstall codeplex-ai -n codeplex-ai
```
