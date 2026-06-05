---
title: "Building a Live Training Dashboard with Jekyll and TrainingPeaks"
---

One of the things I wanted on this site was a way to see my current training load at a glance without having to open TrainingPeaks or Strava. A simple page that answers: what did I actually do this week, how fit am I right now, and how am I balancing load against recovery?

The result is the [Training](/training/) tab — a rolling 7-day dashboard that shows swim, bike, run, and strength stats alongside Chart.js visualizations and PMC fitness metrics (CTL, ATL, TSB). It updates daily via an automated script that pulls from the TrainingPeaks API and pushes a data file to GitHub.

Here is how it was built, and the technical problems that came up along the way.

---

## The architecture

The site runs on Jekyll 3 (GitHub Pages), which means no server-side code and no database. Everything has to be static at build time. That constraint shaped the whole approach:

1. A Python script runs daily, fetches the past 7 days of workouts from TrainingPeaks, and writes the results to `_data/training_data.yml`
2. The script commits and pushes that file to GitHub, triggering a Pages rebuild
3. Jekyll reads the YAML at build time and injects it into the page via Liquid templating
4. Chart.js (loaded from CDN) renders the visualizations client-side from data baked into the page

No API calls from the browser, no tokens exposed, no server needed. The page is fully static — it just rebuilds itself every day.

---

## Getting data out of TrainingPeaks

TrainingPeaks has an MCP server I use for Claude Code integrations, but the relevant detail here is a subtlety in how the API returns workout data.

Every workout has a `workoutTypeValueId` field — an integer that maps to the actual sport type (1 = Swim, 2 = Bike, 3 = Run, 9 = Strength, etc.). There is also a `workoutTypeFamilyId` field that would be cleaner to use, but it is always `null` in the list endpoint. If you rely on the family ID or try to infer sport from the session title, you get misclassification.

The canonical lookup table:

| ID | Sport |
|----|-------|
| 1 | Swim |
| 2 | Bike |
| 3 | Run |
| 4 | Bike (Brick) |
| 9 | Strength |
| 13 | Run/Walk |

This matters more than it sounds. Session titles like "Ironman> 5×2000m Z3>4" contain distance notation that looks like swim yardage if you are pattern-matching on strings. A keyword-based classifier will put that in the swim column. The type ID always puts it correctly in run. Every classification decision in the script goes through the ID lookup, never through the title.

The fitness metrics (CTL, ATL, TSB) come from a separate endpoint and are appended to the same YAML file so the dashboard can show the full performance management picture alongside the weekly workout data.

---

## The data file

`_data/training_data.yml` is the bridge between the Python script and the Jekyll page. It gets overwritten daily and is never edited by hand — the header of the file says so explicitly.

The structure covers three things: the rolling window metadata, per-sport totals for the week, and a day-by-day breakdown for the charts:

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

Building the page template exposed two non-obvious limitations of Jekyll 3 that are worth documenting.

**1. Inline filter in a `for` loop silently fails.**

In Jekyll 4, you can write:

```liquid
{% for sport in "swim,bike,run,strength" | split: "," %}
```

In Jekyll 3 (which GitHub Pages still uses), this silently produces no iterations. No error, no warning — it just skips the loop entirely. The fix is to write explicit HTML for each sport rather than trying to loop over a static list. Tedious, but it works.

**2. Liquid blocks inside Markdown tables break the table.**

Conditionals like `{% if %}` inside a Markdown table row emit newlines that the Markdown parser treats as paragraph breaks, collapsing the table entirely. The fix is to use an HTML `<table>` instead of Markdown syntax for any table that needs Liquid logic inside its rows. HTML is whitespace-tolerant; Markdown is not.

Both of these issues are the kind of thing that fails quietly — the page renders without error but shows nothing. That makes them harder to diagnose than a loud crash would be.

---

## The daily update script

`scripts/update_training_data.py` is a standalone Python script that runs against the TrainingPeaks API using the same venv as the MCP server. It:

1. Computes the 7-day window (yesterday − 6 days → yesterday)
2. Fetches raw workouts and classifies each by `workoutTypeValueId`
3. Fetches CTL/ATL/TSB from the fitness endpoint
4. Aggregates totals and builds the per-day breakdown
5. Writes the YAML file
6. Runs `git add`, `git commit`, and `git push`

The window ends at yesterday (not today) because today's workouts may not be complete yet. Using yesterday as the anchor guarantees a fully closed window.

Authentication is handled via the macOS keyring — the TrainingPeaks credentials are stored there and the script inherits them as long as it runs as the same user. No environment variables or secrets files are needed.

A Cowork recurring job runs the script once per day, keeps the dashboard current, and triggers a GitHub Pages rebuild automatically via the push.

---

## What the dashboard shows

The final page has four sections:

- **PMC cards**: CTL (fitness), ATL (fatigue), TSB (form), color-coded so a positive TSB reads green and negative reads red
- **7-day sport summary**: sessions, hours, distance, and TSS per sport for the rolling window
- **Stacked bar charts**: daily TSS by sport and daily hours by sport — useful for seeing how the week was distributed across disciplines
- **TSS donut**: proportion of total load by sport for the week
- **Sessions table**: each individual workout with date, sport, title, hours, distance, and TSS

The charts use Chart.js 4.4.0 loaded from CDN. The data is injected from the YAML file at build time via Liquid, so the charts render entirely from static markup — no runtime API calls.

---

## What this is actually for

The dashboard is not a replacement for TrainingPeaks. TrainingPeaks has a real PMC, calendar view, structured workout builder, and everything else a serious training log needs.

What this gives me is a public-facing snapshot that lives alongside the training analysis posts and makes the data tangible rather than abstract. When I write that a month ended with CTL 140 and TSB +22, there is now a page that shows what that looks like in real time rather than just a number in a table.

It is also a useful exercise in building a constrained data pipeline: fetch, transform, serialize, commit, deploy — entirely automated, no moving parts visible to the user.
