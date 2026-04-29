# Codeplex AI

A Flask service that fronts OpenAI, Anthropic, and Google Gemini behind a unified set of endpoints — analyze, generate, optimize, chat, and batch-process code — plus a built-in interactive web playground.

## What you get

- **Unified API** over three providers (OpenAI / Anthropic / Google), pick per request via `provider`
- **Web playground** at `/` — pick a tab, type a prompt, get markdown-rendered responses (no Postman needed)
- **Live provider status** — green/red pills tell you which keys are configured before you hit Send
- **Helpful errors** — missing keys, deprecated models, and upstream failures are surfaced with the actual cause
- **Sensible defaults** — SQLite for local DB, in-memory cache fallback if Redis is unreachable

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET    | `/`                  | Web playground |
| GET    | `/health`            | Liveness probe |
| GET    | `/api/models`        | List configured providers |
| POST   | `/api/analyze`       | Analyze a code snippet |
| POST   | `/api/generate`      | Generate code from a prompt |
| POST   | `/api/optimize`      | Optimize a code snippet |
| POST   | `/api/chat`          | Multi-turn chat |
| POST   | `/api/batch-analyze` | Analyze a list of snippets |

All POST endpoints accept JSON with an optional `provider` field (`openai` | `anthropic` | `google`).

## Quick start

### Prerequisites
- **Python 3.11** (3.12+ is not supported — some dependencies don't have wheels for it yet)
- A Google AI Studio key (free tier, easiest to get) — https://aistudio.google.com/app/apikey
  - Or an Anthropic / OpenAI key if you prefer those providers

### Windows (PowerShell)

```powershell
git clone https://github.com/luniemma/codeplex-application-ai-systhem.git
cd codeplex-application-ai-systhem

# Create venv and install deps
python -m venv venv
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and replace the placeholder API keys with real ones

# Run
$env:PYTHONUTF8 = "1"
.\venv\Scripts\python.exe main.py
```

Open http://127.0.0.1:8000/ in your browser.

### macOS / Linux

```bash
git clone https://github.com/luniemma/codeplex-application-ai-systhem.git
cd codeplex-application-ai-systhem

python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

cp .env.example .env
# Edit .env and replace the placeholder API keys with real ones

python main.py
```

## Configuration

All config is read from `.env` at startup (see `.env.example` for the full template). The keys that matter:

| Variable | Default | Notes |
|----------|---------|-------|
| `OPENAI_API_KEY`     | — | Get from https://platform.openai.com/api-keys (paid only) |
| `ANTHROPIC_API_KEY`  | — | Get from https://console.anthropic.com/ |
| `GOOGLE_API_KEY`     | — | Get from https://aistudio.google.com/app/apikey (free tier available) |
| `OPENAI_MODEL`       | `gpt-4` | Set to `gpt-3.5-turbo` if you don't have GPT-4 access |
| `ANTHROPIC_MODEL`    | `claude-3-opus` | |
| `GOOGLE_MODEL`       | `gemini-pro` | **Deprecated** — set to `gemini-2.5-flash` (or `gemini-1.5-flash`) |
| `API_HOST`           | `0.0.0.0` | Use `127.0.0.1` for local-only |
| `API_PORT`           | `8000` | |
| `DEBUG`              | `False` | |
| `DATABASE_URL`       | `sqlite:///./codeplex.db` | |
| `REDIS_URL`          | `redis://localhost:6379/0` | Optional; cache falls back to in-memory |

## Docker

```bash
docker build -t codeplex-ai .
docker run -p 8000:8000 --env-file .env codeplex-ai
```

Or with the bundled compose file:

```bash
docker-compose up
```

## Testing

```bash
pytest tests/
pytest tests/ --cov=app
```

## Example: hitting the API directly

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"provider":"google","messages":[{"role":"user","content":"Reply with: PONG"}]}'
```

```json
{
  "data": {
    "provider": "google",
    "messages": [{"role": "user", "content": "Reply with: PONG"}],
    "response": "PONG"
  },
  "status_code": 200,
  "timestamp": "..."
}
```

## Troubleshooting

- **`UnicodeEncodeError: 'charmap' codec can't encode character '✓'`** on Windows — run with `$env:PYTHONUTF8 = "1"` before `python main.py`.
- **`gemini-pro is not found for API version v1beta`** — Google deprecated this model name. Set `GOOGLE_MODEL=gemini-2.5-flash` in `.env` and restart.
- **`OPENAI_API_KEY is not configured`** when you've set the key — make sure you replaced the `your_openai_key_here` placeholder, not just appended to it. The placeholder check looks for a `your_*` prefix.
- **VSCode shows "Package X not installed" warnings** — VSCode is using your system Python. `Ctrl+Shift+P` → "Python: Select Interpreter" → pick `.\venv\Scripts\python.exe`.
- **`source venv/bin/activate` fails on Windows** — that's a Linux path. Use `venv\Scripts\activate` on Windows, or just call `.\venv\Scripts\python.exe` directly without activating.

## Project layout

```
.
├── main.py                 # Flask app entry point
├── app/
│   ├── routes.py           # API endpoints (/api/*, /health)
│   ├── web.py              # Web playground (/)
│   ├── ai_services.py      # Provider abstractions (OpenAI/Anthropic/Google)
│   ├── config.py           # Env-backed config dataclass
│   ├── cache.py            # Redis cache with in-memory fallback
│   ├── database.py         # SQLAlchemy session factory
│   ├── models.py           # Pydantic request/response models
│   └── utils.py            # Response envelope helpers
├── tests/test_api.py
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── nginx.conf
```

## License

MIT
