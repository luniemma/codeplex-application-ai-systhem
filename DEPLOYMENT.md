# Codeplex AI - Deployment Guide

## How this project actually deploys

The generic Docker-Compose / cloud sections below are reference material. The real deploy targets a single shared EKS cluster (`codeplex-eks`) with four namespaces (dev / qa / staging / prod). Two pipelines drive the same Helm chart against that cluster — pick one per release, don't run both at once.

### Path A — Helm pipeline (`deploy.yml`)

The original CI deploy. `git push origin master` builds + scans + publishes a Docker image (`docker.yml`), then a `workflow_run` trigger fires `deploy.yml` → `deploy-eks.yml` which:

1. Assumes the `AWS_DEPLOY_ROLE_ARN` IAM role via OIDC.
2. `aws eks update-kubeconfig` for `codeplex-eks`.
3. **Recover from stuck Helm release** — if the previous release is `pending-*`, `failed`, or the release record is gone but k8s resources tagged `app.kubernetes.io/instance=codeplex-ai` remain, label-sweep + uninstall before retry.
4. `helm upgrade --install` with `--wait --timeout 10m`, passing `--set image.tag=sha-<short>`. **Note:** `--atomic` is intentionally NOT set — a failed install now leaves a `failed` release record + resources in place so the next-step "Diagnose helm failure" can dump describe / logs / events. The recovery step on the next run cleans the failed state.
5. Apply `k8s/monitoring/` (Prometheus + Grafana + shared Ingress with per-namespace host).
6. `kubectl rollout status` + in-cluster HTTP smoke test against app / prom / grafana.
7. Print public URLs (or `kubectl port-forward` commands if no NLB is provisioned).

