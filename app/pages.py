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
    <a href="/docs" class="{% if active == 'docs' %}active{% endif %}">Docs</a>
    <a href="/compare" class="{% if active == 'compare' %}active{% endif %}">Compare</a>
    <a href="/faq" class="{% if active == 'faq' %}active{% endif %}">FAQ</a>
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


# ─── /docs — multi-language quick-start ───────────────────────────────────
# Each entry is (endpoint, description, samples_by_lang). Edit to add more
# endpoints or new language tabs.
_DOC_SAMPLES = [
    (
        "POST /api/analyze",
        "Static analysis of a code snippet — surfaces smells, complexity hot-spots, and suggestions.",
        {
            "curl": (
                "curl -X POST https://codeplex.ai/api/analyze \\\n"
                "  -H 'Content-Type: application/json' \\\n"
                "  -d '{\n"
                "    \"code\": \"def add(a, b):\\n    return a + b\",\n"
                "    \"provider\": \"openai\"\n"
                "  }'"
            ),
            "python": (
                "import requests\n\n"
                "resp = requests.post(\n"
                "    'https://codeplex.ai/api/analyze',\n"
                "    json={\n"
                "        'code': 'def add(a, b):\\n    return a + b',\n"
                "        'provider': 'openai',\n"
                "    },\n"
                "    timeout=30,\n"
                ")\n"
                "resp.raise_for_status()\n"
                "print(resp.json()['data']['analysis'])"
            ),
            "javascript": (
                "const res = await fetch('https://codeplex.ai/api/analyze', {\n"
                "  method: 'POST',\n"
                "  headers: { 'Content-Type': 'application/json' },\n"
                "  body: JSON.stringify({\n"
                "    code: 'def add(a, b):\\n    return a + b',\n"
                "    provider: 'openai',\n"
                "  }),\n"
                "});\n"
                "const { data } = await res.json();\n"
                "console.log(data.analysis);"
            ),
        },
    ),
    (
        "POST /api/generate",
        "Generate code from a natural-language prompt; response includes the generated source plus a short rationale.",
        {
            "curl": (
                "curl -X POST https://codeplex.ai/api/generate \\\n"
                "  -H 'Content-Type: application/json' \\\n"
                "  -d '{\n"
                "    \"prompt\": \"Write a Python LRU cache with size N.\",\n"
                "    \"provider\": \"anthropic\"\n"
                "  }'"
            ),
            "python": (
                "import requests\n\n"
                "resp = requests.post(\n"
                "    'https://codeplex.ai/api/generate',\n"
                "    json={\n"
                "        'prompt': 'Write a Python LRU cache with size N.',\n"
                "        'provider': 'anthropic',\n"
                "    },\n"
                ")\n"
                "print(resp.json()['data']['generated_code'])"
            ),
            "javascript": (
                "const res = await fetch('https://codeplex.ai/api/generate', {\n"
                "  method: 'POST',\n"
                "  headers: { 'Content-Type': 'application/json' },\n"
                "  body: JSON.stringify({\n"
                "    prompt: 'Write a Python LRU cache with size N.',\n"
                "    provider: 'anthropic',\n"
                "  }),\n"
                "});\n"
                "const { data } = await res.json();\n"
                "console.log(data.generated_code);"
            ),
        },
    ),
    (
        "POST /api/chat (streaming)",
        "Multi-turn chat. Set <code>stream: true</code> to receive Server-Sent Events as tokens arrive.",
        {
            "curl": (
                "curl -N -X POST https://codeplex.ai/api/chat/stream \\\n"
                "  -H 'Content-Type: application/json' \\\n"
                "  -d '{\n"
                "    \"messages\": [\n"
                "      {\"role\": \"user\", \"content\": \"Explain Python decorators briefly.\"}\n"
                "    ],\n"
                "    \"provider\": \"openai\"\n"
                "  }'"
            ),
            "python": (
                "import json, requests\n\n"
                "with requests.post(\n"
                "    'https://codeplex.ai/api/chat/stream',\n"
                "    json={\n"
                "        'messages': [{'role': 'user', 'content': 'Explain decorators.'}],\n"
                "        'provider': 'openai',\n"
                "    },\n"
                "    stream=True,\n"
                ") as r:\n"
                "    for line in r.iter_lines():\n"
                "        if line and line.startswith(b'data: '):\n"
                "            payload = line[6:].decode()\n"
                "            if payload == '[DONE]':\n"
                "                break\n"
                "            chunk = json.loads(payload).get('chunk', '')\n"
                "            print(chunk, end='', flush=True)"
            ),
            "javascript": (
                "const res = await fetch('https://codeplex.ai/api/chat/stream', {\n"
                "  method: 'POST',\n"
                "  headers: { 'Content-Type': 'application/json' },\n"
                "  body: JSON.stringify({\n"
                "    messages: [{ role: 'user', content: 'Explain decorators.' }],\n"
                "    provider: 'openai',\n"
                "  }),\n"
                "});\n"
                "const reader = res.body.getReader();\n"
                "const dec = new TextDecoder();\n"
                "let buf = '';\n"
                "while (true) {\n"
                "  const { done, value } = await reader.read();\n"
                "  if (done) break;\n"
                "  buf += dec.decode(value, { stream: true });\n"
                "  for (const ev of buf.split('\\n\\n').slice(0, -1)) {\n"
                "    const line = ev.trim();\n"
                "    if (!line.startsWith('data:')) continue;\n"
                "    const payload = line.slice(5).trim();\n"
                "    if (payload === '[DONE]') return;\n"
                "    const { chunk } = JSON.parse(payload);\n"
                "    if (chunk) process.stdout.write(chunk);\n"
                "  }\n"
                "  buf = buf.split('\\n\\n').pop();\n"
                "}"
            ),
        },
    ),
    (
        "POST /api/batch-analyze",
        "Analyse a list of snippets in one request. Partial success is supported — failed entries appear with an <code>error</code> field.",
        {
            "curl": (
                "curl -X POST https://codeplex.ai/api/batch-analyze \\\n"
                "  -H 'Content-Type: application/json' \\\n"
                "  -d '{\n"
                "    \"codes\": [\n"
                "      \"def a(): pass\",\n"
                "      \"def b(): return 1/0\"\n"
                "    ],\n"
                "    \"provider\": \"google\"\n"
                "  }'"
            ),
            "python": (
                "import requests\n\n"
                "resp = requests.post(\n"
                "    'https://codeplex.ai/api/batch-analyze',\n"
                "    json={\n"
                "        'codes': ['def a(): pass', 'def b(): return 1/0'],\n"
                "        'provider': 'google',\n"
                "    },\n"
                "    timeout=120,\n"
                ")\n"
                "for i, item in enumerate(resp.json()['data']['results']):\n"
                "    print(f'[{i}]', item.get('analysis') or item.get('error'))"
            ),
            "javascript": (
                "const res = await fetch('https://codeplex.ai/api/batch-analyze', {\n"
                "  method: 'POST',\n"
                "  headers: { 'Content-Type': 'application/json' },\n"
                "  body: JSON.stringify({\n"
                "    codes: ['def a(): pass', 'def b(): return 1/0'],\n"
                "    provider: 'google',\n"
                "  }),\n"
                "});\n"
                "const { data } = await res.json();\n"
                "data.results.forEach((r, i) =>\n"
                "  console.log(`[${i}]`, r.analysis ?? r.error),\n"
                ");"
            ),
        },
    ),
]

