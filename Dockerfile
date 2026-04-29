# Multi-stage Dockerfile for Codeplex AI

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Build Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt


# Stage 2: Runtime
FROM python:3.11-slim

# Create the non-root user before any COPY so we can use --chown.
# Putting the pip --user tree under /root/.local (the default for root) and
# then dropping to a non-root user makes the binaries unreachable: /root is
# mode 0700, so codeplex can't traverse it. We instead place everything
# under /home/codeplex/.local, owned by codeplex from the start.
RUN useradd -m -u 1000 codeplex

WORKDIR /app

# PATH points to codeplex's user-installed scripts (gunicorn lives here).
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/home/codeplex/.local/bin:$PATH \
    ENVIRONMENT=production

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder, retargeted to codeplex's home
# and chown'd in the same step (no separate chmod/chown pass needed).
COPY --from=builder --chown=codeplex:codeplex /root/.local /home/codeplex/.local

# Copy application code with correct ownership.
COPY --chown=codeplex:codeplex . .

# Logs directory must be writable by gunicorn workers running as codeplex.
RUN mkdir -p logs && chown codeplex:codeplex logs

USER codeplex

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run application.
# main:create_app() — factory pattern; main.py only exposes `app` inside its
# __main__ block, so gunicorn must call the factory itself. The parens are
# how gunicorn detects this is a factory rather than a WSGI variable.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "--access-logfile", "logs/access.log", "--error-logfile", "logs/error.log", "main:create_app()"]

