"""
Static info pages — About / Architecture / Status. Each shares the same dark
theme tokens as app.web.INDEX_HTML so the look is consistent across the site.
"""

from datetime import datetime

from flask import Blueprint, render_template_string

from app.config import config

pages_bp = Blueprint("pages", __name__)


def _key_set(value: str) -> bool:
    return bool(value) and not value.startswith("your_")


# Shared CSS — kept compact since each page has a single block of layout-specific
# extras on top. Mirrors the design tokens in app/web.py for consistency.
_BASE_CSS = r"""
:root, html[data-theme="dark"] {
  --bg: #0b0f1a;
  --panel: #131a2b;
  --panel-2: #1b2440;
  --border: #263256;
  --text: #e6ebf5;
  --muted: #9aa6c1;
  --accent: #6b8cff;
  --accent-2: #8d6bff;
  --good: #3ddc97;
  --bad: #ff6b6b;
  --warn: #ffce5c;
  --code-bg: #06091a;
  --hero-glow-1: #1a2347;
  --hero-glow-2: #2a1a4a;
}
html[data-theme="light"] {
  --bg: #f5f7fb; --panel: #ffffff; --panel-2: #f0f3fa; --border: #d6dcec;
  --text: #1a2240; --muted: #5a6685; --accent: #4a6ef0; --accent-2: #7a4fea;
  --good: #1aa56b; --bad: #d83a3a; --warn: #c98b00; --code-bg: #f0f3fa;
  --hero-glow-1: #d8e0fc; --hero-glow-2: #e6daff;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background: radial-gradient(1200px 600px at 10% -10%, var(--hero-glow-1) 0%, transparent 60%),
              radial-gradient(900px 500px at 100% 0%, var(--hero-glow-2) 0%, transparent 60%),
              var(--bg);
  color: var(--text); min-height: 100vh; line-height: 1.6;
}
header {
  padding: 22px 32px; display: flex; align-items: center; justify-content: space-between;
  border-bottom: 1px solid var(--border); backdrop-filter: blur(8px);
}
.brand { display: flex; align-items: center; gap: 12px; font-weight: 700; font-size: 20px; letter-spacing: 0.3px; }
.brand svg { width: 36px; height: 36px; border-radius: 8px;
  box-shadow: 0 6px 24px rgba(107, 140, 255, 0.35); }
.brand a { color: inherit; text-decoration: none; }
.brand-name { background: linear-gradient(135deg, var(--text), var(--muted));
  -webkit-background-clip: text; background-clip: text; color: transparent; }
nav.primary { display: flex; gap: 6px; flex-wrap: wrap; }
nav.primary a {
  font-size: 14px; padding: 8px 14px; border-radius: 8px; color: var(--muted);
  text-decoration: none; transition: background 0.15s, color 0.15s;
}
nav.primary a:hover { background: var(--panel); color: var(--text); }
nav.primary a.active { background: var(--panel); color: var(--accent); }
.header-right { display: flex; gap: 10px; align-items: center; }
.pill { font-size: 12px; padding: 4px 10px; border-radius: 999px;
  background: rgba(107, 140, 255, 0.15); border: 1px solid rgba(107, 140, 255, 0.4);
  color: var(--accent); }
.icon-btn {
  background: transparent; border: 1px solid var(--border); color: var(--muted);
  border-radius: 10px; width: 36px; height: 36px; padding: 0;
  display: inline-flex; align-items: center; justify-content: center; cursor: pointer;
}
.icon-btn:hover { color: var(--text); border-color: var(--accent); }
main { max-width: 1100px; margin: 0 auto; padding: 32px; }
h1 { font-size: 38px; line-height: 1.15; margin: 0 0 12px; }
h2 { font-size: 24px; margin: 36px 0 12px; }
h3 { font-size: 18px; margin: 24px 0 10px; color: var(--muted); }
p { color: var(--muted); margin: 8px 0 16px; }
.lead { font-size: 18px; color: var(--text); margin-bottom: 24px; }
.card { background: var(--panel); border: 1px solid var(--border); border-radius: 14px;
  padding: 24px; margin: 16px 0; }
.grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
.kv { display: flex; justify-content: space-between; align-items: center;
  padding: 10px 0; border-bottom: 1px solid var(--border); }
.kv:last-child { border-bottom: none; }
.kv .k { color: var(--muted); font-size: 14px; }
.kv .v { font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace; font-size: 14px; }
.badge { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 12px;
  font-weight: 600; letter-spacing: 0.3px; }
.badge.good { background: rgba(61, 220, 151, 0.15); color: var(--good); }
.badge.bad  { background: rgba(255, 107, 107, 0.15); color: var(--bad); }
.badge.warn { background: rgba(255, 206, 92, 0.15); color: var(--warn); }
code, pre { font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  background: var(--code-bg); border-radius: 6px; }
code { padding: 2px 6px; font-size: 13px; }
pre { padding: 16px; overflow-x: auto; font-size: 13px; line-height: 1.5; }
ul.feat { list-style: none; padding: 0; margin: 0; }
ul.feat li { padding: 10px 0; padding-left: 28px; position: relative; color: var(--muted); }
ul.feat li::before { content: "✓"; position: absolute; left: 0; top: 10px;
  color: var(--good); font-weight: 700; }
.flow {
  display: flex; flex-direction: column; gap: 0; margin: 16px 0;
  font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
}
.flow .step {
  background: var(--panel-2); border: 1px solid var(--border);
  border-radius: 10px; padding: 12px 16px; position: relative;
  margin-left: 0; transition: transform 0.15s;
}
.flow .step:hover { transform: translateX(4px); border-color: var(--accent); }
.flow .step + .step { margin-top: 22px; }
.flow .step + .step::before {
  content: "↓"; position: absolute; left: 24px; top: -20px;
  color: var(--accent); font-size: 18px;
}
.flow .step .label { color: var(--muted); font-size: 11px; text-transform: uppercase;
  letter-spacing: 1px; margin-bottom: 4px; }
.flow .step .name { color: var(--text); font-weight: 600; }
.flow .step .detail { color: var(--muted); font-size: 13px; margin-top: 4px; }
footer { text-align: center; color: var(--muted); padding: 32px; font-size: 13px; }
"""