_DOCS_CSS = r"""
.lang-tabs { display: flex; gap: 2px; margin-top: 12px; }
.lang-tabs .lang {
  padding: 6px 14px; cursor: pointer; font-size: 13px; color: var(--muted);
  border: 1px solid var(--border); border-bottom: none;
  border-radius: 8px 8px 0 0; user-select: none; background: var(--panel-2);
  transition: color 0.15s, background 0.15s;
}
.lang-tabs .lang:hover { color: var(--text); }
.lang-tabs .lang.active { color: var(--text); background: var(--code-bg); border-color: var(--accent); }
.lang-panel { display: none; border: 1px solid var(--border); border-radius: 0 10px 10px 10px;
  background: var(--code-bg); padding: 0; overflow: hidden; }
.lang-panel.active { display: block; }
.lang-panel pre { margin: 0; padding: 16px; background: transparent; }
.endpoint-tag {
  display: inline-block; font-family: ui-monospace, Consolas, monospace;
  font-size: 13px; color: var(--accent); background: var(--panel-2);
  border: 1px solid var(--border); padding: 4px 10px; border-radius: 6px;
}
.toc {
  display: flex; flex-wrap: wrap; gap: 8px; margin: 16px 0 28px;
}
.toc a {
  font-size: 13px; padding: 6px 12px; border-radius: 999px;
  background: var(--panel-2); border: 1px solid var(--border);
  color: var(--muted); text-decoration: none; transition: all 0.15s;
}
.toc a:hover { color: var(--text); border-color: var(--accent); }
"""

