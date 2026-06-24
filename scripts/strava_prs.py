#!/usr/bin/env python3
"""
Run pace PRs from Strava `best_efforts`, with an incremental on-disk cache.

Strava returns per-activity best efforts (1K, 5K, 10K, Half-Marathon, Marathon …)
on the *detailed* activity endpoint. Scanning all history every day would blow the
rate limit, so we keep a local cache and only fold in runs we haven't seen yet.

Cache shape (scripts/.strava_pr_cache.json):
{
  "processed_ids": [123, 456, ...],
  "all_time":  { "1K": {time, date, name, activity_id}, ... },
  "by_year":   { "2026": { "1K": {...}, ... }, ... }
}

The daily updater calls process_run() on each new run; the one-time
strava_backfill_prs.py replays full history into the same cache.
"""

from __future__ import annotations

import json
from pathlib import Path

CACHE = Path(__file__).parent / ".strava_pr_cache.json"

# Strava best_effort `name` → our PR key in training_data.yml
DIST_MAP: dict[str, str] = {
    "1K":            "speed1K",
    "5K":            "speed5K",
    "10K":           "speed10K",
    "Half-Marathon": "speedHalfMarathon",
    "Marathon":      "speedMarathon",
}

# Nominal metres per PR key — used to convert a best-effort time into pace/km.
DIST_METERS: dict[str, int] = {
    "speed1K":            1000,
    "speed5K":            5000,
    "speed10K":           10000,
    "speedHalfMarathon":  21097,
    "speedMarathon":      42195,
}

PR_LABELS: dict[str, str] = {
    "speed1K":            "1 km",
    "speed5K":            "5 km",
    "speed10K":           "10 km",
    "speedHalfMarathon":  "Half Marathon",
    "speedMarathon":      "Marathon",
}

# 3:00/km — anything faster is a GPS artefact, ignore it.
MAX_VALID_PACE_SEC_PER_KM = 180


def pace_per_km(seconds: float, key: str) -> str:
    """Total time over a known distance → 'M:SS' pace per km."""
    km = DIST_METERS[key] / 1000
    sec_per_km = seconds / km
    m = int(sec_per_km // 60)
    s = int(round(sec_per_km % 60))
    if s == 60:
        m, s = m + 1, 0
    return f"{m}:{s:02d}"


# ── Cache I/O ────────────────────────────────────────────────────────────────
def load_cache() -> dict:
    if CACHE.exists():
        return json.loads(CACHE.read_text())
    return {"processed_ids": [], "all_time": {}, "by_year": {}}


def save_cache(cache: dict) -> None:
    CACHE.write_text(json.dumps(cache, indent=2))


# ── Folding a run into the cache ─────────────────────────────────────────────
def process_run(detail: dict, cache: dict) -> bool:
    """Update cache with one detailed run's best efforts. Returns True if new."""
    aid = detail.get("id")
    if aid is None or aid in cache["processed_ids"]:
        return False

    name = detail.get("name", "")
    date = (detail.get("start_date_local") or "")[:10]
    year = date[:4]

    for eff in detail.get("best_efforts") or []:
        key = DIST_MAP.get(eff.get("name"))
        if not key:
            continue
        t = eff.get("elapsed_time") or eff.get("moving_time")
        if not t or t <= 0:
            continue
        # GPS-artefact guard
        if t / (DIST_METERS[key] / 1000) < MAX_VALID_PACE_SEC_PER_KM:
            continue

        rec = {"time": t, "date": date, "name": name, "activity_id": aid}

        cur = cache["all_time"].get(key)
        if cur is None or t < cur["time"]:
            cache["all_time"][key] = rec

        yb = cache["by_year"].setdefault(year, {})
        cury = yb.get(key)
        if cury is None or t < cury["time"]:
            yb[key] = rec

    cache["processed_ids"].append(aid)
    return True


# ── Build the prs['run'] block in training_data.yml shape ────────────────────
def build_run_prs(cache: dict, year: str) -> dict:
    out: dict = {}
    yb = cache.get("by_year", {}).get(year, {})
    for key in DIST_MAP.values():
        at = cache["all_time"].get(key)
        ty = yb.get(key)
        out[key] = {
            "all_time":          pace_per_km(at["time"], key) if at else None,
            "all_time_date":     at["date"] if at else "",
            "all_time_workout":  at["name"] if at else "",
            "this_year":         pace_per_km(ty["time"], key) if ty else None,
            "this_year_date":    ty["date"] if ty else "",
            "this_year_workout": ty["name"] if ty else "",
        }
    return out