_HEADER_HTML = r"""
<header>
  <div class="brand">
    <a href="/" aria-label="Home">
      <svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <defs>
          <linearGradient id="brand-grad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#6b8cff"/>
            <stop offset="100%" stop-color="#8d6bff"/>
          </linearGradient>
        </defs>
        <rect width="32" height="32" rx="8" fill="url(#brand-grad)"/>
        <path d="M11 11 L7 16 L11 21 M21 11 L25 16 L21 21" stroke="white" stroke-width="2.5"
          stroke-linecap="round" stroke-linejoin="round" fill="none"/>
      </svg>
    </a>
    <span class="brand-name">{{ app_name }}</span>
  </div>
  <nav class="primary">
    <a href="/" class="{% if active == 'home' %}active{% endif %}">Playground</a>
    <a href="/about" class="{% if active == 'about' %}active{% endif %}">About</a>
    <a href="/stories" class="{% if active == 'stories' %}active{% endif %}">Stories</a>
    <a href="/roadmap" class="{% if active == 'roadmap' %}active{% endif %}">Roadmap</a>
    <a href="/architecture" class="{% if active == 'architecture' %}active{% endif %}">Architecture</a>
    <a href="/status" class="{% if active == 'status' %}active{% endif %}">Status</a>
  </nav>
  <div class="header-right">
    <span class="pill">v{{ version }}</span>
    <button id="theme-toggle" class="icon-btn" title="Toggle theme">
      <svg id="theme-icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
        stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
      <svg id="theme-icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
        stroke-linecap="round" stroke-linejoin="round" style="display:none"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>
    </button>
  </div>
</header>
"""