_DOCS_JS = r"""
<script>
  document.querySelectorAll('.docs-block').forEach(block => {
    const langs = block.querySelectorAll('.lang');
    const panels = block.querySelectorAll('.lang-panel');
    langs.forEach(l => l.addEventListener('click', () => {
      langs.forEach(x => x.classList.toggle('active', x === l));
      panels.forEach(p => p.classList.toggle('active', p.dataset.lang === l.dataset.lang));
    }));
  });
</script>
"""


def _docs_block(idx: int, endpoint: str, desc: str, samples: dict) -> str:
    anchor = endpoint.replace(" ", "-").replace("/", "-").replace("(", "").replace(")", "").lower()
    tabs = "".join(
        f'<span class="lang {"active" if i == 0 else ""}" data-lang="{lang}">{lang}</span>'
        for i, lang in enumerate(samples.keys())
    )
    panels = "".join(
        f'<div class="lang-panel {"active" if i == 0 else ""}" data-lang="{lang}">'
        f"<pre><code>{code.replace('<', '&lt;').replace('>', '&gt;')}</code></pre>"
        "</div>"
        for i, (lang, code) in enumerate(samples.items())
    )
    return (
        f'<div class="card docs-block" id="{anchor}">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap">'
        f'<span class="endpoint-tag">{endpoint}</span></div>'
        f"<p>{desc}</p>"
        f'<div class="lang-tabs">{tabs}</div>'
        f"{panels}"
        "</div>"
    )


_DOCS_BODY = (
    "<style>" + _DOCS_CSS + "</style>"
    "<h1>Docs</h1>"
    "<p class='lead'>Every endpoint is the same shape: <code>POST</code> a JSON body, "
    "pick a <code>provider</code>, get a JSON response. Pick a language tab on each "
    "block to copy a working snippet.</p>"
    "<div class='toc'>"
    + "".join(
        f'<a href="#{ep.replace(" ", "-").replace("/", "-").replace("(", "").replace(")", "").lower()}">{ep}</a>'
        for ep, _, _ in _DOC_SAMPLES
    )
    + "</div>"
    "<div class='card'>"
    "<h3>Common request shape</h3>"
    "<p>Every endpoint accepts a JSON body and returns "
    "<code>{ success, data, error?, request_id }</code>. The <code>provider</code> "
    "field is optional — if omitted, the first configured provider wins. Pass "
    "<code>X-Request-ID</code> to correlate client logs with the server's "
    "request id (also echoed back in the response header).</p>"
    "</div>"
    + "".join(_docs_block(i, ep, desc, samples) for i, (ep, desc, samples) in enumerate(_DOC_SAMPLES))
    + "<h2>Error handling</h2>"
    "<div class='card'>"
    "<p>All errors are JSON with a stable shape: <code>{ success: false, error: \"...\", code: \"...\", request_id }</code>. "
    "Common codes:</p>"
    "<ul class='feat'>"
    "<li><code>400 invalid_request</code> — missing or malformed body</li>"
    "<li><code>401 missing_key</code> — the requested provider has no key configured</li>"
    "<li><code>429 rate_limited</code> — back off using the <code>Retry-After</code> header</li>"
    "<li><code>502 upstream_error</code> — the provider returned non-2xx; retry with another <code>provider</code></li>"
    "<li><code>504 timeout</code> — request exceeded the configured upper bound (see "
    "<code>/status</code>)</li>"
    "</ul></div>"
    + _DOCS_JS
)


