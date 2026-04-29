# Security policy

## Reporting a vulnerability

**Do not** open a public GitHub issue for security vulnerabilities.

If you believe you've found a security issue in Codeplex AI:

1. Use GitHub's [private vulnerability reporting](https://github.com/luniemma/codeplex-application-ai-systhem/security/advisories/new) (preferred — keeps the discussion private until a fix lands).
2. Or email **luniyisiemmanuel@gmail.com** with subject `SECURITY: <short title>`.

Include enough detail to reproduce: affected version (commit SHA or tag), endpoint, payload, and observed vs. expected behavior. A working PoC is welcome but not required.

We aim to acknowledge reports within **72 hours** and ship a fix within **30 days** for High/Critical issues.

## Scope

| In scope | Out of scope |
|---|---|
| `app/` and `main.py` (the running service) | Forks of this repo |
| Dockerfile + the published images on GHCR / Docker Hub | Code in `tests/` (test-only fixtures) |
| GitHub Actions workflows (CI supply-chain) | Third-party AI provider SDKs (report upstream) |
| Default config in `.env.example` | Self-hosted deployments with custom config |

## Supported versions

We track only `master`. There are no LTS branches; please re-base or upgrade to the latest published image.

## What we ship

Every published image at `ghcr.io/luniemma/codeplex-application-ai-systhem` and `luniemma/codeplex.ai`:

- Is built reproducibly from a tagged commit ([build-docker.yml](.github/workflows/build-docker.yml))
- Is **scanned by Trivy** before publish — any `CRITICAL` CVE fails the build
- Is **signed with Sigstore (cosign)** keylessly — verify with:

    ```bash
    cosign verify ghcr.io/luniemma/codeplex-application-ai-systhem:latest \
      --certificate-identity-regexp 'https://github.com/luniemma/codeplex-application-ai-systhem' \
      --certificate-oidc-issuer https://token.actions.githubusercontent.com
    ```

- Ships with **SLSA provenance** and **SPDX SBOM** as OCI artifacts; inspect with:

    ```bash
    docker buildx imagetools inspect ghcr.io/luniemma/codeplex-application-ai-systhem:latest
    ```

## Hardening already in place

These are baseline expectations; if any are missing in a deployment, treat as a bug:

- **Non-root container** — runs as UID 1000 (`codeplex`); no `--privileged` required
- **Multi-stage build** — runtime image has no compilers or build tools
- **Pinned Python dependencies** in `requirements.txt`; Dependabot opens weekly update PRs
- **Static analysis** — CodeQL (`security-extended` queries) on every push
- **Rate limiting** — Flask-Limiter, default 200/min/IP, 30/min/IP for `/api/*`
- **Security headers** — CSP, HSTS (HTTPS only), X-Frame-Options, Referrer-Policy, Permissions-Policy
- **CORS** — wildcard only allowed in development; production refuses all cross-origin by default
- **Secret detection** — gitleaks runs as a pre-commit hook
- **Placeholder key rejection** — `your_*_key_here` values fail loudly rather than reaching upstream APIs

## What we don't claim to handle

These would need additional configuration in your deployment:

- Authentication / authorization (the API is unauthenticated by default)
- DDoS at the network layer (rate limiting is per-IP, not absolute)
- Secret rotation (we recommend short-lived tokens via your secret store)
- Audit logging beyond access logs (no SIEM integration shipped)
- Encryption at rest for the cache or database

## Acknowledgements

Reporters who follow responsible disclosure will be credited in the [CHANGELOG](CHANGELOG.md) on the release that fixes their finding (unless they prefer to remain anonymous).
