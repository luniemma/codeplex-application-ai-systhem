"""
Web UI Blueprint - serves the homepage and interactive playground.
"""

from flask import Blueprint, render_template_string

from app.config import config

web_bp = Blueprint("web", __name__)


def _key_set(value: str) -> bool:
    return bool(value) and not value.startswith("your_")


INDEX_HTML = r"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{{ app_name }}</title>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0' x2='1' y1='0' y2='1'%3E%3Cstop offset='0' stop-color='%236b8cff'/%3E%3Cstop offset='1' stop-color='%238d6bff'/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width='32' height='32' rx='8' fill='url(%23g)'/%3E%3Cpath d='M11 11 L7 16 L11 21 M21 11 L25 16 L21 21' stroke='white' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round' fill='none'/%3E%3C/svg%3E" />
<style>
  /* ── Theme tokens ─────────────────────────────────────────────────── */
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
    --bg: #f5f7fb;
    --panel: #ffffff;
    --panel-2: #f0f3fa;
    --border: #d6dcec;
    --text: #1a2240;
    --muted: #5a6685;
    --accent: #4a6ef0;
    --accent-2: #7a4fea;
    --good: #1aa56b;
    --bad: #d83a3a;
    --warn: #c98b00;
    --code-bg: #f0f3fa;
    --hero-glow-1: #d8e0fc;
    --hero-glow-2: #e6daff;
  }

  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: radial-gradient(1200px 600px at 10% -10%, var(--hero-glow-1) 0%, transparent 60%),
                radial-gradient(900px 500px at 100% 0%, var(--hero-glow-2) 0%, transparent 60%),
                var(--bg);
    color: var(--text);
    min-height: 100vh;
    line-height: 1.5;
    transition: background-color 0.2s, color 0.2s;
  }

  /* ── Header / brand ───────────────────────────────────────────────── */
  header {
    padding: 22px 32px;
    display: flex; align-items: center; justify-content: space-between;
    border-bottom: 1px solid var(--border);
    backdrop-filter: blur(8px);
  }
  .brand { display: flex; align-items: center; gap: 12px; font-weight: 700; font-size: 20px; letter-spacing: 0.3px; }
  .brand svg { width: 36px; height: 36px; border-radius: 8px;
    box-shadow: 0 6px 24px rgba(107, 140, 255, 0.35); flex-shrink: 0; }
  .brand-name { background: linear-gradient(135deg, var(--text), var(--muted));
    -webkit-background-clip: text; background-clip: text; color: transparent; }
  .header-right { display: flex; gap: 10px; align-items: center; }
  .pill { font-size: 12px; padding: 4px 10px; border-radius: 999px;
    background: rgba(107, 140, 255, 0.15); border: 1px solid rgba(107, 140, 255, 0.4);
    color: var(--accent); }
  .icon-btn {
    background: transparent; border: 1px solid var(--border); color: var(--muted);
    border-radius: 10px; width: 36px; height: 36px; padding: 0;
    display: inline-flex; align-items: center; justify-content: center;
    cursor: pointer; transition: color 0.15s, border-color 0.15s, background 0.15s;
  }
  .icon-btn:hover { color: var(--text); border-color: var(--accent); }
  .icon-btn svg { width: 18px; height: 18px; }

  main { max-width: 1100px; margin: 0 auto; padding: 32px; }

  /* ── Hero ──────────────────────────────────────────────────────────── */
  .hero { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 28px; align-items: center; margin-top: 8px; }
  @media (max-width: 760px) { .hero { grid-template-columns: 1fr; } .hero-art { order: -1; max-width: 320px; margin: 0 auto; } }
  h1 { font-size: 40px; line-height: 1.1; margin: 16px 0 8px;
    background: linear-gradient(135deg, var(--text), var(--muted));
    -webkit-background-clip: text; background-clip: text; color: transparent; }
  .lede { color: var(--muted); font-size: 17px; max-width: 720px; }
  .hero-art { width: 320px; height: 200px; }
  .hero-art .pulse { animation: pulse 2.4s ease-in-out infinite; transform-origin: center; }
  .hero-art .flow-1 { animation: flow 3s linear infinite; }
  .hero-art .flow-2 { animation: flow 3s linear infinite; animation-delay: 1s; }
  .hero-art .flow-3 { animation: flow 3s linear infinite; animation-delay: 2s; }
  @keyframes pulse { 0%, 100% { opacity: 0.85; transform: scale(1); } 50% { opacity: 1; transform: scale(1.05); } }
  @keyframes flow { 0% { stroke-dashoffset: 60; opacity: 0; } 20% { opacity: 1; } 100% { stroke-dashoffset: 0; opacity: 0; } }

  /* ── Status row with provider mini-logos ─────────────────────────── */
  .status-row { display: flex; flex-wrap: wrap; gap: 10px; margin: 18px 0 0; }
  .status {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 14px 8px 10px; border-radius: 999px; font-size: 13px;
    border: 1px solid var(--border); background: var(--panel);
  }
  .status .plogo { width: 18px; height: 18px; border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    color: white; font-size: 10px; font-weight: 700; flex-shrink: 0; }
  .status .plogo.openai    { background: #0db66e; }
  .status .plogo.anthropic { background: #d97757; }
  .status .plogo.google    { background: #4285f4; }
  .status .plogo svg { width: 12px; height: 12px; }
  .status .state { display: flex; align-items: center; gap: 6px; color: var(--muted); }
  .status .state .dot { width: 6px; height: 6px; border-radius: 50%; }
  .status .state .dot.on  { background: var(--good); box-shadow: 0 0 8px var(--good); }
  .status .state .dot.off { background: var(--bad); }

  /* ── Cards / sections ─────────────────────────────────────────────── */
  .grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); margin: 28px 0; }
  .card { background: var(--panel); border: 1px solid var(--border); border-radius: 14px; padding: 18px 20px; }
  .card h3 { margin: 0 0 6px; font-size: 16px; }
  .card p { margin: 0; color: var(--muted); font-size: 14px; }
  .card .endpoint { font-family: ui-monospace, "JetBrains Mono", Consolas, monospace;
    font-size: 12px; color: var(--accent);
    background: var(--panel-2); border: 1px solid var(--border);
    padding: 4px 8px; border-radius: 6px; display: inline-block; margin-top: 10px; }

  section { margin: 36px 0; }
  section h2 { font-size: 22px; margin: 0 0 14px; }
  .panel { background: var(--panel); border: 1px solid var(--border); border-radius: 14px; padding: 20px; }
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

  /* ── Output / rendered markdown ──────────────────────────────────── */
  .output {
    margin-top: 14px; padding: 14px; background: var(--code-bg); border: 1px solid var(--border);
    border-radius: 10px; font-family: ui-monospace, Consolas, monospace;
    font-size: 13px; white-space: pre-wrap; word-wrap: break-word;
    max-height: 460px; overflow: auto; color: var(--text);
  }
  .output.error { border-color: rgba(255, 107, 107, 0.5); color: #ffd3d3; }
  .output.rendered {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 15px; line-height: 1.65; white-space: normal;
  }
  .output.rendered h1, .output.rendered h2, .output.rendered h3, .output.rendered h4 {
    margin: 20px 0 8px; line-height: 1.3; color: var(--text);
  }
  .output.rendered h1 { font-size: 22px; }
  .output.rendered h2 { font-size: 18px; padding-bottom: 6px; border-bottom: 1px solid var(--border); }
  .output.rendered h3 { font-size: 16px; }
  .output.rendered h4 { font-size: 14px; color: var(--muted); }
  .output.rendered p { margin: 10px 0; }
  .output.rendered ul, .output.rendered ol { margin: 10px 0; padding-left: 22px; }
  .output.rendered li { margin: 4px 0; }
  .output.rendered strong { color: var(--text); }
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
    background: var(--code-bg); border: 1px solid var(--border); border-radius: 10px;
    padding: 14px 16px; padding-top: 36px;     /* room for the copy button */
    overflow-x: auto; margin: 12px 0; position: relative;
  }
  .output.rendered pre code { background: transparent; border: 0; padding: 0; font-size: 13px; line-height: 1.55; }
  .output.rendered pre .copy-btn {
    position: absolute; top: 8px; right: 8px;
    background: var(--panel-2); color: var(--muted); border: 1px solid var(--border);
    border-radius: 6px; padding: 4px 10px; font-size: 11px; font-weight: 500;
    cursor: pointer; box-shadow: none; transition: all 0.15s;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }
  .output.rendered pre .copy-btn:hover { color: var(--text); border-color: var(--accent); transform: none; box-shadow: none; }
  .output.rendered pre .copy-btn.ok { color: var(--good); border-color: var(--good); }
  .output.rendered table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 14px; }
  .output.rendered th, .output.rendered td { text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--border); }

  .output-toolbar { display: flex; justify-content: space-between; align-items: center; margin-top: 14px; margin-bottom: -4px; }
  .output-toolbar .meta { color: var(--muted); font-size: 12px; }
  .output-toolbar button.ghost {
    background: transparent; box-shadow: none; border: 1px solid var(--border);
    color: var(--muted); padding: 6px 12px; font-size: 12px; font-weight: 500;
  }
  .output-toolbar button.ghost:hover { transform: none; box-shadow: none; color: var(--text); border-color: var(--accent); }

  /* ── Tabs ─────────────────────────────────────────────────────────── */
  .tabs { display: flex; gap: 4px; margin-bottom: 14px; border-bottom: 1px solid var(--border); }
  .tab {
    padding: 10px 16px; cursor: pointer; color: var(--muted);
    border-bottom: 2px solid transparent; user-select: none;
    display: inline-flex; align-items: center; gap: 8px;
  }
  .tab.active { color: var(--text); border-bottom-color: var(--accent); }
  .tab kbd {
    font-family: ui-monospace, Consolas, monospace; font-size: 10px;
    border: 1px solid var(--border); border-radius: 4px; padding: 1px 5px;
    color: var(--muted); background: var(--panel-2);
  }
  .tab-content { display: none; }
  .tab-content.active { display: block; }

  /* ── Example-prompt chips ─────────────────────────────────────────── */
  .examples { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0 12px; }
  .examples-label { color: var(--muted); font-size: 12px; align-self: center; margin-right: 4px; }
  .chip {
    font-size: 12px; padding: 5px 10px; border-radius: 999px;
    background: var(--panel-2); border: 1px solid var(--border); color: var(--muted);
    cursor: pointer; transition: all 0.15s;
  }
  .chip:hover { color: var(--text); border-color: var(--accent); background: rgba(107, 140, 255, 0.08); }

  /* ── Input footer (token count + history) ────────────────────────── */
  .input-footer {
    display: flex; justify-content: space-between; align-items: center;
    margin-top: 6px; font-size: 11px; color: var(--muted);
  }
  .input-footer .tokens { font-family: ui-monospace, Consolas, monospace; }
  .input-footer .history-wrap { position: relative; }
  .history-btn {
    background: transparent; box-shadow: none; border: 1px solid var(--border);
    color: var(--muted); padding: 4px 10px; font-size: 11px; font-weight: 500;
    border-radius: 6px;
  }
  .history-btn:hover { transform: none; box-shadow: none; color: var(--text); border-color: var(--accent); }
  .history-menu {
    position: absolute; bottom: calc(100% + 6px); right: 0;
    background: var(--panel); border: 1px solid var(--border); border-radius: 10px;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.45);
    width: 320px; max-height: 280px; overflow-y: auto; padding: 6px; z-index: 50;
  }
  .history-menu .empty { color: var(--muted); padding: 12px; font-size: 12px; text-align: center; }
  .history-menu .item {
    display: block; width: 100%; text-align: left; padding: 8px 10px;
    border-radius: 6px; color: var(--text); font-size: 12px; cursor: pointer;
    background: transparent; border: 0; box-shadow: none;
    line-height: 1.4; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    font-family: ui-monospace, Consolas, monospace;
  }
  .history-menu .item:hover { background: var(--panel-2); transform: none; box-shadow: none; }
  .history-menu .clear {
    margin-top: 4px; border-top: 1px solid var(--border); padding-top: 6px;
    color: var(--bad); font-size: 11px;
  }

  /* ── Endpoint reference table ─────────────────────────────────────── */
  table { width: 100%; border-collapse: collapse; font-size: 14px; }
  th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--border); }
  th { color: var(--muted); font-weight: 500; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
  td code { font-family: ui-monospace, Consolas, monospace; font-size: 13px;
    background: var(--panel-2); padding: 2px 6px; border-radius: 4px; }
  .method-get  { color: var(--good); font-weight: 600; }
  .method-post { color: var(--accent); font-weight: 600; }

  footer {
    text-align: center; color: var(--muted); font-size: 13px;
    padding: 32px 16px; border-top: 1px solid var(--border); margin-top: 40px;
  }
  footer a { color: var(--accent); text-decoration: none; }
  footer .shortcuts { margin-top: 6px; font-size: 11px; }
  footer .shortcuts kbd {
    font-family: ui-monospace, Consolas, monospace; border: 1px solid var(--border);
    border-radius: 4px; padding: 1px 5px; background: var(--panel-2); color: var(--text);
  }

  .warn-banner {
    background: rgba(255, 206, 92, 0.08); border: 1px solid rgba(255, 206, 92, 0.4);
    color: var(--warn); padding: 12px 16px; border-radius: 10px; margin: 18px 0; font-size: 14px;
  }
</style>
</head>
<body>
<header>
  <div class="brand">
    <!-- Codeplex logo: gradient rounded square with stylized < > brackets -->
    <svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg" aria-label="{{ app_name }} logo">
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
    <span class="brand-name">{{ app_name }}</span>
  </div>
  <div class="header-right">
    <span class="pill">v{{ version }}</span>
    <button id="theme-toggle" class="icon-btn" title="Toggle theme (dark/light)" aria-label="Toggle theme">
      <!-- moon icon shown in dark mode, sun shown in light — flipped in JS via data-theme -->
      <svg id="theme-icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
      <svg id="theme-icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:none"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>
    </button>
  </div>
</header>

<main>
  <div class="hero">
    <div>
      <h1>Code intelligence, served as an API.</h1>
      <p class="lede">{{ app_name }} is a Flask service that fronts OpenAI, Anthropic, and Google generative models behind a unified set of endpoints — analyze, generate, optimize, chat, and batch-process code.</p>
    </div>
    <!-- Hero illustration: code → model → output, with animated flow -->
    <svg class="hero-art" viewBox="0 0 320 200" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <defs>
        <linearGradient id="hero-grad" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stop-color="#6b8cff" stop-opacity="0.0"/>
          <stop offset="50%" stop-color="#6b8cff" stop-opacity="1"/>
          <stop offset="100%" stop-color="#8d6bff" stop-opacity="0.0"/>
        </linearGradient>
        <radialGradient id="hero-core" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0%" stop-color="#a8b9ff"/>
          <stop offset="100%" stop-color="#6b8cff"/>
        </radialGradient>
      </defs>
      <!-- left: code block -->
      <g transform="translate(20,40)">
        <rect width="80" height="120" rx="10" fill="var(--panel)" stroke="var(--border)"/>
        <rect x="10" y="14" width="50" height="6" rx="3" fill="#6b8cff" opacity="0.7"/>
        <rect x="10" y="28" width="40" height="6" rx="3" fill="var(--muted)" opacity="0.5"/>
        <rect x="20" y="42" width="50" height="6" rx="3" fill="var(--muted)" opacity="0.4"/>
        <rect x="20" y="56" width="35" height="6" rx="3" fill="var(--muted)" opacity="0.4"/>
        <rect x="10" y="70" width="55" height="6" rx="3" fill="#8d6bff" opacity="0.6"/>
        <rect x="10" y="84" width="35" height="6" rx="3" fill="var(--muted)" opacity="0.4"/>
        <rect x="10" y="98" width="60" height="6" rx="3" fill="var(--muted)" opacity="0.5"/>
      </g>
      <!-- middle: AI core -->
      <g class="pulse" transform="translate(160,100)">
        <circle r="32" fill="url(#hero-core)" opacity="0.25"/>
        <circle r="20" fill="url(#hero-core)" opacity="0.5"/>
        <circle r="10" fill="#a8b9ff"/>
      </g>
      <!-- flow lines (animated) -->
      <g fill="none" stroke="url(#hero-grad)" stroke-width="2" stroke-linecap="round" stroke-dasharray="4 6">
        <path class="flow-1" d="M105 70 C 130 70, 140 95, 158 95"/>
        <path class="flow-2" d="M105 100 C 130 100, 140 105, 158 105"/>
        <path class="flow-3" d="M105 130 C 130 130, 140 115, 158 115"/>
      </g>
      <!-- right: response block -->
      <g transform="translate(220,40)">
        <rect width="80" height="120" rx="10" fill="var(--panel)" stroke="var(--border)"/>
        <rect x="10" y="14" width="60" height="6" rx="3" fill="#3ddc97" opacity="0.7"/>
        <rect x="10" y="28" width="55" height="6" rx="3" fill="var(--muted)" opacity="0.5"/>
        <rect x="10" y="42" width="40" height="6" rx="3" fill="var(--muted)" opacity="0.4"/>
        <rect x="10" y="56" width="50" height="6" rx="3" fill="var(--muted)" opacity="0.4"/>
        <rect x="10" y="70" width="60" height="6" rx="3" fill="#3ddc97" opacity="0.5"/>
        <rect x="10" y="84" width="45" height="6" rx="3" fill="var(--muted)" opacity="0.4"/>
        <rect x="10" y="98" width="55" height="6" rx="3" fill="var(--muted)" opacity="0.5"/>
      </g>
    </svg>
  </div>

  <div class="status-row">
    <div class="status">
      <span class="plogo openai">O</span>
      <span>OpenAI</span>
      <span class="state"><span class="dot {{ 'on' if providers.openai else 'off' }}"></span>{{ 'configured' if providers.openai else 'no key' }}</span>
    </div>
    <div class="status">
      <span class="plogo anthropic">A</span>
      <span>Anthropic</span>
      <span class="state"><span class="dot {{ 'on' if providers.anthropic else 'off' }}"></span>{{ 'configured' if providers.anthropic else 'no key' }}</span>
    </div>
    <div class="status">
      <span class="plogo google">G</span>
      <span>Google</span>
      <span class="state"><span class="dot {{ 'on' if providers.google else 'off' }}"></span>{{ 'configured' if providers.google else 'no key' }}</span>
    </div>
  </div>

  {% if not (providers.openai or providers.anthropic or providers.google) %}
  <div class="warn-banner">
    No AI provider keys are configured. The interactive panels below will return errors until you add at least one key to <code>.env</code> and restart the server. The endpoints themselves still respond — they just can't reach an upstream model.
  </div>
  {% endif %}

  <section>
    <h2>Capabilities</h2>
    <div class="grid">
      <div class="card"><h3>Analyze</h3><p>Static review of a code snippet — issues, smells, complexity, suggestions.</p><span class="endpoint">POST /api/analyze</span></div>
      <div class="card"><h3>Generate</h3><p>Generate code from a natural-language prompt with your provider of choice.</p><span class="endpoint">POST /api/generate</span></div>
      <div class="card"><h3>Optimize</h3><p>Rewrite code for performance, readability, and best practices, with rationale.</p><span class="endpoint">POST /api/optimize</span></div>
      <div class="card"><h3>Chat</h3><p>Multi-turn conversation with system + user messages, provider-agnostic.</p><span class="endpoint">POST /api/chat</span></div>
      <div class="card"><h3>Batch</h3><p>Analyze a list of snippets in one request — partial success is OK.</p><span class="endpoint">POST /api/batch-analyze</span></div>
      <div class="card"><h3>Health & Discovery</h3><p>Service heartbeat plus a list of providers wired into the build.</p><span class="endpoint">GET /health · /api/models</span></div>
    </div>
  </section>

  <section>
    <h2>Playground</h2>
    <div class="panel">
      <div class="tabs">
        <div class="tab active" data-tab="chat">Chat <kbd>1</kbd></div>
        <div class="tab" data-tab="analyze">Analyze <kbd>2</kbd></div>
        <div class="tab" data-tab="generate">Generate <kbd>3</kbd></div>
      </div>

      {# render each tab from a small server-side dict so the JS hooks line up #}
      {% for tab in tabs %}
      <div class="tab-content {{ 'active' if loop.first else '' }}" data-tab="{{ tab.id }}">
        <div class="row" style="margin-bottom: 12px;">
          <div style="flex: 1; min-width: 200px;">
            <label>Provider</label>
            <select id="{{ tab.id }}-provider">
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="google">Google</option>
            </select>
          </div>
          {% if tab.id == 'chat' %}
          <div style="display: flex; align-items: flex-end; gap: 8px; padding-bottom: 4px;">
            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; margin: 0;">
              <input type="checkbox" id="chat-stream" style="width: auto; cursor: pointer;" checked />
              <span style="color: var(--text); font-size: 13px;">Stream</span>
            </label>
          </div>
          {% endif %}
        </div>

        <div class="examples">
          <span class="examples-label">examples:</span>
          {% for ex in tab.examples %}
          <button type="button" class="chip" data-target="{{ tab.id }}-input" data-fill="{{ ex.fill | e }}">{{ ex.label }}</button>
          {% endfor %}
        </div>

        <label>{{ tab.input_label }}</label>
        <textarea id="{{ tab.id }}-input" placeholder="{{ tab.placeholder }}"></textarea>

        <div class="input-footer">
          <span class="tokens" id="{{ tab.id }}-tokens">0 chars · ~0 tokens</span>
          <span class="history-wrap">
            <button type="button" class="history-btn" data-tab-id="{{ tab.id }}">History ▾</button>
            <div class="history-menu" id="{{ tab.id }}-history" style="display: none;"></div>
          </span>
        </div>

        <div style="margin-top: 12px;"><button id="{{ tab.id }}-send">{{ tab.send_label }}</button></div>
        <div id="{{ tab.id }}-output" class="output" style="display: none;"></div>
      </div>
      {% endfor %}
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
  {{ app_name }} · running in {{ environment }} mode · <a href="/health">/health</a> · <a href="/api/models">/api/models</a> · <a href="/metrics">/metrics</a>
  <div class="shortcuts">
    Shortcuts:
    <kbd>1</kbd> <kbd>2</kbd> <kbd>3</kbd> switch tabs ·
    <kbd>Ctrl</kbd>+<kbd>K</kbd> focus input ·
    <kbd>Ctrl</kbd>+<kbd>Enter</kbd> send
  </div>
</footer>

<script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>
<script>
(() => {
  if (window.marked && marked.setOptions) marked.setOptions({ breaks: true, gfm: true });

  // ── Theme toggle ────────────────────────────────────────────────────
  const root = document.documentElement;
  const moon = document.getElementById('theme-icon-moon');
  const sun  = document.getElementById('theme-icon-sun');
  function applyTheme(t) {
    root.setAttribute('data-theme', t);
    moon.style.display = t === 'dark' ? '' : 'none';
    sun.style.display  = t === 'dark' ? 'none' : '';
  }
  applyTheme(localStorage.getItem('theme') || 'dark');
  document.getElementById('theme-toggle').addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    localStorage.setItem('theme', next);
    applyTheme(next);
  });

  // ── Tabs ────────────────────────────────────────────────────────────
  function activateTab(name) {
    document.querySelectorAll('.tab').forEach(x => x.classList.toggle('active', x.dataset.tab === name));
    document.querySelectorAll('.tab-content').forEach(x => x.classList.toggle('active', x.dataset.tab === name));
  }
  document.querySelectorAll('.tab').forEach(t => {
    t.addEventListener('click', () => activateTab(t.dataset.tab));
  });

  // ── Token counter (rough: 1 token ≈ 4 chars) ───────────────────────
  const TABS = ['chat', 'analyze', 'generate'];
  TABS.forEach(id => {
    const ta = document.getElementById(id + '-input');
    const lbl = document.getElementById(id + '-tokens');
    const update = () => {
      const c = ta.value.length;
      lbl.textContent = `${c.toLocaleString()} chars · ~${Math.ceil(c / 4).toLocaleString()} tokens`;
    };
    ta.addEventListener('input', update);
    update();
  });

  // ── Example-prompt chips ───────────────────────────────────────────
  document.querySelectorAll('.chip[data-target]').forEach(chip => {
    chip.addEventListener('click', () => {
      const ta = document.getElementById(chip.dataset.target);
      ta.value = chip.dataset.fill;
      ta.dispatchEvent(new Event('input'));
      ta.focus();
    });
  });

  // ── Local prompt history ───────────────────────────────────────────
  const HISTORY_KEY = (id) => `cdp-history-${id}`;
  const HISTORY_MAX = 20;
  function getHistory(id) {
    try { return JSON.parse(localStorage.getItem(HISTORY_KEY(id)) || '[]'); }
    catch (_) { return []; }
  }
  function pushHistory(id, value) {
    const v = (value || '').trim();
    if (!v) return;
    const list = getHistory(id).filter(x => x !== v);
    list.unshift(v);
    localStorage.setItem(HISTORY_KEY(id), JSON.stringify(list.slice(0, HISTORY_MAX)));
  }
  function clearHistory(id) { localStorage.removeItem(HISTORY_KEY(id)); }
  function renderHistory(id) {
    const menu = document.getElementById(id + '-history');
    const items = getHistory(id);
    menu.innerHTML = '';
    if (!items.length) {
      const empty = document.createElement('div');
      empty.className = 'empty';
      empty.textContent = 'no recent prompts';
      menu.appendChild(empty);
      return;
    }
    items.forEach(p => {
      const btn = document.createElement('button');
      btn.className = 'item';
      btn.title = p;
      btn.textContent = p.slice(0, 80);
      btn.onclick = () => {
        const ta = document.getElementById(id + '-input');
        ta.value = p;
        ta.dispatchEvent(new Event('input'));
        ta.focus();
        menu.style.display = 'none';
      };
      menu.appendChild(btn);
    });
    const clr = document.createElement('button');
    clr.className = 'item clear';
    clr.textContent = 'clear history';
    clr.onclick = () => { clearHistory(id); renderHistory(id); };
    menu.appendChild(clr);
  }
  document.querySelectorAll('.history-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const id = btn.dataset.tabId;
      const menu = document.getElementById(id + '-history');
      const opening = menu.style.display === 'none';
      // close all menus first
      document.querySelectorAll('.history-menu').forEach(m => m.style.display = 'none');
      if (opening) { renderHistory(id); menu.style.display = 'block'; }
    });
  });
  document.addEventListener('click', () => {
    document.querySelectorAll('.history-menu').forEach(m => m.style.display = 'none');
  });

  // ── Output rendering helpers ───────────────────────────────────────
  function extractContent(parsed) {
    const d = parsed && parsed.data;
    if (!d) return null;
    return d.response ?? d.generated_code ?? d.optimized_code
        ?? (d.analysis && typeof d.analysis === 'string' ? d.analysis : null);
  }

  function attachCopyButtons(container) {
    container.querySelectorAll('pre').forEach(pre => {
      if (pre.querySelector('.copy-btn')) return;
      const btn = document.createElement('button');
      btn.className = 'copy-btn';
      btn.textContent = 'Copy';
      btn.onclick = (ev) => {
        ev.stopPropagation();
        const code = pre.querySelector('code');
        const text = code ? code.innerText : pre.innerText;
        const done = () => {
          btn.textContent = 'Copied'; btn.classList.add('ok');
          setTimeout(() => { btn.textContent = 'Copy'; btn.classList.remove('ok'); }, 1400);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(done, () => fallback(text, done));
        } else {
          fallback(text, done);
        }
      };
      pre.appendChild(btn);
    });
  }
  function fallback(text, onDone) {
    const ta = document.createElement('textarea');
    ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    try { document.execCommand('copy'); onDone(); } catch (_) {}
    document.body.removeChild(ta);
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
        attachCopyButtons(body);
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
          attachCopyButtons(md);
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

  // ── Streaming chat (SSE consumer) ──────────────────────────────────
  async function callApiStream(path, body, outputEl, btn) {
    outputEl.style.display = 'block';
    outputEl.classList.remove('error', 'rendered');
    outputEl.innerHTML = '';
    btn.disabled = true;

    // Set up the rendered surface up-front so we can append into it as
    // chunks arrive instead of waiting for the whole response.
    outputEl.classList.add('rendered');
    const meta = document.createElement('div');
    meta.className = 'output-toolbar';
    const metaText = document.createElement('span');
    metaText.className = 'meta';
    metaText.textContent = 'streaming...';
    meta.appendChild(metaText);
    outputEl.appendChild(meta);
    const md = document.createElement('div');
    outputEl.appendChild(md);

    let acc = '';
    try {
      const r = await fetch(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!r.ok || !r.body) {
        const text = await r.text();
        outputEl.classList.add('error');
        md.textContent = 'HTTP ' + r.status + '\n\n' + text;
        return;
      }
      const reader = r.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let chunks = 0;
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split('\n\n');
        buffer = events.pop();   // last (possibly partial) event stays in buffer
        for (const ev of events) {
          const line = ev.trim();
          if (!line.startsWith('data:')) continue;
          const payload = line.slice(5).trim();
          if (payload === '[DONE]') { metaText.textContent = `done · ${chunks} chunks`; break; }
          try {
            const obj = JSON.parse(payload);
            if (obj.error) { outputEl.classList.add('error'); md.textContent = obj.error; return; }
            if (obj.chunk) { acc += obj.chunk; chunks++; md.innerHTML = window.marked ? marked.parse(acc) : acc; }
          } catch (_) { /* ignore parse errors on partial frames */ }
        }
      }
      // After the stream ends, re-attach copy buttons in case the markdown
      // grew code blocks during streaming.
      attachCopyButtons(md);
    } catch (e) {
      outputEl.classList.add('error');
      md.textContent = 'Network error: ' + e.message;
    } finally {
      btn.disabled = false;
    }
  }

  // ── Per-tab send handlers ──────────────────────────────────────────
  function send(tab) {
    const value = document.getElementById(tab + '-input').value;
    const provider = document.getElementById(tab + '-provider').value;
    if (!value.trim()) return;
    const out = document.getElementById(tab + '-output');
    const btn = document.getElementById(tab + '-send');
    pushHistory(tab, value);
    if (tab === 'chat') {
      const streaming = document.getElementById('chat-stream') && document.getElementById('chat-stream').checked;
      const path = streaming ? '/api/chat/stream' : '/api/chat';
      const body = { messages: [{ role: 'user', content: value }], provider };
      if (streaming) callApiStream(path, body, out, btn);
      else           callApi(path, body, out, btn);
    } else if (tab === 'analyze') {
      callApi('/api/analyze', { code: value, provider }, out, btn);
    } else if (tab === 'generate') {
      callApi('/api/generate', { prompt: value, provider }, out, btn);
    }
  }
  TABS.forEach(t => {
    document.getElementById(t + '-send').addEventListener('click', () => send(t));
  });

  // ── Keyboard shortcuts ─────────────────────────────────────────────
  document.addEventListener('keydown', (e) => {
    const tag = (e.target.tagName || '').toLowerCase();
    const inField = ['textarea', 'input', 'select'].includes(tag);

    // Ctrl/Cmd+K: focus active tab's textarea
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      const active = document.querySelector('.tab.active');
      if (active) document.getElementById(active.dataset.tab + '-input').focus();
      return;
    }

    // Ctrl/Cmd+Enter: send the active tab
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      const active = document.querySelector('.tab.active');
      if (active) send(active.dataset.tab);
      return;
    }

    // 1/2/3: switch tabs (only when not typing)
    if (!inField && ['1', '2', '3'].includes(e.key)) {
      activateTab(TABS[parseInt(e.key, 10) - 1]);
    }
  });
})();
</script>
</body>
</html>
"""


# Tab-specific config — keeps the example-prompt list out of the template so
# it's easy to tweak without scrolling through ~700 lines of HTML.
TAB_CONFIG = [
    {
        "id": "chat",
        "input_label": "Message",
        "send_label": "Send",
        "placeholder": "Ask anything... e.g. Explain Python decorators with one short example.",
        "examples": [
            {
                "label": "Explain decorators",
                "fill": "Explain Python decorators with a small example.",
            },
            {
                "label": "When to use async",
                "fill": "When should I use async/await in Python? Trade-offs?",
            },
            {
                "label": "GIL impact",
                "fill": "How does the Python GIL affect multi-threaded performance?",
            },
            {
                "label": "Pick a DB",
                "fill": "I have a write-heavy workload of ~5k inserts/sec. Postgres or DynamoDB?",
            },
        ],
    },
    {
        "id": "analyze",
        "input_label": "Code to analyze",
        "send_label": "Analyze",
        "placeholder": "def add(a, b):\n    return a + b",
        "examples": [
            {
                "label": "Mutable default arg",
                "fill": "def append_to(item, target=[]):\n    target.append(item)\n    return target",
            },
            {
                "label": "N+1 query",
                "fill": "users = User.query.all()\nfor u in users:\n    print(u.posts.count())",
            },
            {
                "label": "Race condition",
                "fill": "balance = 100\ndef withdraw(amount):\n    global balance\n    if balance >= amount:\n        balance -= amount\n        return True\n    return False",
            },
        ],
    },
    {
        "id": "generate",
        "input_label": "Prompt",
        "send_label": "Generate",
        "placeholder": "Write a Python function that returns the nth Fibonacci number iteratively.",
        "examples": [
            {
                "label": "Fibonacci (iterative)",
                "fill": "Write a Python function that returns the nth Fibonacci number iteratively.",
            },
            {
                "label": "Retry decorator",
                "fill": "Write a Python decorator that retries a function up to N times on exceptions, with exponential backoff.",
            },
            {
                "label": "Rate limiter",
                "fill": "Implement a token bucket rate limiter in Python with a clean class API.",
            },
            {
                "label": "LRU cache",
                "fill": "Implement a simple LRU cache class in Python without using functools.lru_cache.",
            },
        ],
    },
]


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
        tabs=TAB_CONFIG,
    )