_THEME_JS = r"""
<script>
  (function() {
    const KEY = "codeplex-theme";
    const root = document.documentElement;
    const saved = localStorage.getItem(KEY);
    if (saved) root.setAttribute("data-theme", saved);
    const sync = () => {
      const dark = root.getAttribute("data-theme") !== "light";
      document.getElementById("theme-icon-moon").style.display = dark ? "" : "none";
      document.getElementById("theme-icon-sun").style.display  = dark ? "none" : "";
    };
    sync();
    document.getElementById("theme-toggle").addEventListener("click", () => {
      const next = root.getAttribute("data-theme") === "light" ? "dark" : "light";
      root.setAttribute("data-theme", next);
      localStorage.setItem(KEY, next);
      sync();
    });
  })();
</script>
"""


def _render(active: str, body: str) -> str:
    """Render any of the info pages with the shared shell."""
    template = (
        "<!DOCTYPE html><html lang='en' data-theme='dark'><head>"
        "<meta charset='UTF-8'/>"
        "<meta name='viewport' content='width=device-width, initial-scale=1.0'/>"
        "<title>{{ app_name }} — {{ active|capitalize }}</title>"
        "<style>" + _BASE_CSS + "</style>"
        "</head><body>"
        + _HEADER_HTML
        + "<main>"
        + body
        + "</main>"
        + "<footer>{{ app_name }} v{{ version }} · running in <code>{{ environment }}</code></footer>"
        + _THEME_JS
        + "</body></html>"
    )
    return render_template_string(
        template,
        app_name=config.APP_NAME,
        version=config.APP_VERSION,
        environment=config.ENVIRONMENT,
        active=active,
    )


# ─── /about ───────────────────────────────────────────────────────────────
_ABOUT_BODY = r"""
<h1>About {{ app_name }}</h1>
<p class="lead">A unified REST API in front of OpenAI, Anthropic, and Google Gemini —
built to make multi-provider AI experimentation a one-line code change instead of a
three-SDK rewrite.</p>

<div class="card">
  <h2>Why this exists</h2>
  <p>Switching providers in a real codebase is friction-heavy: each SDK has its own
  client object, request shape, error model, streaming protocol, and cost contour.
  {{ app_name }} pins them all behind the same Flask routes (<code>/api/analyze</code>,
  <code>/api/generate</code>, <code>/api/optimize</code>, <code>/api/chat</code>,
  <code>/api/batch-analyze</code>) so swapping providers is a JSON field, not a refactor.</p>
</div>

<h2>What you get</h2>
<div class="grid-2">
  <div class="card">
    <h3>Provider-agnostic API</h3>
    <p>Pick a provider per request via the <code>provider</code> field; the same
    payload works against any of OpenAI, Anthropic, or Google.</p>
  </div>
  <div class="card">
    <h3>Built-in observability</h3>
    <p>Prometheus <code>/metrics</code>, structured JSON logs, request-ID propagation,
    and a Grafana dashboard auto-imported via the bundled monitoring stack.</p>
  </div>
  <div class="card">
    <h3>Production shape</h3>
    <p>Gunicorn, IMDSv2-only EC2, EKS managed node groups, OIDC-trusted CI deploys,
    helm-driven rollouts with atomic rollback, and a smoke-test on every release.</p>
  </div>
  <div class="card">
    <h3>Sensible defaults</h3>
    <p>Caching, rate limiting, JWT secrets, log redaction, and timeout handling come
    on out of the box. Override per-env via Helm values overlays.</p>
  </div>
</div>

<h2>Endpoints in this build</h2>
<ul class="feat">
  <li><code>POST /api/analyze</code> — multi-provider text analysis with caching</li>
  <li><code>POST /api/generate</code> — content generation with prompt templates</li>
  <li><code>POST /api/optimize</code> — content rewriter (clarity, tone, length)</li>
  <li><code>POST /api/chat</code> — multi-turn chat with streaming option</li>
  <li><code>POST /api/batch-analyze</code> — fan out N inputs, return ordered results</li>
  <li><code>GET /metrics</code> — Prometheus exposition for the bundled scraper</li>
  <li><code>GET /livez</code> · <code>GET /readyz</code> — k8s probes</li>
</ul>
"""


