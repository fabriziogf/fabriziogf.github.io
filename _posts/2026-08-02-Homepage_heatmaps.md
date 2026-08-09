---
title: "Building the Commits and Training Hours Heatmaps"
---

The homepage now has two year-long heatmaps: GitHub contributions and workout hours. This post is about how the two charts are built.

---

## The GitHub grid

Both the heatmaps were inspired by the Github grid. Mine currently looks a bit bare - I am working on it. I like how it clearly shows the consistency of activity, something a bar chart wouldn't accomplish with such simplicity and elegance. Training consistency is also something I care about, so I built the same grid for my Strava hours.

---

## How it's built

Both charts are static. Nothing is fetched in the browser: both are assembled at build time, and since the training updater pushes daily, the site rebuilds and the squares stay current.

**GitHub data needs no token.** The profile calendar is served as plain markup at `github.com/users/<name>/contributions`, one `<td>` per day carrying `data-date` and `data-level` (0–4), with the exact count in the tooltip text. Parsing that is less work than authenticating against the GraphQL API, and there is no secret to store in Actions.

**Training data was already there.** The daily updater pulls a year of Strava activities to build the dashboard's monthly trends, so summing each day's moving time is a free aggregation on data I had already fetched — no extra API calls, just a new `year_daily` block in the YAML.

Rendering is one Astro component used twice, emitting inline SVG. Colors come in as a CSS variable, so each chart takes its source's brand color and both adapt to light and dark mode. GitHub hands over its own 0–4 buckets; for hours I picked fixed thresholds — 1.5, 3, and 4.5 — so a light month actually reads light instead of being normalized into looking busy.

Two things I got wrong first. GitHub pads its calendar out to whole weeks, so on the right day of the week it returns *tomorrow* as a trailing square; future days now get skipped. And to make both grids exactly the same width, the training chart draws whatever span GitHub reports rather than its own — which means the updater has to pull slightly more than a year so that span is always covered. The extra days feed the squares only. **The total in the corner still counts the trailing 365 days, and the dashboard never sees them.**

The last addition was clicking. Each square had a `<title>`, which gives you a tooltip on hover and nothing at all on a phone.
