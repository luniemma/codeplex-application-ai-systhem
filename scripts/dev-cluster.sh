#!/usr/bin/env bash
# Bring the Codeplex AI stack up/down on whatever Kubernetes cluster
# `kubectl` currently points at — minikube, kind, Docker Desktop, k3d,
# a real cluster, anything.
#
# Usage:
#   ./scripts/dev-cluster.sh up       # apply manifests, wait, start port-forwards
#   ./scripts/dev-cluster.sh down     # kill port-forwards (manifests stay)
#   ./scripts/dev-cluster.sh status   # show pods + port-forward state
#   ./scripts/dev-cluster.sh urls     # print the endpoint URLs and exit
#   ./scripts/dev-cluster.sh nuke     # delete the namespace (everything goes)
#
# Ports are intentionally NOT 8000/9090/3000 — those collide with a local
# Flask dev server, a host-side Prometheus, and Grafana respectively. The
# 1xxxx prefix avoids those without losing the easy-to-remember number.

set -euo pipefail

NAMESPACE="${NAMESPACE:-codeplex-ai}"
APP_PORT="${APP_PORT:-18000}"
PROM_PORT="${PROM_PORT:-19090}"
GRAFANA_PORT="${GRAFANA_PORT:-13000}"

# PID file location — /tmp on Unix, $TEMP on Windows. Git Bash maps both.
PIDFILE="${TMPDIR:-/tmp}/codeplex-ai-portforwards.pids"

# ── Colors (skipped if NO_COLOR is set or stdout isn't a terminal) ─────
if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
    GREEN='\033[0;32m'; YELLOW='\033[0;33m'; RED='\033[0;31m'; CYAN='\033[0;36m'; RESET='\033[0m'
else
    GREEN=''; YELLOW=''; RED=''; CYAN=''; RESET=''
fi

log()  { printf "${CYAN}==>${RESET} %s\n" "$*"; }
ok()   { printf "${GREEN}✓${RESET} %s\n" "$*"; }
warn() { printf "${YELLOW}⚠${RESET} %s\n" "$*"; }
die()  { printf "${RED}✗${RESET} %s\n" "$*" >&2; exit 1; }

require() { command -v "$1" >/dev/null 2>&1 || die "$1 not found on PATH"; }

# ── Cluster check ─────────────────────────────────────────────────────
check_cluster() {
    require kubectl
    if ! kubectl version -o json >/dev/null 2>&1; then
        die "kubectl can't reach a cluster. Start one first (minikube start, kind create cluster, etc.)"
    fi
    local ctx
    ctx=$(kubectl config current-context 2>/dev/null || echo "<none>")
    log "kubectl context: ${ctx}"
}

# ── Subcommand: up ─────────────────────────────────────────────────────
cmd_up() {
    check_cluster

    log "Applying k8s/ manifests..."
    kubectl apply -f k8s/

    log "Waiting for rollouts (timeout 180s each)..."
    for d in codeplex-ai redis prometheus grafana; do
        if kubectl -n "$NAMESPACE" get deploy "$d" >/dev/null 2>&1; then
            kubectl -n "$NAMESPACE" rollout status "deploy/$d" --timeout=180s
        fi
    done
    ok "All deployments ready."

    # Stop any leftover port-forwards from a previous run.
    cmd_down >/dev/null 2>&1 || true

    log "Starting port-forwards..."
    : > "$PIDFILE"
    kubectl -n "$NAMESPACE" port-forward svc/codeplex-ai "${APP_PORT}:8000"   >/dev/null 2>&1 & echo $! >> "$PIDFILE"
    kubectl -n "$NAMESPACE" port-forward svc/prometheus  "${PROM_PORT}:9090"  >/dev/null 2>&1 & echo $! >> "$PIDFILE"
    kubectl -n "$NAMESPACE" port-forward svc/grafana     "${GRAFANA_PORT}:3000" >/dev/null 2>&1 & echo $! >> "$PIDFILE"

    # Give port-forwards a moment to bind.
    sleep 3

    # Smoke-check each one.
    local fail=0
    for spec in "codeplex-ai|http://localhost:${APP_PORT}/health" \
                "prometheus|http://localhost:${PROM_PORT}/-/healthy" \
                "grafana|http://localhost:${GRAFANA_PORT}/api/health"; do
        local svc="${spec%%|*}"; local url="${spec##*|}"
        if curl -fsS -o /dev/null -m 5 "$url"; then
            ok "$svc reachable at $url"
        else
            warn "$svc not reachable at $url (it may still be starting)"
            fail=1
        fi
    done

    cmd_urls
    [ "$fail" = 0 ] || warn "One or more services didn't respond yet — re-run 'status' in a few seconds."
}