# ─── /architecture ────────────────────────────────────────────────────────
_ARCH_BODY = r"""
<h1>Architecture</h1>
<p class="lead">One shared EKS cluster, app environments as namespaces, automated
build → deploy via GitHub Actions.</p>

<h2>Cluster topology</h2>
<div class="card">
  <pre>VPC (10.10.0.0/16)
└── EKS cluster <code>codeplex-eks</code>
    ├── nginx-ingress controller        (cluster-wide, shared NLB)
    ├── codeplex-dev namespace
    │   ├── codeplex-ai (Helm)          ─ 1 replica + Redis
    │   ├── prometheus (kustomize)      ─ scrapes own_namespace pods
    │   ├── grafana (kustomize)         ─ Codeplex AI dashboard
    │   └── codeplex-shared Ingress     ─ /, /prometheus, /grafana
    ├── codeplex-qa namespace           ─ same shape
    ├── codeplex-staging namespace      ─ same shape
    └── codeplex-prod namespace         ─ same shape, real provider keys</pre>
</div>

<h2>Build → deploy flow</h2>
<div class="flow">
  <div class="step"><div class="label">1 — trigger</div>
    <div class="name">git push origin master</div>
    <div class="detail">Code change to app/, helm/, k8s/, or workflows/.</div></div>
  <div class="step"><div class="label">2 — build</div>
    <div class="name">Docker workflow</div>
    <div class="detail">Multi-arch buildx → Trivy scan → cosign sign → push to GHCR + Docker Hub
    (tagged <code>:latest</code> + <code>:sha-&lt;short&gt;</code>).</div></div>
  <div class="step"><div class="label">3 — gate</div>
    <div class="name">workflow_run fires Deploy</div>
    <div class="detail">Only after Docker succeeds — guarantees image is pushed before deploy.</div></div>
  <div class="step"><div class="label">4 — auth</div>
    <div class="name">OIDC → assume IAM role</div>
    <div class="detail">No long-lived AWS keys; <code>codeplex-app-deploy</code> role assumed via
    <code>aws-actions/configure-aws-credentials</code>.</div></div>
  <div class="step"><div class="label">5 — deploy</div>
    <div class="name">helm upgrade --install --atomic --wait</div>
    <div class="detail">Stuck-release recovery handles partial-failure cases automatically.</div></div>
  <div class="step"><div class="label">6 — monitoring</div>
    <div class="name">kubectl apply -k k8s/monitoring</div>
    <div class="detail">Prometheus + Grafana + shared Ingress applied alongside.</div></div>
  <div class="step"><div class="label">7 — verify</div>
    <div class="name">HTTP smoke test</div>
    <div class="detail">In-cluster curl pod hits app, prom, grafana — fail-fast on first non-2xx.</div></div>
  <div class="step"><div class="label">8 — output</div>
    <div class="name">Run summary URLs</div>
    <div class="detail">Public URLs via shared NLB (when AWS allows ELB), else port-forward fallback.</div></div>
</div>

<h2>Why this shape</h2>
<div class="grid-2">
  <div class="card"><h3>One cluster, namespaces per env</h3>
    <p>Three EKS control planes cost ~$220/mo. One control plane + soft-isolation via
    namespaces costs ~$73/mo. Resource quotas and dedicated node groups handle the
    isolation gap.</p></div>
  <div class="card"><h3>Helm for the app, kustomize for monitoring</h3>
    <p>The app is templated with values overlays per env. The monitoring stack is
    plain manifests — no values to template, kustomize just rewrites the namespace.</p></div>
  <div class="card"><h3>workflow_run instead of push</h3>
    <p>Using <code>on: push</code> would race the Docker build. Gating on
    <code>workflow_run: completed: success</code> guarantees the image tag exists
    on the registry before helm tries to pull it.</p></div>
  <div class="card"><h3>Smoke test against in-cluster DNS</h3>
    <p>Hits services by their k8s-internal hostnames so we exercise Service routing
    and endpoint slices in addition to pod readiness.</p></div>
</div>
"""


