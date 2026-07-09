#!/usr/bin/env bash
set -euo pipefail

mkdir -p perf/results

LARAVEL_DOCKER_URL=${LARAVEL_DOCKER_URL:-http://127.0.0.1/api/health-check}
ZIG_NATIVE_URL=${ZIG_NATIVE_URL:-http://127.0.0.1:8080/api/health-check}
ZIG_DOCKER_URL=${ZIG_DOCKER_URL:-http://127.0.0.1:8081/api/health-check}

run_target() {
  local target=$1
  local url=$2

  for profile in load stress benchmark; do
    python3 perf/http_perf.py \
      "$profile" \
      --target "$target" \
      --url "$url" \
      --output "perf/results/${target}-${profile}.json" || true
  done
}

run_target laravel-docker "$LARAVEL_DOCKER_URL"
run_target zig-native "$ZIG_NATIVE_URL"
run_target zig-docker "$ZIG_DOCKER_URL"

python3 perf/render_dashboard.py perf/results docs/performance-dashboard.html
