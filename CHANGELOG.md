# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project does not yet follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html) — `master` is the only release track.

## [Unreleased]

### Added — 2026-05 (GitOps + UI expansion)
- **Argo CD GitOps pipeline** (`argocd/` + `.github/workflows/deploy-argocd.yml`). One workflow_dispatch run takes the cluster from "no GitOps" to "Argo CD installed in `argocd` namespace with four Applications under management" — one per env (dev / qa / staging / prod) pointing at `helm/codeplex-ai` with the matching `helm/envs/<env>.yaml` overlay. Sync policy mirrors the existing promotion shape: dev auto-syncs from master; qa/staging/prod sync manually via the Argo UI or CLI. Pinned to Argo CD v2.13.1; bump via the workflow's `argocd_version` input.
- **AppProject `codeplex`** restricting Applications to the single source repo, the four destination namespaces, and (cluster-scoped) only the `Namespace` kind. Everything else at cluster scope is rejected by the project allowlist.
- **Three new info pages** in the Flask app: `/docs` (multi-language curl/Python/JS quick-start per endpoint, with per-block language tabs and copy buttons), `/faq` (12 collapsible Q&A items — auth, rate limits, streaming, caching, deploy, cost, SDK, licensing), `/compare` (side-by-side OpenAI / Anthropic / Google capability + pricing table, plus four "picking a default" recommendation cards).
- **Three new homepage sections**: "By the numbers" stat counters (six gradient cards), "Quick start" with curl/Python/JS code-sample tabs and per-snippet copy buttons, and "What people are saying" testimonials grid.
- **Nav extended** to nine items on both the homepage shell (`app/web.py`) and the info-page shell (`app/pages.py`): Playground · Docs · Compare · FAQ · About · Stories · Roadmap · Architecture · Status. Wraps cleanly on narrow viewports.

### Changed — 2026-05
- **`helm/codeplex-ai/values.yaml` image defaults** — repository was `luniemma/codeplex-ai` (dash), now `luniemma/codeplex.ai` (period) to match what `build-docker.yml` actually publishes via `dockerhub_image`. Tag default flipped from `""` (which fell back to `Chart.AppVersion = "1.0.0"`, never published) to `"latest"`. Argo CD uses chart defaults verbatim — the previous defaults caused `ImagePullBackOff` for every Argo-managed pod. The helm-path `deploy.yml` workflow already overrode both via `--set`, so its behaviour is unchanged.
- **`helm/envs/prod.yaml`** — `serviceMonitor.enabled` and `grafanaDashboard.enabled` flipped from `true` to `false`. Both depend on kube-prometheus-stack CRDs (ServiceMonitor + the `grafana_dashboard=1` ConfigMap-sidecar) which the platform-layer `k8s/monitoring/` overlay doesn't install. Static-config Prometheus already scrapes prod pods via the chart's `prometheus.io/scrape` annotations. Re-enable once kube-prometheus-stack lands on the platform layer (existing roadmap item).
- **`.github/workflows/deploy-eks.yml`** — dropped `--atomic` from the `helm upgrade --install` command. `--atomic` on a failed first install ran `helm uninstall` to roll back, which wrapped the real install error in an opaque "uninstalling the release" message and wiped resources before `kubectl describe` could see them. Without `--atomic`, failed installs leave a `failed` release record and the resources in place. The recovery step on the next run catches that; a new "Diagnose helm failure" step dumps describe/logs/events on failure so the CI log itself shows what went wrong.
- **Stuck-release recovery** extended to handle `failed` state (in addition to `pending-*`) and to label-sweep orphan resources matching `app.kubernetes.io/instance=<release>` when the release record is gone but k8s resources remain (the "atomic rollback partially failed" case).
- **AppProject `codeplex`** initial `clusterResourceWhitelist: []` was too tight — Applications with `syncOptions: CreateNamespace=true` need to create the destination namespace at PreSync, and `Namespace` is cluster-scoped. Now explicitly allows `""/Namespace` and only that kind.

### Fixed — 2026-05
- **Ruff RUF001 ambiguous Unicode** in `app/pages.py`: `−` (U+2212 MINUS SIGN) in the `/faq` toggle CSS replaced with the CSS unicode escape `\002212` (renders the same minus sign without ambiguous source). `×` (U+00D7 MULTIPLICATION SIGN) in "20× cheaper" on `/compare` replaced with conventional `x`. Other non-ASCII glyphs (em-dash, arrows, box drawing) are unchanged — they're not confusable with ASCII.

### Removed
- `.github/workflows/generator-generic-ossf-slsa3-publish.yml` — the standalone SLSA generic-generator workflow GitHub scaffolded via the UI. It was failing with `Input required and not supplied: path` and was redundant with the OCI-native SLSA provenance our Docker workflow already emits via `docker/build-push-action@v6` (`provenance: true`, `sbom: true`). The generic generator is for binary releases (Go, JARs); for container images, OCI-native attestations attached to the manifest are the recommended pattern.

