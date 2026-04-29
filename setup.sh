#!/usr/bin/env bash
# Cross-platform setup for Codeplex AI.
#
# Works in:
#   - Linux bash
#   - macOS bash / zsh (run as `bash setup.sh`)
#   - Windows Git Bash / MSYS2 / Cygwin / WSL
#
# On Windows, the venv layout differs (Scripts/ instead of bin/, .exe suffix)
# and the Python launcher is sometimes `py` instead of `python3`. Both
# variants are detected at runtime so the same file works everywhere.
#
# For a pure-Windows / cmd.exe / PowerShell flow, use setup.bat instead.

set -euo pipefail

echo "=========================================="
echo "Codeplex AI - Setup Script"
echo "=========================================="
echo

# ── Platform detection ─────────────────────────────────────────────────────
# OSTYPE is set by bash; Git Bash, MSYS2, and Cygwin all start with msys/mingw/cygwin.
case "${OSTYPE:-}" in
    msys*|mingw*|cygwin*) IS_WINDOWS=1 ;;
    *)                     IS_WINDOWS=0 ;;
esac

if [ "$IS_WINDOWS" = "1" ]; then
    VENV_BIN="venv/Scripts"
    PY_EXE="python.exe"
    ACTIVATE="venv/Scripts/activate"
else
    VENV_BIN="venv/bin"
    PY_EXE="python"
    ACTIVATE="venv/bin/activate"
fi

# ── Find a usable Python interpreter ───────────────────────────────────────
# Try common names in order. On Windows, Microsoft Store ships a stub for
# `python` that errors with "Python was not found" when no real Python is
# installed; detect and skip that.
find_python() {
    for candidate in python3.11 python3 python py; do
        if command -v "$candidate" >/dev/null 2>&1; then
            # Probe — Microsoft Store stub prints to stderr and exits non-zero.
            if "$candidate" --version >/dev/null 2>&1; then
                if [ "$candidate" = "py" ]; then
                    # py launcher: prefer 3.11 if available, otherwise default 3.x.
                    if py -3.11 --version >/dev/null 2>&1; then
                        echo "py -3.11"
                    else
                        echo "py -3"
                    fi
                else
                    echo "$candidate"
                fi
                return 0
            fi
        fi
    done
    return 1
}

echo "Detecting Python..."
if ! PYTHON_BIN=$(find_python); then
    echo "✗ No usable Python found on PATH."
    if [ "$IS_WINDOWS" = "1" ]; then
        echo "  Install Python 3.11 from https://www.python.org/downloads/"
        echo "  or run:  winget install Python.Python.3.11"
    else
        echo "  Install Python 3.11 (e.g. via your package manager or https://www.python.org/downloads/)."
    fi
    exit 1
fi

PYTHON_VERSION=$($PYTHON_BIN --version 2>&1 | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION detected ($PYTHON_BIN)"
echo

# Warn (but don't fail) if Python is too new — pinned deps don't have wheels for 3.12+.
PY_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
if [ "$PY_MAJOR" = "3" ] && [ "$PY_MINOR" -gt 11 ]; then
    echo "⚠ Python $PYTHON_VERSION is newer than 3.11. Some pinned dependencies"
    echo "  in requirements.txt don't have wheels for 3.12+. If pip install fails,"
    echo "  install Python 3.11 and re-run."
    echo
fi

# ── Create venv ────────────────────────────────────────────────────────────
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    $PYTHON_BIN -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo

# ── Activate (and verify) ──────────────────────────────────────────────────
# `source` only affects the current shell. The activation script may not
# even exist on Windows if the venv was created by a non-bash tool; check
# both paths just in case.
echo "Activating virtual environment..."
if [ ! -f "$ACTIVATE" ]; then
    # Maybe the venv was created on the other platform — fall back to the alt.
    for alt in venv/bin/activate venv/Scripts/activate; do
        if [ -f "$alt" ]; then
            ACTIVATE="$alt"
            VENV_BIN="$(dirname "$alt")"
            break
        fi
    done
fi
if [ ! -f "$ACTIVATE" ]; then
    echo "✗ Could not find activation script in venv/. Try:  rm -rf venv  and re-run."
    exit 1
fi
# shellcheck disable=SC1090
source "$ACTIVATE"
echo "✓ Virtual environment activated ($ACTIVATE)"
echo

# Use the venv's pip directly to avoid any PATH ambiguity on Windows.
VENV_PY="$VENV_BIN/$PY_EXE"
[ -x "$VENV_PY" ] || VENV_PY="$VENV_BIN/python"  # fallback if .exe suffix not used

# ── Upgrade pip ────────────────────────────────────────────────────────────
echo "Upgrading pip..."
"$VENV_PY" -m pip install --upgrade pip setuptools wheel
echo "✓ Pip upgraded"
echo

# ── Install deps ───────────────────────────────────────────────────────────
echo "Installing dependencies..."
"$VENV_PY" -m pip install -r requirements.txt
echo "✓ Dependencies installed"
echo

# ── App directories ────────────────────────────────────────────────────────
echo "Creating application directories..."
mkdir -p logs output
# app/ and tests/ already exist in the repo; mkdir -p is a no-op if so.
mkdir -p app tests
echo "✓ Directories created"
echo

# ── .env ──────────────────────────────────────────────────────────────────
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo "⚠ Please update .env with your API keys."
    else
        echo "⚠ No .env.example found — skipping .env creation."
    fi
else
    echo "✓ .env file already exists"
fi
echo

# ── Final report ───────────────────────────────────────────────────────────
echo "=========================================="
echo "Setup completed successfully!"
echo "=========================================="
echo
echo "Next steps:"
echo "  1. Update .env with your API keys."
if [ "$IS_WINDOWS" = "1" ]; then
    echo "  2. Activate the venv (in Git Bash):  source $ACTIVATE"
    echo "     ...or in PowerShell:               .\\venv\\Scripts\\Activate.ps1"
else
    echo "  2. Activate the venv:  source venv/bin/activate"
fi
echo "  3. Run the app:  python main.py"
echo "  4. Or with Docker:  docker compose up"
echo

# ── API key status ─────────────────────────────────────────────────────────
if [ -f ".env" ]; then
    echo "API Keys Status:"
    for key in OPENAI_API_KEY ANTHROPIC_API_KEY GOOGLE_API_KEY; do
        # Match the line, then check whether the value starts with `your_`
        # (the placeholder pattern from .env.example) or is empty.
        line=$(grep -E "^${key}=" .env || true)
        if [ -z "$line" ]; then
            echo "  ⚠ $key: missing from .env"
        else
            value=${line#*=}
            if [ -z "$value" ] || [[ "$value" == your_* ]]; then
                echo "  ⚠ $key: NOT SET (placeholder)"
            else
                echo "  ✓ $key: SET"
            fi
        fi
    done
fi