# ─── /faq ─────────────────────────────────────────────────────────────────
FAQ = [
    (
        "Do I need accounts with all three providers?",
        "No. Configure any one of <code>OPENAI_API_KEY</code>, <code>ANTHROPIC_API_KEY</code>, "
        "or <code>GOOGLE_API_KEY</code> and the corresponding endpoints will work. "
        "Requests that name an unconfigured provider get a <code>401 missing_key</code> error "
        "rather than silently falling back, so you can see what's wired up.",
    ),
    (
        "How do you handle authentication?",
        "Server-side: provider keys live in environment variables and are never echoed in logs "
        "(redaction is in <code>app/logging_setup.py</code>). Client-side: the public API is "
        "currently open with a CORS allowlist and rate limits — a JWT layer is planned for "
        "the 1.2 release (<a href='/roadmap' style='color:var(--accent)'>see roadmap</a>).",
    ),
    (
        "What are the rate limits?",
        "Default is 30 requests/minute per IP across <code>/api/*</code> — see the Flask-Limiter "
        "config in <code>app/security.py</code>. Production tiers configure a higher per-key "
        "limit via Redis-backed storage; without Redis the limiter falls back to in-process "
        "(per-worker) counters.",
    ),
    (
        "Does the API stream responses?",
        "Yes — <code>POST /api/chat/stream</code> returns Server-Sent Events with one "
        "<code>chunk</code> per event, terminated by <code>data: [DONE]</code>. The "
        "playground's Chat tab uses it by default; toggle the 'Stream' checkbox to compare "
        "with the buffered <code>/api/chat</code> endpoint.",
    ),
    (
        "How is caching implemented?",
        "Per-route Redis-backed cache, keyed by a SHA-256 of the request body. TTL is "
        "<code>CACHE_TTL</code> seconds (default 3600). Caching is disabled for "
        "<code>/api/chat</code> (conversations are stateful) and "
        "<code>/api/batch-analyze</code> (partial-success makes cache keys leaky). Toggle the "
        "global flag with <code>ENABLE_CACHING</code>.",
    ),
    (
        "How do I switch providers per-request?",
        "Set the <code>provider</code> field in the JSON body to <code>openai</code>, "
        "<code>anthropic</code>, or <code>google</code>. Omitting it picks the first configured "
        "provider in the order they appear in <code>/api/models</code>. The provider that "
        "actually answered is echoed in <code>data.provider</code> in the response.",
    ),
    (
        "Where do I see metrics?",
        "<code>GET /metrics</code> exposes Prometheus format. The bundled monitoring overlay "
        "(<code>k8s/monitoring/</code>) imports a Codeplex AI Grafana dashboard automatically: "
        "request volume, latency histograms, top routes, and cache hit rate. "
        "<a href='/architecture' style='color:var(--accent)'>Architecture page</a> has the cluster diagram.",
    ),
    (
        "How do I deploy this to my own cluster?",
        "<code>helm/codeplex-ai</code> is the chart; <code>helm upgrade --install</code> with a "
        "values overlay per environment is the supported path. The repo's "
        "<code>.github/workflows/deploy.yml</code> shows the full chain: OIDC → EKS auth → helm "
        "upgrade → smoke test. Bring your own kubeconfig and image registry.",
    ),
    (
        "What about cost?",
        "Provider billing is per-token, paid directly to OpenAI/Anthropic/Google — Codeplex is "
        "free software with no usage fees. The biggest cost lever is routing: cheap "
        "classifiers (Gemini Flash) for routine work, expensive models (Claude Opus, GPT-4) for "
        "long-form generation. <a href='/compare' style='color:var(--accent)'>Compare page</a> "
        "lays out price per million tokens.",
    ),
    (
        "Is there an SDK?",
        "Not yet — the API is intentionally HTTP-first so any language with a JSON client works. "
        "If you want typed bindings, the OpenAPI spec at <code>/api/openapi.json</code> can "
        "generate them for ~30 languages via <code>openapi-generator</code>. A first-party "
        "Python SDK is on the roadmap.",
    ),
    (
        "How do I report bugs or request features?",
        "Open an issue on GitHub: <a href='https://github.com/luniemma/codeplex-application-ai-systhem/issues' "
        "style='color:var(--accent)'>github.com/luniemma/codeplex-application-ai-systhem</a>. "
        "Include the <code>X-Request-ID</code> header value from a failing response — server "
        "logs are correlated by that id.",
    ),
    (
        "What's the license?",
        "MIT. See <code>LICENSE</code> in the repo root. Provider SDK licenses are separate and "
        "apply per the provider's terms.",
    ),
]

