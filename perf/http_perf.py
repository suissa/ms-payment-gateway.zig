#!/usr/bin/env python3
"""Small dependency-free HTTP load/stress/benchmark runner."""
from __future__ import annotations
import argparse, concurrent.futures, json, statistics, time, urllib.request, urllib.error
from datetime import datetime, timezone

PROFILES = {
    "load": {"requests": 200, "concurrency": 20, "timeout": 5.0},
    "stress": {"requests": 1000, "concurrency": 100, "timeout": 5.0},
    "benchmark": {"requests": 500, "concurrency": 1, "timeout": 5.0},
}

def hit(url: str, timeout: float) -> dict:
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as res:
            res.read()
            status = res.status
            ok = 200 <= status < 400
            err = None
    except urllib.error.HTTPError as exc:
        status, ok, err = exc.code, False, str(exc)
    except Exception as exc:
        status, ok, err = 0, False, exc.__class__.__name__ + ": " + str(exc)
    return {"latency_ms": (time.perf_counter() - start) * 1000, "status": status, "ok": ok, "error": err}

def percentile(values: list[float], pct: float) -> float:
    if not values: return 0.0
    values = sorted(values)
    idx = min(len(values) - 1, max(0, round((pct / 100) * (len(values) - 1))))
    return values[idx]

def run(profile: str, target: str, url: str, requests: int, concurrency: int, timeout: float) -> dict:
    started = time.perf_counter()
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(hit, url, timeout) for _ in range(requests)]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    elapsed = time.perf_counter() - started
    lat = [r["latency_ms"] for r in results]
    failures = [r for r in results if not r["ok"]]
    return {
        "target": target, "profile": profile, "url": url,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "requests": requests, "concurrency": concurrency, "duration_seconds": elapsed,
        "requests_per_second": requests / elapsed if elapsed else 0,
        "success": requests - len(failures), "failures": len(failures),
        "latency_ms": {
            "min": min(lat) if lat else 0, "mean": statistics.fmean(lat) if lat else 0,
            "median": statistics.median(lat) if lat else 0, "p95": percentile(lat, 95),
            "p99": percentile(lat, 99), "max": max(lat) if lat else 0,
        },
        "sample_errors": [f["error"] for f in failures if f.get("error")][:5],
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("profile", choices=PROFILES)
    parser.add_argument("--target", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--requests", type=int)
    parser.add_argument("--concurrency", type=int)
    parser.add_argument("--timeout", type=float)
    args = parser.parse_args()
    cfg = PROFILES[args.profile]
    data = run(args.profile, args.target, args.url, args.requests or cfg["requests"], args.concurrency or cfg["concurrency"], args.timeout or cfg["timeout"])
    from pathlib import Path
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    print(json.dumps(data, indent=2))
    return 0 if data["failures"] == 0 else 2
if __name__ == "__main__": raise SystemExit(main())