### Added
- **Multi-arch Docker images** (linux/amd64 + linux/arm64) for ARM Macs and AWS Graviton.
- **Sigstore keyless signing** of every published image — verify identity with `cosign verify`.
- **Trivy CVE scanning** in the build pipeline; CRITICAL CVEs fail the build, results upload to GitHub Code Scanning.
- **CodeQL** static analysis with the `security-extended` query pack.
- **Dependabot** configuration for pip, github-actions, and docker ecosystems (weekly cadence, grouped security updates).
- **Rate limiting** via Flask-Limiter — 200/min global default, 30/min on `/api/*`. Redis backend when reachable, in-memory fallback otherwise.
- **Security headers** middleware — CSP, HSTS (HTTPS only), X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, Cross-Origin-{Opener,Resource}-Policy.
- **CORS lockdown** — wildcard only in development; production with no `CORS_ORIGINS` refuses all cross-origin requests and logs a warning.
- **`/livez` and `/readyz`** endpoints (Kubernetes convention). `/health` retained as alias of `/livez` for backward compatibility.
- **Retry policy** for upstream provider calls — up to 3 attempts with exponential backoff on transient errors (timeouts, 5xx, 429); permanent errors propagate immediately.
- **Structured logging** — request IDs (returned in `X-Request-ID` header), per-request access logs, provider-call timing logs, startup banner with config summary, optional JSON output (`LOG_FORMAT=json`).
- **Reusable Docker workflow** (`build-docker.yml`) — build → smoke test → CVE scan → multi-arch publish → cosign sign.
- **Dual-registry publish** — every master push lands at `ghcr.io/luniemma/codeplex-application-ai-systhem` and `luniemma/codeplex.ai`.
- **Cosign verification command** in workflow summary so consumers know how to verify image signatures.
- **Ruff** linter + formatter, **pre-commit** hooks (trailing whitespace, gitleaks, large-file blocker), `pyproject.toml` for tool config.
- **Architecture diagrams** (Mermaid) in `ARCHITECTURE.md` covering system context, components, request lifecycle, class hierarchy, deployment topology.
- **Web playground** at `/` with markdown rendering of model output, provider status pills, and three interactive tabs (Chat / Analyze / Generate).
- **`SECURITY.md`** disclosure policy.
- `LICENSE` (MIT) — making the README's claim official.

### Changed
- **`requirements.txt` trimmed** from 26 packages to 13 — removed `tensorflow`, `torch`, `transformers`, `numpy`, `pandas`, `scikit-learn`, `langchain`, `psycopg2`, `alembic`, `uvicorn`, `python-multipart`, and others that were never imported by the code. Resolved an irreconcilable `tensorflow`/`pydantic`/`typing-extensions` version conflict.
- **Dockerfile**: gunicorn now invokes `main:create_app()` (factory pattern) instead of the broken `main:app`. The `.local` install path is in `/home/codeplex/.local` instead of `/root/.local`, fixing a permission-denied crash on container startup. `FROM ... AS builder` capitalised to silence buildkit lint.
- **Routes**: every POST endpoint now uses `request.get_json(silent=True)` so malformed JSON returns a clean 400 instead of bubbling a 500. `/health` returns the standard envelope `{ data: { status: ... } }` for shape consistency with every other endpoint.
- **Error responses**: 500 handlers now include the upstream exception message (`f"Chat failed: {e}"`) instead of swallowing it; rate-limit, deprecated-model, and auth errors are now actionable from the client side.
- **Provider key check**: any value starting with `your_` (the placeholder pattern from `.env.example`) is treated as "not configured" and rejected with a clear error before any upstream call.
- **README**: rewritten with accurate endpoint paths, full request/response examples, troubleshooting matrix, configuration table, project layout, and honest "Known limitations" section.
- **`gemini-pro` → `gemini-2.5-flash`** documented as the recommended Google model since the original was deprecated by Google in 2025.
- Workflow runners forced to **Node.js 24** (`FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true`) ahead of GitHub's 2026-09-16 Node 20 removal.
- SLSA generic generator workflow bumped from `v1.4.0` → `v2.1.0` (v1.4.0 used the deprecated `actions/upload-artifact@v3`).

### Fixed
- Dockerfile container would fail to start with `AttributeError: module 'main' has no attribute 'app'` (gunicorn invocation bug).
- Dockerfile container would fail to start with `Permission denied: /root/.local/bin/gunicorn` after switching to non-root user.
- Removed broken `asyncio==3.4.3` from requirements (a stdlib backport that breaks on modern Python).
- `GoogleProvider.analyze_code` and `generate_code` referenced `genai` which was only in scope inside `__init__` — would `NameError` at runtime. Now uses `self.client.types.GenerationConfig`.
- Test `test_invalid_json` returned 500 instead of 400/422 because `request.json` raises on malformed bodies and was caught by the generic 500 handler.
- Test `test_health_check` expected `data.status` but `/health` returned a bare `{status: ...}` outside the standard envelope.

### Security
- Container images now pass a `CRITICAL`-severity Trivy scan before publish.
- Secrets cannot be committed via gitleaks pre-commit hook (manual override requires explicit allowlisting).
- Removed default wildcard CORS in production deployments — operators must opt in to specific origins.