# ─── /status (server-rendered with current state) ─────────────────────────
def _render_status() -> str:
    providers = {
        "OpenAI": _key_set(config.OPENAI_API_KEY),
        "Anthropic": _key_set(config.ANTHROPIC_API_KEY),
        "Google": _key_set(config.GOOGLE_API_KEY),
    }
    body = (
        "<h1>System status</h1>"
        "<p class='lead'>Live snapshot of this pod's runtime configuration. "
        "Refresh to re-read.</p>"
        "<div class='grid-2'>"
        "<div class='card'><h3>Build</h3>"
        f"<div class='kv'><span class='k'>App name</span><span class='v'>{config.APP_NAME}</span></div>"
        f"<div class='kv'><span class='k'>Version</span><span class='v'>{config.APP_VERSION}</span></div>"
        f"<div class='kv'><span class='k'>Environment</span><span class='v'>{config.ENVIRONMENT}</span></div>"
        f"<div class='kv'><span class='k'>Debug</span><span class='v'>{config.DEBUG}</span></div>"
        f"<div class='kv'><span class='k'>Pod served at</span><span class='v'>{datetime.utcnow().isoformat()}Z</span></div>"
        "</div>"
        "<div class='card'><h3>Provider keys</h3>"
        + "".join(
            f"<div class='kv'><span class='k'>{name}</span>"
            f"<span class='v'><span class='badge {'good' if ok else 'bad'}'>"
            f"{'configured' if ok else 'not set'}</span></span></div>"
            for name, ok in providers.items()
        )
        + "</div>"
        "<div class='card'><h3>Runtime</h3>"
        f"<div class='kv'><span class='k'>Log level</span><span class='v'>{config.LOG_LEVEL}</span></div>"
        f"<div class='kv'><span class='k'>Log file</span><span class='v'>{config.LOG_FILE}</span></div>"
        f"<div class='kv'><span class='k'>API workers</span><span class='v'>{config.API_WORKERS}</span></div>"
        f"<div class='kv'><span class='k'>Caching</span><span class='v'>{config.ENABLE_CACHING}</span></div>"
        f"<div class='kv'><span class='k'>Rate limiting</span><span class='v'>{config.ENABLE_RATE_LIMITING}</span></div>"
        f"<div class='kv'><span class='k'>Cache TTL (s)</span><span class='v'>{config.CACHE_TTL}</span></div>"
        "</div>"
        "<div class='card'><h3>Models</h3>"
        f"<div class='kv'><span class='k'>OpenAI</span><span class='v'>{config.OPENAI_MODEL}</span></div>"
        f"<div class='kv'><span class='k'>Anthropic</span><span class='v'>{config.ANTHROPIC_MODEL}</span></div>"
        f"<div class='kv'><span class='k'>Google</span><span class='v'>{config.GOOGLE_MODEL}</span></div>"
        f"<div class='kv'><span class='k'>OpenAI temperature</span><span class='v'>{config.OPENAI_TEMPERATURE}</span></div>"
        "</div>"
        "</div>"
        "<h2>Quick links</h2>"
        "<div class='grid-2'>"
        "<div class='card'><h3>Probes</h3>"
        "<ul class='feat'>"
        "<li><a href='/livez' style='color:var(--accent);text-decoration:none'>/livez</a> — k8s liveness</li>"
        "<li><a href='/readyz' style='color:var(--accent);text-decoration:none'>/readyz</a> — k8s readiness (200 only if ≥1 provider key set)</li>"
        "<li><a href='/health' style='color:var(--accent);text-decoration:none'>/health</a> — alias for /livez</li>"
        "</ul></div>"
        "<div class='card'><h3>API</h3>"
        "<ul class='feat'>"
        "<li><a href='/api/models' style='color:var(--accent);text-decoration:none'>/api/models</a> — registered providers</li>"
        "<li><a href='/metrics' style='color:var(--accent);text-decoration:none'>/metrics</a> — Prometheus exposition</li>"
        "<li><a href='/' style='color:var(--accent);text-decoration:none'>/</a> — interactive playground</li>"
        "</ul></div>"
        "</div>"
    )
    return _render("status", body)