_FAQ_CSS = r"""
details.faq {
  background: var(--panel); border: 1px solid var(--border);
  border-radius: 10px; padding: 0; margin: 10px 0;
  transition: border-color 0.15s;
}
details.faq[open] { border-color: var(--accent); }
details.faq summary {
  padding: 16px 20px; cursor: pointer; list-style: none;
  font-weight: 600; color: var(--text); font-size: 15px;
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
}
details.faq summary::-webkit-details-marker { display: none; }
details.faq summary::after {
  content: "+"; color: var(--muted); font-size: 22px; line-height: 1;
  transition: transform 0.15s, color 0.15s; flex-shrink: 0;
}
details.faq[open] summary::after { content: "−"; color: var(--accent); }
details.faq summary:hover { color: var(--accent); }
details.faq .answer { padding: 0 20px 18px; color: var(--muted); font-size: 14px; line-height: 1.65; }
details.faq .answer code { background: var(--code-bg); padding: 2px 6px; border-radius: 4px; font-size: 12px; }
"""

_FAQ_BODY = (
    "<style>" + _FAQ_CSS + "</style>"
    "<h1>Frequently asked</h1>"
    "<p class='lead'>Quick answers to the questions teams ask before adopting "
    "Codeplex. For anything not here, open an issue or check the "
    "<a href='/docs' style='color:var(--accent)'>docs</a>.</p>"
    + "".join(
        f"<details class='faq'>"
        f"<summary>{q}</summary>"
        f"<div class='answer'>{a}</div>"
        "</details>"
        for q, a in FAQ
    )
)


# ─── /compare — provider comparison ────────────────────────────────────────
# Each row: (capability, openai, anthropic, google, note).
# Pricing reflects mainstream public list price for the model in COMPARE_MODELS
# at the time this was written; treat as a rough order-of-magnitude guide.
COMPARE_MODELS = {
    "openai": "GPT-4o",
    "anthropic": "Claude Sonnet 4.5",
    "google": "Gemini 2.5 Flash",
}

COMPARE_ROWS = [
    ("Context window", "128K tokens", "200K tokens", "1M tokens",
     "Largest wins on long-document workloads; Gemini's 1M context is the differentiator."),
    ("Price / 1M input tokens", "$2.50", "$3.00", "$0.15",
     "Flash is ~20× cheaper than the others — ideal for high-volume classifiers."),
    ("Price / 1M output tokens", "$10.00", "$15.00", "$0.60",
     "Output is where bills explode for generation-heavy workloads."),
    ("Streaming", "✓ SSE", "✓ SSE", "✓ SSE",
     "All three stream; the abstraction in <code>app/ai_services.py</code> hides the differences."),
    ("Tool use / function calling", "✓ strict mode", "✓ via Messages API", "✓",
     "OpenAI's strict-mode JSON gives the most predictable shape; Anthropic is most lenient."),
    ("Vision input", "✓", "✓", "✓",
     "All three accept image inputs in the same multimodal message; not yet exposed in the playground."),
    ("Long-form quality", "Strong", "Best (subjectively)", "Good",
     "Anecdotal pick for creative long-form drafts; benchmark on your own prompts."),
    ("Code quality", "Strong", "Strong", "Good",
     "OpenAI and Anthropic trade leadership on code benchmarks release-to-release."),
    ("Cold-start latency p50", "~600ms", "~700ms", "~250ms",
     "Flash is noticeably snappier; matters for interactive UIs."),
    ("Free tier", "Limited", "Limited", "Generous (Flash)",
     "Google has the most permissive free tier for prototyping."),
    ("Region availability", "Global", "US/EU/APAC", "Global",
     "Bedrock + Vertex give Anthropic and Google regional residency options."),
    ("Best for", "General purpose", "Long, nuanced reasoning", "High-volume + cheap",
     "These are starting heuristics, not hard rules. Test against your prompts."),
]

