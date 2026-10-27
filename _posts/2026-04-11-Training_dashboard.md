---
title: "Building a Daily-Updated Training Dashboard with Jekyll and TrainingPeaks"
---

I wanted a way to see my current training load on this site without opening TrainingPeaks or Strava. A simple page that answers three questions: what did I do this week, how fit am I right now, and how am I balancing load against recovery?

The result is the [Training](/training/) tab: a rolling 7-day dashboard with swim, bike, run, and strength stats, Chart.js charts, and PMC fitness metrics (CTL, ATL, TSB). A script pulls from the TrainingPeaks API every day and pushes a data file to GitHub.

This post covers how I built it and the problems I hit along the way.

---

## Architecture

The site runs on Jekyll 3 (GitHub Pages). No server-side code, no database. Everything has to be static at build time, and that shaped the whole design:

1. A Python script runs daily, fetches the past 7 days of workouts from TrainingPeaks, and writes them to `_data/training_data.yml`
2. The script commits and pushes that file, which triggers a Pages rebuild
3. Jekyll reads the YAML at build time and injects it into the page with Liquid
4. Chart.js (loaded from a CDN) renders the charts in the browser from data baked into the page

No API calls from the browser, no exposed tokens, no server. The page is fully static. It just rebuilds itself every day.

---

## Getting data out of TrainingPeaks

I already use a TrainingPeaks MCP server with Claude Code. The detail that matters here is how the API labels workouts.

Every workout has a `workoutTypeValueId` field, an integer that maps to the sport (1 = Swim, 2 = Bike, 3 = Run, 9 = Strength, etc.). There's also a `workoutTypeFamilyId` field that would be cleaner, but it's always `null` in the list endpoint. If you rely on the family ID or guess the sport from the session title, workouts get misclassified.

The lookup table:

| ID | Sport |
|----|-------|
| 1 | Swim |
| 2 | Bike |
| 3 | Run |
| 4 | Bike (Brick) |
| 9 | Strength |
| 13 | Run/Walk |

This matters more than it sounds. A title like "Ironman> 5×2000m Z3>4" contains distance notation that looks like swim yardage. A keyword classifier puts it in the swim column. The type ID correctly puts it in run. **Every classification in the script goes through the ID, never the title.**

Fitness metrics (CTL, ATL, TSB) come from a separate endpoint and get added to the same YAML file, so the dashboard shows them next to the weekly workouts.

---

## The data file

`_data/training_data.yml` connects the Python script to the Jekyll page. It's overwritten daily and never edited by hand.

It holds three things: the window dates, per-sport totals for the week, and a day-by-day breakdown for the charts:

```yaml
generated_at: "2026-06-04"
window_start: "2026-05-29"
window_end:   "2026-06-04"

fitness:
  ctl:  140.5
  atl:  104.5
  tsb:  +22.0

totals:
  swim:     { sessions: 3, hours: 2.5, distance_km: 8.5,   tss: 143 }
  bike:     { sessions: 4, hours: 9.9, distance_km: 340.8, tss: 470 }
  run:      { sessions: 4, hours: 4.1, distance_km: 50.3,  tss: 490 }
  strength: { sessions: 2, hours: 1.5, distance_km: 0,     tss: 45  }

daily:
  - date: "2026-05-29"
    swim:     { hours: 0.0, distance_km: 0.0, tss: 0.0, sessions: 0 }
    bike:     { hours: 2.1, distance_km: 72.0, tss: 98, sessions: 1 }
    ...
```

---

## Two Jekyll 3 gotchas

Building the template exposed two limitations of Jekyll 3 worth writing down.

**1. An inline filter in a `for` loop silently fails.**

In Jekyll 4 you can write:

```
{% for sport in "swim,bike,run,strength" | split: "," %}
```

In Jekyll 3 (which GitHub Pages still uses), this runs zero iterations. No error, no warning. It just skips the loop. The fix is to write explicit HTML for each sport instead of looping over a static list.

**2. Liquid blocks inside Markdown tables break the table.**

Conditionals like `{% if %}` inside a Markdown table row emit newlines that the Markdown parser reads as paragraph breaks, and the table collapses. The fix is to use an HTML `<table>` whenever a row needs Liquid logic. HTML tolerates whitespace; Markdown doesn't.

Both fail quietly. The page renders without errors but shows nothing, which makes them harder to track down than a crash.

---

## The daily update script

`scripts/update_training_data.py` is a standalone Python script that calls the TrainingPeaks API using the same venv as the MCP server. It:

1. Computes the 7-day window (yesterday − 6 days → yesterday)
2. Fetches raw workouts and classifies each by `workoutTypeValueId`
3. Fetches CTL/ATL/TSB from the fitness endpoint
4. Aggregates totals and builds the per-day breakdown
5. Writes the YAML file
6. Runs `git add`, `git commit`, and `git push`

The window ends yesterday, not today, because today's workouts may not be done yet. Anchoring on yesterday guarantees a complete window.

Authentication goes through the macOS keyring. The TrainingPeaks credentials live there, and the script picks them up as long as it runs as the same user. No environment variables or secrets files.

A recurring Cowork job runs the script once a day. The push keeps the dashboard current and triggers the Pages rebuild.

---

## What the dashboard shows

- **PMC cards**: CTL (fitness), ATL (fatigue), TSB (form), color-coded so positive TSB reads green and negative reads red
- **7-day sport summary**: sessions, hours, distance, and TSS per sport
- **Stacked bar charts**: daily TSS and daily hours by sport, to see how the week was spread across disciplines
- **TSS donut**: each sport's share of the week's load
- **Sessions table**: every workout with date, sport, title, hours, distance, and TSS

The charts use Chart.js 4.4.0 from a CDN. Liquid injects the YAML data at build time, so the charts render from static markup with no runtime API calls.

---

## What it's for

The dashboard doesn't replace TrainingPeaks. TrainingPeaks has a real PMC, a calendar, a workout builder, and everything else a serious training log needs.

What this gives me is a public snapshot that sits next to the monthly training posts and makes the data concrete. When I write that a month ended with CTL 140 and TSB +22, there's now a page that shows what that looks like, updated daily.

It was also good practice in building a small, constrained data pipeline: fetch, transform, serialize, commit, deploy. Fully automated, with nothing for the reader to see but the result.