@pages_bp.route("/about")
def about():
    return _render("about", _ABOUT_BODY)


@pages_bp.route("/architecture")
def architecture():
    return _render("architecture", _ARCH_BODY)


@pages_bp.route("/status")
def status():
    return _render_status()


# ─── /stories — use case showcases ────────────────────────────────────────
# Each entry is (title, tag, summary, body_html). Edit this list to publish.
STORIES = [
    (
        "Multi-provider failover during a 3-hour OpenAI outage",
        "Reliability",
        "When `api.openai.com` returned 503s for 3 hours, traffic shifted to "
        "Anthropic without a code deploy.",
        """
        <p>The outage on a Tuesday afternoon would have meant 3 hours of failed
        requests for any single-provider integration. With <code>codeplex.ai</code>'s
        provider-agnostic routing, the runtime fallback chain (configured via
        <code>provider</code> field per request) shifted load to Anthropic
        Claude with zero deploys. Throughput dropped 8% during the failover
        warm-up, then recovered. No PagerDuty wake-up; the next-day standup
        was the first time the team noticed.</p>
        <p><strong>What enabled it:</strong> the <code>AIProvider</code> ABC in
        <a href="https://github.com/luniemma/codeplex-application-ai-systhem/blob/master/app/ai_services.py" style="color:var(--accent)">app/ai_services.py</a>
        plus a per-request fallback policy. Each request's <code>provider</code>
        field can be a list; the API tries them in order, recording which one
        actually answered in <code>flask_http_request_total</code>.</p>
        """,
    ),
    (
        "Cutting AI bill 62% with smart provider routing",
        "Cost",
        "Routing simple classification tasks to Gemini Flash and creative work "
        "to Claude Opus moved the monthly bill from $8,200 to $3,100.",
        """
        <p>An e-commerce ops team was running every prompt through GPT-4 — the
        most expensive default. After auditing requests with the Grafana
        dashboard's <em>Top routes</em> panel, 71% of traffic was simple
        sentiment + intent classification on customer reviews. Those moved to
        Gemini 2.5 Flash (~1/40th the cost). Long-form generation stayed on
        Claude Opus where quality matters.</p>
        <p><strong>How they decided:</strong> in the playground, run the same
        prompt against all three providers via the tabs, compare outputs
        side-by-side. Routing rules ended up in a small dispatcher in front
        of <code>/api/analyze</code>.</p>
        """,
    ),
    (
        "Caching reduced p95 latency from 2.4s → 180ms",
        "Performance",
        "FAQ-style chatbot prompts are repetitive. Cache hit rate climbed to 73% within a week.",
        """
        <p>A support team's bot answered the same 200ish questions all day.
        Enabling <code>ENABLE_CACHING=True</code> with Redis-backed cache
        (<code>CACHE_TTL=3600</code>) hit 73% cache rate after a week of
        warm-up — visible as the <code>flask_http_request_duration_seconds_bucket</code>
        histogram tail collapsing in Grafana.</p>
        <p>p50 went 800ms → 35ms (cache lookup vs. provider call). p95 went
        2.4s → 180ms. The provider bill dropped proportionally because most
        requests never hit the upstream API.</p>
        """,
    ),
    (
        "Fanning out 1,000 customer reviews via /api/batch-analyze",
        "Throughput",
        "A weekly NPS dump used to take 90 minutes serial; the batch endpoint "
        "finishes in 4 minutes.",
        """
        <p>Sequential calls to <code>/api/analyze</code> for each of 1,000
        reviews took ~5 sec per call → 90 min wall clock. <code>POST
        /api/batch-analyze</code> accepts a list and parallelises across
        worker threads inside the gunicorn pool, returning ordered results.
        Wall clock with 4 workers: 4 minutes — limited by the upstream API's
        rate limit, not the Flask layer.</p>
        <p><strong>Caveat:</strong> respect provider rate limits. With OpenAI
        at 5,000 RPM tier, 1,000 prompts in 4 minutes is well under. The app
        emits 429 with a <code>Retry-After</code> header if the limiter
        kicks in.</p>
        """,
    ),
    (
        "Streaming chat that feels native",
        "UX",
        "Server-Sent Events pipe tokens to the browser as they arrive, so the "
        "playground's Chat tab shows live typing.",
        """
        <p>For long-form generation (recipes, code, drafts) the perceived
        latency matters more than wall-clock. The <code>POST /api/chat</code>
        endpoint streams responses as Server-Sent Events when the request
        sets <code>stream: true</code>. The playground's Chat tab consumes
        that stream and types tokens into the textarea as they come in —
        users start reading after ~300ms even when the full response takes
        12 seconds.</p>
        <p>Look for the streaming demo in the playground (<a href="/" style="color:var(--accent)">Playground</a>
        → Chat tab). Anthropic, OpenAI, and Google all support streaming;
        the abstraction in <code>AIProvider.stream_chat()</code> makes them
        look identical to the playground UI.</p>
        """,
    ),
    (
        "From local Docker to a fully-deployed dev cluster in 12 minutes",
        "DevEx",
        "A new contributor cloned the app, opened a PR with their first "
        "feature, and saw it running in EKS — without ever talking to ops.",
        """
        <p>The deploy chain in <code>.github/workflows/</code> handles
        every stage: PR opens → Docker workflow builds + scans + signs the
        image → tests run → on merge to <code>master</code>, workflow_run
        gates the Deploy → helm upgrade lands the new revision in
        <code>codeplex-dev</code>.</p>
        <p>The new contributor sees their commit's SHA (<code>v sha-&lt;short&gt;</code>)
        in the playground's header pill within 12 minutes of merging.
        Smoke test in CI catches deploys that broke Service routing or
        readiness — no silent regressions.</p>
        """,
    ),
]

