#!/usr/bin/env python3
"""
One-time backfill of the run-PR cache from full Strava history.

The daily updater only folds in *new* runs, so run this once to seed all-time
bests from everything you've ever logged. It's rate-limit aware (Strava allows
~100 requests / 15 min): it sleeps between detail calls and resumes safely if
re-run, because process_run() skips already-processed activities.

Run:
  /Users/fabriziogiovanninifilho/ai-projects/trainingpeaks-mcp/.venv/bin/python3 \
      scripts/strava_backfill_prs.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from strava_client import StravaClient, classify
from strava_prs import load_cache, save_cache, process_run

# Conservative: ~90 detail calls per 15-min window, with margin.
SLEEP_BETWEEN_DETAILS = 11.0  # seconds


def main() -> None:
    c = StravaClient()
    cache = load_cache()

    # Pull the full activity list (summary objects are cheap, 200/page).
    print("Fetching full activity list…")
    now = int(time.time())
    acts = c.activities(after=0, before=now)
    runs = [a for a in acts if classify(a) == "run"]
    runs.sort(key=lambda a: a.get("start_date_local", ""))
    todo = [a for a in runs if a["id"] not in cache["processed_ids"]]
    print(f"{len(runs)} total runs, {len(todo)} new to process.")

    for i, a in enumerate(todo, 1):
        try:
            detail = c.activity_detail(a["id"])
        except Exception as e:  # noqa: BLE001
            print(f"  [{i}/{len(todo)}] {a['id']} failed: {e} — saving and stopping.")
            break
        new = process_run(detail, cache)
        d = (a.get("start_date_local") or "")[:10]
        print(f"  [{i}/{len(todo)}] {d}  {a.get('name','')[:40]}  {'✓' if new else '·'}")
        if i % 25 == 0:
            save_cache(cache)  # checkpoint
        time.sleep(SLEEP_BETWEEN_DETAILS)

    save_cache(cache)
    print("\nDone. All-time bests now in cache:")
    for key, rec in cache["all_time"].items():
        print(f"  {key:18} {rec['time']}s on {rec['date']}  ({rec['name']})")


if __name__ == "__main__":
    main()