# ── Subcommand: down ──────────────────────────────────────────────────
cmd_down() {
    if [ ! -f "$PIDFILE" ]; then
        log "No port-forwards tracked; nothing to stop."
        return 0
    fi
    log "Stopping port-forwards..."
    while IFS= read -r pid; do
        [ -n "$pid" ] || continue
        if kill "$pid" 2>/dev/null; then
            ok "killed pid=$pid"
        fi
    done < "$PIDFILE"
    rm -f "$PIDFILE"
}

# ── Subcommand: status ────────────────────────────────────────────────
cmd_status() {
    check_cluster
    log "Pods in $NAMESPACE:"
    kubectl -n "$NAMESPACE" get pods 2>/dev/null || warn "namespace not found"

    if [ -f "$PIDFILE" ]; then
        echo
        log "Tracked port-forwards:"
        while IFS= read -r pid; do
            [ -n "$pid" ] || continue
            if kill -0 "$pid" 2>/dev/null; then
                ok "pid=$pid running"
            else
                warn "pid=$pid dead"
            fi
        done < "$PIDFILE"
    else
        warn "No port-forwards tracked. Run './scripts/dev-cluster.sh up' to start them."
    fi
}

# ── Subcommand: urls ──────────────────────────────────────────────────
cmd_urls() {
    cat <<EOF

────────────────────────────────────────────────────────────────────────
 Codeplex AI — endpoints
────────────────────────────────────────────────────────────────────────

  Web playground:        http://localhost:${APP_PORT}/
  Health (liveness):     http://localhost:${APP_PORT}/health
  Liveness (alias):      http://localhost:${APP_PORT}/livez
  Readiness:             http://localhost:${APP_PORT}/readyz
  Metrics (Prometheus):  http://localhost:${APP_PORT}/metrics
  Models list:           http://localhost:${APP_PORT}/api/models

  Prometheus UI:         http://localhost:${PROM_PORT}/
  Scrape targets:        http://localhost:${PROM_PORT}/targets
  Health:                http://localhost:${PROM_PORT}/-/healthy

  Grafana:               http://localhost:${GRAFANA_PORT}/         (admin / admin)
  Codeplex AI dashboard: http://localhost:${GRAFANA_PORT}/d/codeplex-ai/codeplex-ai

────────────────────────────────────────────────────────────────────────
EOF
}

# ── Subcommand: nuke ──────────────────────────────────────────────────
cmd_nuke() {
    check_cluster
    cmd_down >/dev/null 2>&1 || true
    log "Deleting namespace $NAMESPACE (this removes everything)..."
    kubectl delete namespace "$NAMESPACE" --ignore-not-found
    ok "Namespace gone."
}

# ── Main ──────────────────────────────────────────────────────────────
case "${1:-}" in
    up)     cmd_up ;;
    down)   cmd_down ;;
    status) cmd_status ;;
    urls)   cmd_urls ;;
    nuke)   cmd_nuke ;;
    *)
        cat <<EOF
Usage: $0 <command>

Commands:
  up      Apply k8s/ manifests, wait for rollouts, start port-forwards
  down    Stop port-forwards started by 'up' (manifests stay applied)
  status  Show pod state + port-forward state
  urls    Print the endpoint URLs and exit
  nuke    Delete the entire namespace (everything goes)

Env overrides:
  NAMESPACE     (default: codeplex-ai)
  APP_PORT      (default: 18000)
  PROM_PORT     (default: 19090)
  GRAFANA_PORT  (default: 13000)
EOF
        exit 1
        ;;
esac
