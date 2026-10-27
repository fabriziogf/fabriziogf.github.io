---
title: "Building the Commits and Training Hours Heatmaps"
---

The homepage now has two year-long heatmaps: GitHub contributions and workout hours. This post covers how they're built.

---

## The GitHub grid

Both heatmaps are inspired by GitHub's contribution grid. Mine looks a bit bare right now (I'm working on it). I like how the grid shows consistency at a glance, something a bar chart can't do as simply. Training consistency matters to me too, so I built the same grid for my Strava hours.

---

## How it's built

Both charts are static. Nothing is fetched in the browser. They're assembled at build time, and since the training updater pushes daily, the site rebuilds and the squares stay current.

**GitHub data needs no token.** The profile calendar is served as plain markup at `github.com/users/<name>/contributions`, one `<td>` per day with `data-date` and `data-level` (0–4), and the exact count in the tooltip text. Parsing that is less work than authenticating against the GraphQL API, and there's no secret to store in Actions.

**The training data was already there.** The daily updater already pulls a year of Strava activities for the dashboard's monthly trends, so summing each day's moving time is a free aggregation. No extra API calls, just a new `year_daily` block in the YAML.

Rendering is one Astro component used twice, emitting inline SVG. Colors come in as a CSS variable, so each chart uses its source's brand color and both adapt to light and dark mode. GitHub provides its own 0–4 buckets. For hours I picked fixed thresholds (1.5, 3, and 4.5) so a light month actually looks light instead of being normalized to look busy.

I got two things wrong at first. GitHub pads its calendar to whole weeks, so on certain days of the week it returns *tomorrow* as a trailing square. Future days now get skipped. And to make both grids exactly the same width, the training chart draws whatever span GitHub reports instead of its own, so the updater has to pull slightly more than a year to always cover that span. The extra days only feed the squares. **The total in the corner still counts the trailing 365 days, and the dashboard never sees the extra days.**

The last addition was clicking. Each square had a `<title>`, which gives you a tooltip on hover and nothing at all on a phone.
