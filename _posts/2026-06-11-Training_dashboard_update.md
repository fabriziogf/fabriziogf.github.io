---
title: "Updating the Training Dashboard: Trends, Personal Records, and a More Interactive Layout"
---

The [Training](/training/) page started as a simple 7-day snapshot: current fitness metrics, this week's sessions, and a few Chart.js charts. I wrote about that first version in [Building a Daily-Updated Training Dashboard with Jekyll and TrainingPeaks](/Training_dashboard/). It worked, but the view was narrow. You could see the last seven days, not how the year was going.

I wanted three things from an update: a longer time horizon, personal records pulled automatically from TrainingPeaks, and more detail on individual sessions. This post covers what changed, what worked, and where the API or tooling pushed back.

---

## Tabs

The original page was one long scrolling column. Adding 12 months of trend charts and a full PR section would have made it much longer. So the first change was a tab layout: **This Week**, **12-Month Trends**, and **Personal Records**.

Tab switching is plain JavaScript, no library. Each panel is a `<div>` toggled between `display:none` and `display:block`. On tab activation, Chart.js gets a `window.resize` event so charts that were hidden on load render at the right size.

The data still lives in one `_data/training_data.yml` file, injected into all three panels at build time with Liquid. No runtime API calls.

---

## 12-month trends

The updater used to fetch only the 7-day window. Now it also fetches 12 months of workouts and 12 months of CTL/ATL/TSB data, one extra API call each.

The 12 months of workouts are aggregated into monthly totals by sport (sessions, hours, distance, TSS) and written to a `monthly:` section in the YAML. The fitness data is sampled at the last entry of each day to build a `ctl_trend:` section.

Three new charts render in the Trends tab:

- **Monthly TSS by sport**: stacked bars over 12 months, showing load across swim, bike, run, and strength. Last year's Sep/Oct dip from post-Ironman recovery is obvious.
- **Monthly hours by sport**: same layout, hours instead of TSS.
- **CTL/ATL trend**: a line chart of fitness and fatigue over the year. The CTL build from ~65 in September to ~148 now is a clear slope.

There's also a **monthly volume heatmap**: a table with a row per month and a column per sport, where the background gets darker with total TSS relative to the biggest month. It's a quick way to see training distribution without reading numbers.

---

## Personal records

### What the API supports

The TrainingPeaks PR endpoint (`/personalrecord/v2/athletes/{id}/{sport}`) supports **bike** and **run**, with specific PR types:

- Bike: peak power for 5s, 1min, 5min, 10min, 20min, 60min
- Run: best average speed for 1km, 5km, 10km, half marathon, marathon

Swim isn't supported. Every swim PR type I tried returned a 400. TrainingPeaks just doesn't expose swim PRs through this API, so I dropped the swim table I'd built.

Run speeds come back in m/s and need converting to min/km. A 5km best of 4.36 m/s converts to 1000 / (4.36 × 60) = 3.83 min/km, shown as 3:49/km.

### The YAML sexagesimal trap

Once paces became strings like `3:49`, writing them unquoted to YAML caused a silent problem. YAML reads `3:49` as a base-60 number (`3 × 60 + 49 = 229`), so Jekyll got `229` instead of the string `3:49`. Pace became an integer.

The fix is to always quote these values. `"3:49"` is unambiguously a string. Bike power values are plain numbers, so only the pace strings had this problem.

### GPS artifacts

The API ranks best efforts from fastest to slowest. For some PR types, especially short ones like 1km, the top result sometimes comes from a GPS glitch during a long workout: a burst of speed that got recorded but never actually happened.

Here the symptom was a 1km all-time best of 2:29/km. That's 3:58 mile pace, which I have never run. Filtering out anything faster than 3:00/km (5.56 m/s) drops the artifact and surfaces the real best, 3:12/km.

The filter runs on all run PR types before taking the top record.

### Marathons that Garmin comes up short on

The marathon PR type looks for best efforts at the full 42.195km. But Garmin sometimes records a marathon as 41.5–42.0km because of GPS drift. Close enough that you covered the distance, short enough that the API misses it.

The fix is a separate scan of all raw workouts in the 12-month window. Any run of 41.5km or more at a pace of 3:00/km or slower counts as a candidate marathon. The best pace from that scan is compared with the API result, and the faster one wins.

This year the scan returns nothing (no marathon in 2026 yet), so the API result stands. But the logic is ready for when the race happens.

### This Year vs. All-Time

The PR tab has a toggle between 2026 and All-Time. It's CSS-driven: columns with class `pr-this-year` or `pr-all-time` are shown or hidden with `display:none` on click. No refetching, no extra markup. Both sets of values are in the page, and one is hidden at a time.