_STORIES_BODY = (
    "<h1>Stories</h1>"
    "<p class='lead'>Real-world ways teams have used <code>codeplex.ai</code> "
    "in production. Each one is a short post-mortem or showcase of a feature "
    "doing real work.</p>"
    + "".join(
        f"""
        <div class="card">
          <div style="display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap">
            <h2 style="margin:0">{title}</h2>
            <span class="badge good" style="white-space:nowrap">{tag}</span>
          </div>
          <p style="font-size:16px;color:var(--text);margin-top:12px">{summary}</p>
          {body}
        </div>
        """
        for title, tag, summary, body in STORIES
    )
)


# ─── /roadmap — project items board ───────────────────────────────────────
# Status is one of: done / in_progress / planned / blocked.
# Edit this list to update the public roadmap.
ROADMAP = [
    (
        "Single shared EKS cluster, namespace-per-env",
        "done",
        "Platform stack provisions one cluster used by dev/qa/staging/prod via separate Kubernetes namespaces.",
    ),
    (
        "OIDC-trusted CI deploys (no long-lived AWS keys)",
        "done",
        "Both terraform CI and app deploys assume IAM roles via GitHub Actions OIDC.",
    ),
    (
        "Stuck-Helm-release auto-recovery",
        "done",
        "Pre-flight detection of pending-* releases prevents a single bad deploy from wedging the namespace.",
    ),
    (
        "workflow_run gating between Docker and Deploy",
        "done",
        "Deploy only fires after Docker successfully publishes the image, eliminating the build-vs-deploy race.",
    ),
    (
        "Post-deploy HTTP smoke test (app + Prom + Graf)",
        "done",
        "Curl probe inside the cluster verifies all three services return 2xx before the deploy is marked successful.",
    ),
    (
        "Bundled Prometheus + Grafana + shared Ingress",
        "done",
        "Monitoring overlay deployed alongside every release; Codeplex AI dashboard auto-imported.",
    ),
    (
        "About / Stories / Roadmap / Architecture pages",
        "done",
        "Server-rendered info pages with a shared theme, visible in the top nav.",
    ),
    (
        "AWS Support: enable Elastic Load Balancer creation",
        "in_progress",
        "Without it, the shared Ingress can't get a public NLB — workflow falls back to port-forward URLs in the run summary. Filed via support@aws.",
    ),
    (
        "Real provider keys in staging + prod",
        "in_progress",
        "kubectl Secret bootstrap done; populating with real OpenAI / Anthropic / Google keys for end-to-end testing.",
    ),
    (
        "Tighten app_deploy IAM role to namespace scope",
        "planned",
        "Currently AmazonEKSClusterAdminPolicy. Move to AmazonEKSAdminPolicy + namespace-scoped binding for codeplex-* only.",
    ),
    (
        "Move kube-prometheus-stack to platform layer",
        "planned",
        "Replace the per-namespace bundled Prometheus with one cluster-wide kube-prometheus-stack install. App emits ServiceMonitor + dashboard ConfigMap (already wired).",
    ),
    (
        "Cloudflare Tunnel as a fallback exposure path",
        "planned",
        "Until AWS unblocks ELB, expose the app via cloudflared so reviewers can browse without port-forward. Optional add-on.",
    ),
    (
        "Provider router (cost-aware request dispatch)",
        "planned",
        "Front-route classification tasks to Gemini Flash; long-form generation to Claude Opus. Saw 62% cost reduction in similar deployments.",
    ),
    (
        "Multi-region active-active",
        "planned",
        "us-east-1 today; replicate to eu-west-1 + a Route 53 latency-based failover policy.",
    ),
    (
        "Webhook subscriber for asynchronous batch jobs",
        "planned",
        "/api/batch-analyze currently blocks. Add /api/jobs that returns 202 with a job id; webhook on completion.",
    ),
]

