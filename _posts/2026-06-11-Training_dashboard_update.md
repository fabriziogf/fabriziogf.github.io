---
title: "Updating the Training Dashboard: Trends, Personal Records, and a More Interactive Layout"
---

The [Training](/training/) page started as a simple 7-day snapshot — current fitness metrics, this week's sessions, a few Chart.js charts. It worked, but the view was narrow. You could see what happened in the last seven days, not how the year was unfolding.

I wanted three things from an update: a longer time horizon, personal records pulled automatically from TrainingPeaks, and more information when looking at individual sessions. This post documents what changed, what worked, and the few places where the API or tooling pushed back.

---

## Reorganizing the page into tabs

The original page was a single scrollable column. Adding 12 months of trend charts and a full PR section would have made it very long. So the first change was a tab layout: **This Week**, **12-Month Trends**, and **Personal Records**.

The tab switching is pure JavaScript — no library needed. Each panel is a `<div>` that gets `display:none` or `display:block` toggled, with Chart.js receiving a `window.resize` event on tab activation so charts that were hidden on load render at the correct size.

The data still lives in a single `_data/training_data.yml` file and gets injected into all three panels at build time via Liquid. No runtime API calls.

---

## 12-month trends

The updater script previously fetched only the 7-day window. The change here was extending it to also fetch 12 months of workouts and 12 months of CTL/ATL/TSB fitness data from a single additional API call each.

The 12-month workouts get aggregated into monthly totals by sport — sessions, hours, distance, TSS — and written into a `monthly:` section of the YAML. The fitness data gets sampled at the last entry per calendar day to produce a `ctl_trend:` section.

Three new charts render in the Trends tab:

- **Monthly TSS by sport** — stacked bar, 12 months. Shows load distribution across swim, bike, run, and strength. The Sep/Oct dip from post-Ironman recovery last year is obvious.
- **Monthly hours by sport** — same structure, hours instead of TSS.
- **CTL/ATL trend** — a line chart of fitness and fatigue over the year. The CTL build from ~65 in September to the current ~148 is visible as a clear slope.

There's also a **monthly volume heatmap** — a table where each row is a month, each column is a sport, and the background intensity scales with total TSS relative to the highest-volume month. It's a quick way to spot training distribution patterns without reading numbers.

---

## Personal records

### What the TrainingPeaks API supports

The TrainingPeaks PR endpoint (`/personalrecord/v2/athletes/{id}/{sport}`) supports **bike** and **run** with specific PR types:

- Bike: peak power for 5s, 1min, 5min, 10min, 20min, 60min
- Run: best average speed for 1km, 5km, 10km, half marathon, marathon

Swim is not supported. Every swim PR type I tried returned 400. This is a known limitation — TrainingPeaks doesn't expose swim PRs through this API. So the swim table I initially built got dropped entirely.

The run speed values come back in m/s, which need converting to min/km pace. A 5km best of 4.36 m/s converts to 1000 / (4.36 × 60) = 3.83 min/km, displayed as 3:49/km.

### YAML sexagesimal trap

After converting paces to strings like `3:49`, writing them unquoted to YAML causes a silent problem. YAML interprets `3:49` as a base-60 number — `3 × 60 + 49 = 229` — so the value that comes out on the Jekyll side is `229` rather than the string `3:49`. Pace became an integer.

The fix is to always quote these values when writing the YAML. `"3:49"` is unambiguously a string. Bike power values are plain numbers so they don't have this problem, only the pace strings.

### Filtering out GPS artifacts

The API returns the best effort ranked from fastest to slowest. For some PR types — especially short distances like 1km — the top result occasionally comes from a GPS glitch during a long workout: a burst of speed that was recorded but never actually ran.

The specific symptom here was a 1km all-time best of 2:29/km. That's a 3:58 mile pace, which I have never run. Filtering out any result faster than 3:00/km (5.56 m/s) drops the artifact and surfaces the real best, which was 3:12/km.

The filter applies to all run PR types before taking the top record.

### Marathon with Garmin undercount

The marathon PR type looks for best efforts at full marathon distance (42.195km). The problem is Garmin occasionally records a marathon as 41.5–42.0km due to GPS drift — close enough that you covered the distance, but short enough that the API misses it.

The fix is a parallel scan of all raw workouts in the 12-month window. Any run with recorded distance ≥ 41.5km and a pace ≥ 3:00/km is a candidate marathon effort. The best average pace from the workout scan gets compared against the API result, and the faster of the two wins.

For this year the workout scan currently returns nothing — no marathon in 2026 yet — so the API result stands. But the logic is there for when the race happens.

### This Year vs. All-Time toggle

The PR tab has a toggle between 2026 (this year) and All-Time. The toggle is CSS-driven: columns with class `pr-this-year` or `pr-all-time` get shown or hidden with `display:none` on click. No data re-fetching, no extra markup — the two sets of values are both present in the page and one set is hidden at any given time.

---

## Enhanced session table

The raw API response for each workout includes `heartRateAverage` and `powerAverage` as top-level fields — they were just never being captured. Adding them to the workout entries in the YAML and surfacing them as columns in the sessions table took a few lines.

Not every session has both. Easy runs don't have power. Pool swims don't have HR from a chest strap. The table shows `—` when the field is null.

---

## What the daily script now does

The updater was originally a 200-line script that fetched 7 days and wrote a simple YAML file. After these changes, it does more:

1. Fetches 7-day window workouts (for the This Week panel)
2. Fetches 12-month workouts (for monthly aggregates and marathon fallback)
3. Fetches 12 months of fitness data (for the CTL trend)
4. Fetches bike and run PRs — all-time and year-to-date — for all PR types
5. Scans the 12-month workouts for marathon-distance runs as a fallback
6. Writes a single `training_data.yml` covering all three tabs
7. Commits and pushes

Runtime is a little longer — more API calls — but still finishes in well under a minute. The Cowork cron job runs it once daily and the push triggers a GitHub Pages rebuild automatically.

---

## What's still missing

A few things I'd eventually want:

- **W/kg power curve** — normalizing bike power by body weight would make the numbers more meaningful across different training phases
- **Race result overlays** — flagging race days on the CTL trend would make the fitness build-up more readable
- **Swim PRs** — these will require either a TrainingPeaks plan with broader API access, or a manual data file updated after key sessions

For now the dashboard gives a solid picture of where the training has been and where fitness sits heading into Rockford 70.3 in two weeks.