Promotion shape:
- master push → auto-deploy to dev.
- release/* push → auto-deploy to staging.
- qa / prod → `workflow_dispatch` with GitHub Environment reviewers + soft policy (qa only from master, prod only from release/*).

### Path B — Argo CD GitOps (`deploy-argocd.yml` + `argocd/`)

A `workflow_dispatch` pipeline that takes the cluster from "no GitOps" to "Argo CD installed + four Applications under management" in one run:

1. AWS OIDC + kubeconfig same as Path A.
2. Kustomize-build `argocd/install/` (upstream `argo-cd v2.13.1` install.yaml + `argocd-cmd-params-cm` patched for `server.insecure: true` + nginx Ingress on `argocd.codeplex.local`).
3. `kubectl rollout status` on every argocd workload (server, repo-server, applicationset-controller, redis, dex, notifications, application-controller).
4. **Optional** `migrate_helm_releases: true` input — `helm uninstall codeplex-ai` in each codeplex-* namespace so Argo CD can take over cleanly without colliding on `meta.helm.sh/release-name` field ownership. Only flip on first bootstrap.
5. Kustomize-build `argocd/bootstrap/` — applies AppProject `codeplex` + 4 Applications.
6. Smoke test `/healthz` on argocd-server.
7. Print initial admin password retrieval command + port-forward command (no plaintext password in CI logs).

Sync policy in `argocd/bootstrap/applications.yaml`:
- **dev** — `automated.prune + automated.selfHeal`; reconciles continuously against `master`.
- **qa / staging / prod** — manual sync only. `targetRevision: master` is the safe default; retarget staging/prod to `release/N` branches when you adopt the release-branch flow, paired with Argo CD RBAC so only release managers can edit those fields.

The AppProject `codeplex` whitelists the single source repo and the four destination namespaces. At cluster scope only `Namespace` is allowed (needed for `CreateNamespace=true`); anything else (ClusterRole, CRD) is rejected.

### Picking between A and B

| | Path A — Helm CI | Path B — Argo CD |
|---|---|---|
| Trigger | `git push` (auto for dev/staging) | Argo controller polls master every ~3min; manual sync for non-dev |
| Image tag strategy | Per-commit `sha-<short>` injected via `--set` | Chart default `latest` (or pin per env later) |
| Rollback | `helm rollback codeplex-ai N` | Argo UI → History → Rollback |
| Drift detection | None — last apply wins | Continuous reconciliation; `selfHeal` reverts drift on dev |
| Reviewer gating | GitHub Environments | Argo CD RBAC |
| When to use | Per-PR deploys with full CI integration | Long-running release with continuous reconciliation |

### Prerequisites for either path

- `AWS_DEPLOY_ROLE_ARN` repo secret — provisioned by the `aws-terraform-infra` repo.
- `codeplex-ai-real-secrets` Secret in each codeplex-* namespace (provider keys + `SECRET_KEY` + `JWT_SECRET`). Bootstrap once per namespace:
  ```bash
  kubectl -n codeplex-<env> create secret generic codeplex-ai-real-secrets \
    --from-literal=OPENAI_API_KEY=sk-... \
    --from-literal=ANTHROPIC_API_KEY=sk-ant-... \
    --from-literal=GOOGLE_API_KEY=AIza... \
    --from-literal=SECRET_KEY="$(openssl rand -hex 32)" \
    --from-literal=JWT_SECRET="$(openssl rand -hex 32)"
  ```
- The Docker workflow must have published the image being requested. The chart's default `image.repository: luniemma/codeplex.ai` and `image.tag: latest` match what `build-docker.yml` publishes; deploy.yml additionally pins to `sha-<short>` per release. `1.0.0` (Chart.AppVersion) is NOT a published tag — chart defaults were fixed to avoid the resulting `ImagePullBackOff`.

### Browsing the running app

When the cluster has an external NLB, browse `http://codeplex-<env>.codeplex.local/` (add the NLB hostname to your hosts file). When AWS hasn't provisioned the LB (current state), port-forward:

```bash
aws eks update-kubeconfig --region us-east-1 --name codeplex-eks
kubectl -n codeplex-dev port-forward svc/codeplex-ai 8000:8000
# browse http://localhost:8000
```

For Argo CD's own UI:

```bash
kubectl -n argocd port-forward svc/argocd-server 8080:80
# browse http://localhost:8080 — username admin, retrieve password:
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath='{.data.password}' | base64 --decode; echo
```

---

## Pre-Deployment Checklist

- [ ] All dependencies listed in `requirements.txt`
- [ ] Environment variables configured in `.env`
- [ ] API keys obtained for all AI providers
- [ ] Database configured and tested
- [ ] Redis cache configured
- [ ] SSL certificates obtained
- [ ] Secrets managed securely
- [ ] Tests passing locally
- [ ] Security scan completed
- [ ] Performance testing completed

## Deployment Strategies

### 1. Docker Compose (Recommended for Development/Small Deployments)

Prerequisites:
- Docker and Docker Compose installed
- `.env` file configured

Steps:
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 2. Kubernetes (Production)

Prerequisites:
- Kubernetes cluster
- kubectl configured
- Docker image pushed to registry

Create deployment manifests:

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codeplex-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: codeplex-api
  template:
    metadata:
      labels:
        app: codeplex-api
    spec:
      containers:
      - name: codeplex-api
        image: your-registry/codeplex-ai:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: API_WORKERS
          value: "4"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

Deploy:
```bash
kubectl apply -f deployment.yaml
```

### 3. Cloud Platforms

#### AWS (ECS/Fargate)

1. Create ECR repository
2. Build and push Docker image
3. Create ECS task definition
4. Create ECS service
5. Configure load balancer
6. Set up RDS for PostgreSQL
7. Set up ElastiCache for Redis

#### Azure (Container Apps/AKS)

1. Create container registry
2. Push Docker image
3. Create Container App or AKS cluster
4. Configure environment variables
5. Set up managed databases
6. Configure networking and SSL

#### Google Cloud (Cloud Run/GKE)

1. Push image to Container Registry
2. Deploy to Cloud Run or GKE
3. Configure Cloud SQL for PostgreSQL
4. Configure Memorystore for Redis
5. Set up Cloud Load Balancing

## Environment Configuration

### Production .env Example

```env
APP_NAME=Codeplex AI
ENVIRONMENT=production
DEBUG=False

API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=8

OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

DATABASE_URL=postgresql://user:pass@db-server:5432/codeplex_ai
REDIS_URL=redis://redis-server:6379/0

LOG_LEVEL=INFO
SECRET_KEY=generated-secret-key-change-in-production
JWT_SECRET=generated-jwt-secret-change-in-production

ENABLE_CACHING=True
ENABLE_RATE_LIMITING=True
MAX_REQUEST_SIZE=10485760
REQUEST_TIMEOUT=30
```

## SSL/TLS Configuration

### Self-Signed Certificate (Development)

```bash
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

### Let's Encrypt (Production)

With Nginx:
```bash
apt-get install certbot python3-certbot-nginx
certbot certonly --nginx -d yourdomain.com
```

With Docker:
```bash
docker run -it --rm --name certbot \
  -v /path/to/cert:/etc/letsencrypt \
  certbot/certbot certonly --standalone -d yourdomain.com
```

## Database Setup

### PostgreSQL

```sql
CREATE DATABASE codeplex_ai;
CREATE USER codeplex WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE codeplex_ai TO codeplex;
```

### Migrations

```bash
# Create migration
alembic upgrade head
```

## Monitoring and Logging

### Logging

Configure centralized logging:

```python
import logging
from pythonjsonlogger import jsonlogger

# JSON logging for production
handler = logging.FileHandler('logs/codeplex.log')
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)
```

### Monitoring Services

Recommended:
- Prometheus for metrics
- Grafana for visualization
- ELK Stack for logging
- Sentry for error tracking

### Health Checks

Service includes built-in health check:
```bash
GET /health
```

Monitoring should periodically check this endpoint.

## Performance Optimization

1. **Enable Caching:**
   - Redis for distributed caching
   - In-memory cache for fallback

2. **Database Optimization:**
   - Add indexes on frequently queried columns
   - Use connection pooling
   - Configure query timeouts

3. **Load Balancing:**
   - Use Nginx or AWS ELB
   - Configure sticky sessions if needed
   - Use multiple worker processes

4. **Rate Limiting:**
   - Implement token bucket algorithm
   - Configure limits per endpoint

## Security Hardening

### Critical Security Measures

1. **Environment Secrets:**
   - Use environment variables for all secrets
   - Rotate API keys regularly
   - Use secret management services

2. **Network Security:**
   - Implement TLS/SSL
   - Use firewalls
   - Restrict API access if needed

3. **CORS Configuration:**
   - Whitelist trusted origins
   - Disable in production if not needed

4. **Input Validation:**
   - Validate and sanitize all inputs
   - Set size limits on uploads
   - Use parameterized queries

5. **SQL Injection Prevention:**
   - Always use ORM
   - Never concatenate SQL queries
   - Use parameterized statements

6. **Rate Limiting:**
   - Implement per-IP limits
   - Implement per-user limits

## Backup and Disaster Recovery

### Database Backups

PostgreSQL:
```bash
# Full backup
pg_dump -U codeplex codeplex_ai > backup.sql

# Restore
psql -U codeplex codeplex_ai < backup.sql
```

### Automated Backups

Set up cron jobs or cloud backup services:
```bash
0 2 * * * /usr/bin/pg_dump -U codeplex codeplex_ai | gzip > /backups/$(date +\%Y\%m\%d).sql.gz
```

## Scaling Considerations

### Horizontal Scaling

1. Use Docker containers
2. Implement load balancing
3. Use managed databases
4. Implement distributed caching

### Vertical Scaling

1. Increase worker processes
2. Add more RAM
3. Increase CPU allocation

## Deployment Checklist

Before going live:

- [ ] All tests passing
- [ ] Performance benchmarks met
- [ ] Security scan passed
- [ ] Load testing completed
- [ ] Backup strategy in place
- [ ] Monitoring configured
- [ ] Logging configured
- [ ] SSL/TLS enabled
- [ ] Database backups automated
- [ ] Incident response plan ready
- [ ] Team trained on deployment
- [ ] Rollback plan documented
- [ ] Change log updated

## Post-Deployment

1. Monitor application metrics
2. Check error rates and logs
3. Verify backup processes
4. Test incident response procedures
5. Gather performance data
6. Plan for ongoing maintenance

## Troubleshooting

### High Memory Usage

```bash
# Check memory usage
docker stats codeplex-api

# Reduce workers if needed
API_WORKERS=2
```

### Database Connection Issues

```bash
# Check connection pool
SQLALCHEMY_POOL_SIZE=10
SQLALCHEMY_POOL_RECYCLE=3600
```

### Slow API Responses

1. Check database query performance
2. Enable caching
3. Check API key rate limits
4. Increase worker count

## Support and Maintenance

- Regular security updates
- Dependency updates
- Performance monitoring
- Capacity planning
- Team training