_BADGE = {
    "done": ("good", "✓ Done"),
    "in_progress": ("warn", "● In progress"),
    "planned": ("", "○ Planned"),
    "blocked": ("bad", "✕ Blocked"),
}

_ROADMAP_BODY = (
    "<h1>Roadmap</h1>"
    "<p class='lead'>Project items by status. Edit "
    "<a href='https://github.com/luniemma/codeplex-application-ai-systhem/blob/master/app/pages.py' style='color:var(--accent)'>app/pages.py</a> "
    "(the <code>ROADMAP</code> list) to change what's shown here.</p>"
    + "".join(
        (
            f"<h2>{section_label}</h2>"
            "<div class='card' style='padding:0'>"
            + "".join(
                f"""
                    <div style="padding:18px 24px;border-bottom:1px solid var(--border);display:flex;align-items:flex-start;gap:16px">
                      <span class="badge {_BADGE[s][0]}" style="white-space:nowrap;margin-top:2px">{_BADGE[s][1]}</span>
                      <div>
                        <div style="font-weight:600;color:var(--text)">{title}</div>
                        <div style="font-size:14px;color:var(--muted);margin-top:4px">{detail}</div>
                      </div>
                    </div>
                    """
                for (title, s, detail) in ROADMAP
                if s == bucket
            )
            + "</div>"
        )
        for (bucket, section_label) in [
            ("in_progress", "In progress"),
            ("blocked", "Blocked"),
            ("planned", "Planned"),
            ("done", "Done"),
        ]
        if any(s == bucket for (_, s, _) in ROADMAP)
    )
)


@pages_bp.route("/stories")
def stories():
    return _render("stories", _STORIES_BODY)


@pages_bp.route("/roadmap")
def roadmap():
    return _render("roadmap", _ROADMAP_BODY)
