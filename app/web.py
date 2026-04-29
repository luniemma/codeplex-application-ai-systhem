"""
Web UI Blueprint - serves the homepage and interactive playground.
"""

from flask import Blueprint, render_template_string

from app.config import config

web_bp = Blueprint("web", __name__)


def _key_set(value: str) -> bool:
    return bool(value) and not value.startswith("your_")


INDEX_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{{ app_name }}</title>
<style>
  :root {
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
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: radial-gradient(1200px 600px at 10% -10%, #1a2347 0%, transparent 60%),
                radial-gradient(900px 500px at 100% 0%, #2a1a4a 0%, transparent 60%),
                var(--bg);
    color: var(--text);
    min-height: 100vh;
    line-height: 1.5;
  }
  header {
    padding: 28px 32px;
    display: flex; align-items: center; justify-content: space-between;
    border-bottom: 1px solid var(--border);
    backdrop-filter: blur(8px);
  }
  .brand {
    display: flex; align-items: center; gap: 12px;
    font-weight: 700; font-size: 20px; letter-spacing: 0.3px;
  }
  .logo {
    width: 32px; height: 32px; border-radius: 8px;
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
    box-shadow: 0 6px 24px rgba(107, 140, 255, 0.35);
  }
  .pill {
    font-size: 12px; padding: 4px 10px; border-radius: 999px;
    background: rgba(107, 140, 255, 0.15); border: 1px solid rgba(107, 140, 255, 0.4);
    color: #c7d2ff;
  }
  main { max-width: 1100px; margin: 0 auto; padding: 32px; }
  h1 {
    font-size: 40px; line-height: 1.1; margin: 16px 0 8px;
    background: linear-gradient(135deg, #fff, #b9c2dd);
    -webkit-background-clip: text; background-clip: text; color: transparent;
  }
  .lede { color: var(--muted); font-size: 17px; max-width: 780px; }
  .grid {
    display: grid; gap: 16px;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    margin: 28px 0;
  }
  .card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 20px;
  }
  .card h3 { margin: 0 0 6px; font-size: 16px; }
  .card p { margin: 0; color: var(--muted); font-size: 14px; }
  .card .endpoint {
    font-family: ui-monospace, "JetBrains Mono", Consolas, monospace;
    font-size: 12px; color: #c7d2ff;
    background: var(--panel-2); border: 1px solid var(--border);
    padding: 4px 8px; border-radius: 6px; display: inline-block; margin-top: 10px;
  }
  .status-row { display: flex; flex-wrap: wrap; gap: 10px; margin: 12px 0 0; }
  .status {
    display: flex; align-items: center; gap: 8px;
    padding: 8px 12px; border-radius: 999px; font-size: 13px;
    border: 1px solid var(--border); background: var(--panel-2);
  }
  .dot { width: 8px; height: 8px; border-radius: 50%; }
  .dot.on  { background: var(--good); box-shadow: 0 0 10px var(--good); }
  .dot.off { background: var(--bad); }

  section { margin: 36px 0; }
  section h2 { font-size: 22px; margin: 0 0 14px; }
  .panel {
    background: var(--panel); border: 1px solid var(--border); border-radius: 14px; padding: 20px;
  }
  .row { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
  label { display: block; font-size: 13px; color: var(--muted); margin-bottom: 6px; }
  textarea, input, select {
    width: 100%; background: var(--panel-2); color: var(--text);
    border: 1px solid var(--border); border-radius: 10px; padding: 10px 12px;
    font-family: inherit; font-size: 14px; outline: none;
  }
  textarea { min-height: 120px; resize: vertical; font-family: ui-monospace, Consolas, monospace; }
  textarea:focus, input:focus, select:focus { border-color: var(--accent); }
  button {
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
    color: white; border: none; border-radius: 10px; padding: 10px 18px;
    font-weight: 600; cursor: pointer; font-size: 14px;
    box-shadow: 0 6px 20px rgba(107, 140, 255, 0.3);
    transition: transform 0.1s, box-shadow 0.1s;
  }
  button:hover { transform: translateY(-1px); box-shadow: 0 8px 24px rgba(107, 140, 255, 0.45); }
  button:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
  .output {
    margin-top: 14px; padding: 14px; background: #06091a; border: 1px solid var(--border);
    border-radius: 10px; font-family: ui-monospace, Consolas, monospace;
    font-size: 13px; white-space: pre-wrap; word-wrap: break-word;
    max-height: 360px; overflow: auto; color: #d8e2ff;
  }
  .output.error { border-color: rgba(255, 107, 107, 0.5); color: #ffd3d3; }
  .output.rendered {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 15px; line-height: 1.65; white-space: normal; color: var(--text);
  }
  .output.rendered h1, .output.rendered h2, .output.rendered h3, .output.rendered h4 {
    margin: 20px 0 8px; line-height: 1.3; color: #fff;
  }
  .output.rendered h1 { font-size: 22px; }
  .output.rendered h2 { font-size: 18px; padding-bottom: 6px; border-bottom: 1px solid var(--border); }
  .output.rendered h3 { font-size: 16px; }
  .output.rendered h4 { font-size: 14px; color: var(--muted); }
  .output.rendered p { margin: 10px 0; }
  .output.rendered ul, .output.rendered ol { margin: 10px 0; padding-left: 22px; }
  .output.rendered li { margin: 4px 0; }
  .output.rendered li > p { margin: 4px 0; }
  .output.rendered strong { color: #fff; }
  .output.rendered em { color: #d8e2ff; }
  .output.rendered hr { border: 0; border-top: 1px solid var(--border); margin: 18px 0; }
  .output.rendered a { color: var(--accent); }
  .output.rendered blockquote {
    border-left: 3px solid var(--accent); padding: 4px 14px; margin: 12px 0;
    color: var(--muted); background: rgba(107, 140, 255, 0.06);
  }
  .output.rendered code {
    font-family: ui-monospace, "JetBrains Mono", Consolas, monospace; font-size: 0.92em;
    background: var(--panel-2); border: 1px solid var(--border);
    padding: 1px 6px; border-radius: 5px;
  }
  .output.rendered pre {
    background: #06091a; border: 1px solid var(--border); border-radius: 10px;
    padding: 14px 16px; overflow-x: auto; margin: 12px 0;
  }
  .output.rendered pre code {
    background: transparent; border: 0; padding: 0; font-size: 13px;
    color: #d8e2ff; line-height: 1.55;
  }
  .output.rendered table {
    width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 14px;
  }
  .output.rendered th, .output.rendered td {
    text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--border);
  }
  .output-toolbar {
    display: flex; justify-content: space-between; align-items: center;
    margin-top: 14px; margin-bottom: -4px;
  }
  .output-toolbar .meta { color: var(--muted); font-size: 12px; }
  .output-toolbar button.ghost {
    background: transparent; box-shadow: none; border: 1px solid var(--border);
    color: var(--muted); padding: 6px 12px; font-size: 12px; font-weight: 500;
  }
  .output-toolbar button.ghost:hover {
    transform: none; box-shadow: none; color: var(--text); border-color: var(--accent);
  }
  .tabs { display: flex; gap: 4px; margin-bottom: 14px; border-bottom: 1px solid var(--border); }
  .tab {
    padding: 10px 16px; cursor: pointer; color: var(--muted);
    border-bottom: 2px solid transparent; user-select: none;
  }
  .tab.active { color: var(--text); border-bottom-color: var(--accent); }
  .tab-content { display: none; }
  .tab-content.active { display: block; }
  table { width: 100%; border-collapse: collapse; font-size: 14px; }
  th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--border); }
  th { color: var(--muted); font-weight: 500; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
  td code {
    font-family: ui-monospace, Consolas, monospace; font-size: 13px;
    background: var(--panel-2); padding: 2px 6px; border-radius: 4px;
  }
  .method-get  { color: var(--good); font-weight: 600; }
  .method-post { color: var(--accent); font-weight: 600; }
  footer {
    text-align: center; color: var(--muted); font-size: 13px;
    padding: 32px 16px; border-top: 1px solid var(--border); margin-top: 40px;
  }
  footer a { color: var(--accent); text-decoration: none; }
  .warn-banner {
    background: rgba(255, 206, 92, 0.08); border: 1px solid rgba(255, 206, 92, 0.4);
    color: #ffe7a8; padding: 12px 16px; border-radius: 10px; margin: 18px 0;
    font-size: 14px;
  }
</style>
</head>
<body>
<header>
  <div class="brand"><div class="logo"></div><span>{{ app_name }}</span></div>
  <span class="pill">v{{ version }}</span>
</header>

<main>
  <h1>Code intelligence, served as an API.</h1>
  <p class="lede">{{ app_name }} is a Flask service that fronts OpenAI, Anthropic, and Google generative models behind a unified set of endpoints — analyze, generate, optimize, chat, and batch-process code.</p>

  <div class="status-row">
    <div class="status"><span class="dot {{ 'on' if providers.openai else 'off' }}"></span>OpenAI {{ 'configured' if providers.openai else 'no key' }}</div>
    <div class="status"><span class="dot {{ 'on' if providers.anthropic else 'off' }}"></span>Anthropic {{ 'configured' if providers.anthropic else 'no key' }}</div>
    <div class="status"><span class="dot {{ 'on' if providers.google else 'off' }}"></span>Google {{ 'configured' if providers.google else 'no key' }}</div>
  </div>

  {% if not (providers.openai or providers.anthropic or providers.google) %}
  <div class="warn-banner">
    No AI provider keys are configured. The interactive panels below will return errors until you add at least one key to <code>.env</code> and restart the server. The endpoints themselves still respond — they just can't reach an upstream model.
  </div>
  {% endif %}

  <section>
    <h2>Capabilities</h2>
    <div class="grid">
      <div class="card">
        <h3>Analyze</h3>
        <p>Static review of a code snippet — issues, smells, complexity, suggestions.</p>
        <span class="endpoint">POST /api/analyze</span>
      </div>
      <div class="card">
        <h3>Generate</h3>
        <p>Generate code from a natural-language prompt with your provider of choice.</p>
        <span class="endpoint">POST /api/generate</span>
      </div>
      <div class="card">
        <h3>Optimize</h3>
        <p>Rewrite code for performance, readability, and best practices, with rationale.</p>
        <span class="endpoint">POST /api/optimize</span>
      </div>
      <div class="card">
        <h3>Chat</h3>
        <p>Multi-turn conversation with system + user messages, provider-agnostic.</p>
        <span class="endpoint">POST /api/chat</span>
      </div>
      <div class="card">
        <h3>Batch</h3>
        <p>Analyze a list of snippets in one request — partial success is OK.</p>
        <span class="endpoint">POST /api/batch-analyze</span>
      </div>
      <div class="card">
        <h3>Health & Discovery</h3>
        <p>Service heartbeat plus a list of providers wired into the build.</p>
        <span class="endpoint">GET /health · /api/models</span>
      </div>
    </div>
  </section>

  <section>
    <h2>Playground</h2>
    <div class="panel">
      <div class="tabs">
        <div class="tab active" data-tab="chat">Chat</div>
        <div class="tab" data-tab="analyze">Analyze</div>
        <div class="tab" data-tab="generate">Generate</div>
      </div>

      <div class="tab-content active" data-tab="chat">
        <div class="row" style="margin-bottom: 12px;">
          <div style="flex: 1; min-width: 200px;">
            <label>Provider</label>
            <select id="chat-provider">
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="google">Google</option>
            </select>
          </div>
        </div>
        <label>Message</label>
        <textarea id="chat-input" placeholder="Ask anything... e.g. Explain Python decorators with one short example."></textarea>
        <div style="margin-top: 12px;"><button id="chat-send">Send</button></div>
        <div id="chat-output" class="output" style="display: none;"></div>
      </div>

      <div class="tab-content" data-tab="analyze">
        <div class="row" style="margin-bottom: 12px;">
          <div style="flex: 1; min-width: 200px;">
            <label>Provider</label>
            <select id="analyze-provider">
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="google">Google</option>
            </select>
          </div>
        </div>
        <label>Code to analyze</label>
        <textarea id="analyze-input" placeholder="def add(a, b):&#10;    return a + b"></textarea>
        <div style="margin-top: 12px;"><button id="analyze-send">Analyze</button></div>
        <div id="analyze-output" class="output" style="display: none;"></div>
      </div>

      <div class="tab-content" data-tab="generate">
        <div class="row" style="margin-bottom: 12px;">
          <div style="flex: 1; min-width: 200px;">
            <label>Provider</label>
            <select id="generate-provider">
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="google">Google</option>
            </select>
          </div>
        </div>
        <label>Prompt</label>
        <textarea id="generate-input" placeholder="Write a Python function that returns the nth Fibonacci number iteratively."></textarea>
        <div style="margin-top: 12px;"><button id="generate-send">Generate</button></div>
        <div id="generate-output" class="output" style="display: none;"></div>
      </div>
    </div>
  </section>

  <section>
    <h2>Endpoint reference</h2>
    <div class="panel" style="padding: 0; overflow: hidden;">
      <table>
        <thead><tr><th>Method</th><th>Path</th><th>Body</th><th>Description</th></tr></thead>
        <tbody>
          <tr><td class="method-get">GET</td><td><code>/health</code></td><td>—</td><td>Liveness probe</td></tr>
          <tr><td class="method-get">GET</td><td><code>/api/models</code></td><td>—</td><td>List configured providers</td></tr>
          <tr><td class="method-post">POST</td><td><code>/api/analyze</code></td><td><code>{ code, provider? }</code></td><td>Analyze a snippet</td></tr>
          <tr><td class="method-post">POST</td><td><code>/api/generate</code></td><td><code>{ prompt, provider? }</code></td><td>Generate code from a prompt</td></tr>
          <tr><td class="method-post">POST</td><td><code>/api/optimize</code></td><td><code>{ code, provider? }</code></td><td>Optimize a snippet</td></tr>
          <tr><td class="method-post">POST</td><td><code>/api/chat</code></td><td><code>{ messages, provider? }</code></td><td>Chat with the model</td></tr>
          <tr><td class="method-post">POST</td><td><code>/api/batch-analyze</code></td><td><code>{ codes[], provider? }</code></td><td>Batch analysis</td></tr>
        </tbody>
      </table>
    </div>
  </section>
</main>

<footer>
  {{ app_name }} · running in {{ environment }} mode · <a href="/health">/health</a> · <a href="/api/models">/api/models</a>
</footer>

<script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>
<script>
  if (window.marked && marked.setOptions) {
    marked.setOptions({ breaks: true, gfm: true });
  }

  document.querySelectorAll('.tab').forEach(t => {
    t.addEventListener('click', () => {
      const name = t.dataset.tab;
      document.querySelectorAll('.tab').forEach(x => x.classList.toggle('active', x === t));
      document.querySelectorAll('.tab-content').forEach(x =>
        x.classList.toggle('active', x.dataset.tab === name));
    });
  });

  function extractContent(parsed) {
    const d = parsed && parsed.data;
    if (!d) return null;
    return d.response ?? d.generated_code ?? d.optimized_code
        ?? (d.analysis && typeof d.analysis === 'string' ? d.analysis : null);
  }

  function makeToolbar(parsed, status, outputEl, content) {
    const toolbar = document.createElement('div');
    toolbar.className = 'output-toolbar';
    const meta = document.createElement('span');
    meta.className = 'meta';
    const provider = parsed && parsed.data && parsed.data.provider;
    meta.textContent = 'HTTP ' + status + (provider ? ' · ' + provider : '');
    const btn = document.createElement('button');
    btn.className = 'ghost';
    btn.textContent = 'Show raw JSON';
    let raw = false;
    btn.onclick = () => {
      raw = !raw;
      if (raw) {
        outputEl.classList.remove('rendered');
        outputEl.textContent = JSON.stringify(parsed, null, 2);
        outputEl.prepend(toolbar);
        btn.textContent = 'Show formatted';
      } else {
        outputEl.classList.add('rendered');
        outputEl.innerHTML = '';
        outputEl.appendChild(toolbar);
        const body = document.createElement('div');
        body.innerHTML = marked.parse(content);
        outputEl.appendChild(body);
        btn.textContent = 'Show raw JSON';
      }
    };
    toolbar.append(meta, btn);
    return toolbar;
  }

  async function callApi(path, body, outputEl, btn) {
    outputEl.style.display = 'block';
    outputEl.classList.remove('error', 'rendered');
    outputEl.innerHTML = '';
    outputEl.textContent = 'Calling ' + path + '...';
    btn.disabled = true;
    try {
      const r = await fetch(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const text = await r.text();
      let parsed = null;
      try { parsed = JSON.parse(text); } catch (_) {}

      if (r.ok && parsed && window.marked) {
        const content = extractContent(parsed);
        if (content) {
          outputEl.innerHTML = '';
          outputEl.classList.add('rendered');
          outputEl.appendChild(makeToolbar(parsed, r.status, outputEl, content));
          const md = document.createElement('div');
          md.innerHTML = marked.parse(content);
          outputEl.appendChild(md);
          return;
        }
      }

      const pretty = parsed ? JSON.stringify(parsed, null, 2) : text;
      outputEl.textContent = 'HTTP ' + r.status + '\n\n' + pretty;
      if (!r.ok) outputEl.classList.add('error');
    } catch (e) {
      outputEl.classList.add('error');
      outputEl.textContent = 'Network error: ' + e.message;
    } finally {
      btn.disabled = false;
    }
  }

  document.getElementById('chat-send').addEventListener('click', (e) => {
    const msg = document.getElementById('chat-input').value.trim();
    const provider = document.getElementById('chat-provider').value;
    if (!msg) return;
    callApi('/api/chat',
      { messages: [{ role: 'user', content: msg }], provider },
      document.getElementById('chat-output'), e.currentTarget);
  });

  document.getElementById('analyze-send').addEventListener('click', (e) => {
    const code = document.getElementById('analyze-input').value;
    const provider = document.getElementById('analyze-provider').value;
    if (!code.trim()) return;
    callApi('/api/analyze',
      { code, provider },
      document.getElementById('analyze-output'), e.currentTarget);
  });

  document.getElementById('generate-send').addEventListener('click', (e) => {
    const prompt = document.getElementById('generate-input').value.trim();
    const provider = document.getElementById('generate-provider').value;
    if (!prompt) return;
    callApi('/api/generate',
      { prompt, provider },
      document.getElementById('generate-output'), e.currentTarget);
  });
</script>
</body>
</html>
"""


@web_bp.route("/")
def index():
    providers = {
        "openai": _key_set(config.OPENAI_API_KEY),
        "anthropic": _key_set(config.ANTHROPIC_API_KEY),
        "google": _key_set(config.GOOGLE_API_KEY),
    }
    return render_template_string(
        INDEX_HTML,
        app_name=config.APP_NAME,
        version=config.APP_VERSION,
        environment=config.ENVIRONMENT,
        providers=providers,
    )
