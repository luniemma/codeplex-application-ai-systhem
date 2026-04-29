"""Prometheus metrics integration.

Mounts an OpenMetrics-formatted `/metrics` endpoint and auto-instruments every
Flask route with request count + latency histograms (labels: method, status,
endpoint).

Multi-worker gunicorn note: when `PROMETHEUS_MULTIPROC_DIR` is set, the
multiprocess collector aggregates metrics across workers via files in that
directory. The k8s deployment mounts an emptyDir at `/tmp/prometheus_multiproc`
and sets the env var so this Just Works. Without that env var (e.g. `flask
run` for local dev) we fall back to the in-process collector — fine because
there's only one process.
"""

import os

from prometheus_flask_exporter import PrometheusMetrics
from prometheus_flask_exporter.multiprocess import GunicornInternalPrometheusMetrics


def install_metrics(app, version: str = "1.0.0") -> PrometheusMetrics:
    # GunicornInternalPrometheusMetrics — exposes /metrics on the same Flask
    # app while still using the multiprocess collector. The plain
    # GunicornPrometheusMetrics variant assumes a separate HTTP server on its
    # own port (started from a gunicorn when_ready hook), so it deliberately
    # skips the route registration; we want both behaviors at once.
    if os.environ.get("PROMETHEUS_MULTIPROC_DIR"):
        metrics = GunicornInternalPrometheusMetrics(app)
    else:
        metrics = PrometheusMetrics(app)

    metrics.info("codeplex_ai_build_info", "Codeplex AI build info", version=version)
    return metrics
