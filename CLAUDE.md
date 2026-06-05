# Claude Context — fabriziogf.github.io

## Site
- Jekyll 3 / Minimal Mistakes theme, hosted on GitHub Pages
- Run locally: `LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 bundle exec jekyll serve --livereload`
- Push to deploy: `git push origin main`

---

## Training Analysis Blog Posts

### File naming
`_posts/YYYY-MM-DD-Month_training_analysis.md`
Publish date = **first Thursday of the following month**.

### Front matter
```yaml
---
title: "Month YYYY Training Analysis"
---
```
No dramatic subtitle. Clean format only.

### Tone & voice
- First person, analytical, long-time triathlete
- Goal races: Ironman Lake Placid (July 19, 2026); Rockford 70.3 (June 14, 2026) as tune-up
- Explain the *why* behind training decisions, not just what happened
- CTL/ATL/TSB: always define on first use if needed, but assume reader familiarity by later posts

### Standard section structure
1. Intro paragraph (theme of the month)
2. `---` divider
3. `## Overall Stats` — Markdown table: sessions, hours, distance, TSS, end-of-month CTL/ATL/TSB
4. `## Weekly Load Progression` — Markdown table: week range + TSS
5. `## Swim`
6. `## Bike`
7. `## Run`
8. `## Strength` — brief; note session count and consistency
9. `## Fitness Metrics at End of Month` — CTL progression narrative
10. `## What's Next` — bridge to next month

### CRITICAL: Sport classification
**Always use `workoutTypeValueId` from the raw TrainingPeaks API — never classify by session title keywords.**

| workoutTypeValueId | Sport |
|--------------------|-------|
| 1 | swim |
| 2 | bike |
| 3 | run |
| 4 | bike (brick) |
| 9 | strength |
| 13 | run/walk |
| others | other |

Sessions like "Ironman> 5×2000m Z3>4" are RUN workouts — the title contains distance notation that looks like swim but the type ID is authoritative. Never assume sport from session name.

### Fetching data
TrainingPeaks MCP may not load in all sessions. Fall back to direct Python:
```bash
/Users/fabriziogiovanninifilho/ai-projects/trainingpeaks-mcp/.venv/bin/python3 -c "
from trainingpeaks_mcp.client import TPClient
import json, datetime
client = TPClient()
start = '2026-05-04'
end   = '2026-06-04'
data  = client.get(f'/v1/athlete/2106530/workouts/{start}/{end}')
for w in data:
    print(w['workoutTypeValueId'], w['workoutDay'][:10], w.get('title',''))
"
```
Athlete ID: **2106530**

### CTL progression (2026)
| Month end | CTL |
|-----------|-----|
| January   | 79.2 |
| February  | 103.0 |
| March     | 118.8 |
| April     | 133.6 |
| May       | 140.5 |

---

## Training Dashboard (`/training/`)

- Page: `_pages/training.md`, permalink `/training/`
- Data file: `_data/training_data.yml` (machine-generated, 7-day rolling window)
- Daily updater: `scripts/update_training_data.py` (run via Cowork cron job)
- Navigation entry: `_data/navigation.yml` under `main` links

### Dashboard data file structure
```yaml
generated_at: "YYYY-MM-DD HH:MM"
window_start: "YYYY-MM-DD"
window_end:   "YYYY-MM-DD"
fitness:
  ctl: 140.5
  atl: 104.5
  tsb: +22.0
totals:
  swim:     { sessions: N, hours: N.N, distance_km: N.N, tss: N }
  bike:     { sessions: N, hours: N.N, distance_km: N.N, tss: N }
  run:      { sessions: N, hours: N.N, distance_km: N.N, tss: N }
  strength: { sessions: N, hours: N.N, distance_km: 0,   tss: N }
daily:      # 7 entries, one per day
  - date: "YYYY-MM-DD"
    swim:     { tss: N, hours: N.N }
    bike:     { tss: N, hours: N.N }
    run:      { tss: N, hours: N.N }
    strength: { tss: N, hours: N.N }
workouts:   # individual sessions
  - date: "YYYY-MM-DD"
    sport: swim|bike|run|strength|other
    title: "Session Name"
    hours: N.N
    distance_km: N.N
    tss: N
```

### Jekyll 3 Liquid gotchas
- **No `for` loop with inline filter**: `{% for x in "a,b" | split: "," %}` silently fails in Jekyll 3. Write explicit per-sport HTML instead.
- **Markdown tables + Liquid**: `{% if %}` blocks inside Markdown table rows emit newlines that break parsing. Use HTML `<table>` for any table that contains Liquid logic.

### Sport color palette
| Sport    | Color   |
|----------|---------|
| swim     | #4fc3f7 |
| bike     | #81c784 |
| run      | #ffb74d |
| strength | #ce93d8 |
| other    | #90a4ae |

---

## Running the updater script manually
```bash
/Users/fabriziogiovanninifilho/ai-projects/trainingpeaks-mcp/.venv/bin/python3 \
  /Users/fabriziogiovanninifilho/Documents/fabriziogf_page/scripts/update_training_data.py
```