---

## Session table

The raw API response for each workout includes `heartRateAverage` and `powerAverage` as top-level fields. They just weren't being captured. Adding them to the YAML and showing them as columns in the sessions table took a few lines.

Not every session has both. Easy runs have no power. Pool swims have no chest-strap HR. The table shows `—` when a field is null.

---

## What the daily script does now

The updater started as a 200-line script that fetched 7 days and wrote a simple YAML file. Now it:

1. Fetches the 7-day window of workouts (This Week)
2. Fetches 12 months of workouts (monthly totals and the marathon fallback)
3. Fetches 12 months of fitness data (CTL trend)
4. Fetches bike and run PRs, all-time and year-to-date, for every PR type
5. Scans the 12-month workouts for marathon-distance runs as a fallback
6. Writes one `training_data.yml` covering all three tabs
7. Commits and pushes

It runs a bit longer with the extra API calls, but still finishes well under a minute. The Cowork cron job runs it daily, and the push triggers the GitHub Pages rebuild.

---

## Moving activity data to Strava

A couple of weeks after the rebuild above, I moved the dashboard's activity data from TrainingPeaks to Strava. Not a full switch, but a deliberate split. TrainingPeaks still owns what only it computes. Strava becomes the source of truth for what actually happened in each session.

My reasoning: Strava is where the activity record really lives, with distance, moving time, heart rate, power, and clean per-distance best efforts. TrainingPeaks is the only place with a Performance Management Chart (CTL/ATL/TSB) and TSS. So instead of picking one, the updater now talks to both.

### What comes from where

- **Strava**: the session feed, sessions/hours/distance, average HR and power, and run pace PRs.
- **TrainingPeaks**: CTL, ATL, TSB, the CTL trend, TSS (totals, daily, monthly, and per session), and bike peak-power PRs. Strava's API has no power-curve endpoint, so bike power has to stay on TrainingPeaks.

The YAML schema didn't change at all, so the three-tab page needed no edits. Only the source of each field changed.

### A stdlib-only Strava client

Strava uses OAuth2 with a rotating refresh token. I kept the client dependency-free: `urllib` for HTTP and the macOS keyring for credentials (`client_id`, `client_secret`, `refresh_token`), the same way the TrainingPeaks side stores secrets. Each run trades the refresh token for a short-lived access token and saves the new refresh token, since Strava rotates it every time.

### Attaching TSS to Strava activities

TSS only exists in TrainingPeaks, so each Strava activity is matched to a TrainingPeaks workout by date, sport, and nearest duration, and that workout's TSS is attached. Aggregate TSS (daily, monthly, totals) is summed straight from TrainingPeaks by date or month and sport, so the charts stay accurate even when the two services disagree a little on a session's length.

### Run PRs within the rate limit

Strava returns per-distance best efforts (1K, 5K, 10K, half, marathon), but only on the *detailed* activity endpoint, one call per activity. With nearly 1,000 runs in my history and a 1,000-requests-per-day cap, scanning everything at once isn't realistic.

So run PRs work in two layers. TrainingPeaks provides the full-history baseline (its all-time bests were already accurate). Strava best efforts are merged on top, with the faster pace winning per distance. The Strava side is an incremental cache that only fetches detail for runs it hasn't seen. A few new runs a day stays well under the limit, and the cache gradually takes over from the baseline as it fills in. A one-time backfill script exists for full history, but the baseline makes it optional.

---

## Rendering fixes

Two small Jekyll gotchas came up once the tab panels held more content:

- **Section dividers**: markdown `---` rules rendered as literal `---` text. kramdown doesn't process markdown inside a raw HTML block, and each tab panel is one big `<div>`. Switching to explicit `<hr>` elements fixed it. Same thing with the bold **Total TSS / Total Hours** line in the weekly summary: the `**…**` showed its asterisks until I switched to `<strong>`.
- **Linking sessions to Strava**: now that activities come from Strava, each row in the weekly sessions table links to its Strava activity. The updater stores the Strava activity ID per session, and the table wraps the title in a link (with the click isolated so it doesn't also toggle the row open).

---

## What's still missing

A few things I'd like eventually:

- **W/kg power curve**: normalizing bike power by body weight would make the numbers more meaningful across training phases
- **Race overlays**: marking race days on the CTL trend would make the fitness build easier to read
- **Swim PRs**: these need either a TrainingPeaks plan with broader API access or a manual data file updated after key sessions

For now, the dashboard gives a solid picture of where training has been and where my fitness sits heading into Rockford 70.3 in two weeks.