_COMPARE_CSS = r"""
.compare-table { width: 100%; border-collapse: collapse; margin: 18px 0;
  background: var(--panel); border-radius: 14px; overflow: hidden;
  border: 1px solid var(--border); }
.compare-table th, .compare-table td { padding: 14px 16px; text-align: left;
  border-bottom: 1px solid var(--border); font-size: 14px; }
.compare-table th { background: var(--panel-2); color: var(--muted);
  text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px;
  font-weight: 600; }
.compare-table tr:last-child td { border-bottom: none; }
.compare-table td.cap { color: var(--text); font-weight: 600; min-width: 180px; }
.compare-table td.cell { color: var(--text); font-family: ui-monospace, Consolas, monospace;
  font-size: 13px; }
.compare-table td.note { color: var(--muted); font-size: 13px; max-width: 320px; font-style: italic; }
.provider-header { display: flex; align-items: center; gap: 8px; }
.provider-header .plogo {
  width: 22px; height: 22px; border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
  color: white; font-size: 11px; font-weight: 700; flex-shrink: 0;
}
.provider-header .plogo.openai    { background: #0db66e; }
.provider-header .plogo.anthropic { background: #d97757; }
.provider-header .plogo.google    { background: #4285f4; }
.provider-header .pname { color: var(--text); font-size: 13px; font-weight: 600;
  text-transform: none; letter-spacing: 0; }
.provider-header .pmodel { color: var(--muted); font-size: 11px; font-family: ui-monospace, Consolas, monospace;
  text-transform: none; letter-spacing: 0; margin-left: 4px; }
"""

_COMPARE_BODY = (
    "<style>" + _COMPARE_CSS + "</style>"
    "<h1>Compare providers</h1>"
    "<p class='lead'>Side-by-side trade-offs between the three providers Codeplex "
    "fronts. Pricing reflects public list at the time of writing — treat as a "
    "rough order-of-magnitude. Always benchmark against your own prompts before "
    "committing.</p>"
    "<div style='overflow-x:auto'>"
    "<table class='compare-table'>"
    "<thead><tr>"
    "<th style='min-width:180px'>Capability</th>"
    "<th><div class='provider-header'><span class='plogo openai'>O</span>"
    f"<span class='pname'>OpenAI</span><span class='pmodel'>{COMPARE_MODELS['openai']}</span></div></th>"
    "<th><div class='provider-header'><span class='plogo anthropic'>A</span>"
    f"<span class='pname'>Anthropic</span><span class='pmodel'>{COMPARE_MODELS['anthropic']}</span></div></th>"
    "<th><div class='provider-header'><span class='plogo google'>G</span>"
    f"<span class='pname'>Google</span><span class='pmodel'>{COMPARE_MODELS['google']}</span></div></th>"
    "<th>Note</th>"
    "</tr></thead><tbody>"
    + "".join(
        f"<tr><td class='cap'>{cap}</td>"
        f"<td class='cell'>{o}</td>"
        f"<td class='cell'>{a}</td>"
        f"<td class='cell'>{g}</td>"
        f"<td class='note'>{note}</td></tr>"
        for cap, o, a, g, note in COMPARE_ROWS
    )
    + "</tbody></table></div>"
    "<h2>Picking a default</h2>"
    "<div class='grid-2'>"
    "<div class='card'><h3>Cost-sensitive workloads</h3>"
    "<p>Default to <strong>Gemini Flash</strong>. Reserve OpenAI or Anthropic for "
    "the long tail of prompts that the cheaper model gets wrong. The Grafana "
    "dashboard's <em>Top routes</em> panel makes this audit easy.</p></div>"
    "<div class='card'><h3>Latency-sensitive UIs</h3>"
    "<p><strong>Gemini Flash</strong> for snappy first-tokens; "
    "<strong>OpenAI streaming</strong> as a fallback. Avoid Claude Opus for "
    "interactive UIs — it's tuned for thoughtful output, not perceived speed.</p></div>"
    "<div class='card'><h3>Long-document reasoning</h3>"
    "<p><strong>Gemini 2.5 Pro</strong> (1M context) for retrieval-augmented or "
    "whole-codebase prompts. <strong>Claude Sonnet 4.5</strong> (200K) when "
    "quality of synthesis matters more than raw context size.</p></div>"
    "<div class='card'><h3>Strict structured output</h3>"
    "<p><strong>OpenAI</strong> strict-mode JSON. The other two are improving "
    "but OpenAI still has the most reliable schema adherence in production.</p></div>"
    "</div>"
)


@pages_bp.route("/docs")
def docs():
    return _render("docs", _DOCS_BODY)


@pages_bp.route("/faq")
def faq():
    return _render("faq", _FAQ_BODY)


@pages_bp.route("/compare")
def compare():
    return _render("compare", _COMPARE_BODY)
