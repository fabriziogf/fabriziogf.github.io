# Fabrizio GF — Personal Website

Personal website built with [Astro](https://astro.build/), deployed to GitHub Pages via GitHub Actions. Custom "Gridline" design, light + dark themes.

Live at [fabriziogf.github.io](https://fabriziogf.github.io).

## Directory Structure

```
.
├── astro.config.mjs             # Astro config (site URL, sitemap, Shiki code themes)
├── package.json                 # Node dependencies and scripts
├── tsconfig.json                # TypeScript configuration
├── CLAUDE.md                    # Working context for Claude Code
│
├── src/
│   ├── content.config.ts        # Content collection — loads _posts/, preserves exact filenames as slugs
│   ├── components/
│   │   └── CalendarHeatmap.astro # GitHub-style year calendar (geometry + styling only)
│   ├── layouts/
│   │   ├── Base.astro           # Site shell: head, nav, footer
│   │   └── MarkdownPage.astro   # Layout for standalone markdown pages
│   ├── lib/
│   │   ├── posts.ts             # Post collection helpers, filename → date + slug parsing
│   │   ├── training.ts          # Reads _data/training_data.yml at build time
│   │   ├── github.ts            # GitHub contribution calendar, fetched at build time
│   │   ├── projects.ts          # Project list, shared by /projects/ and the homepage
│   │   └── og.ts                # Open Graph image generation (satori + resvg)
│   ├── pages/
│   │   ├── index.astro          # Homepage: latest writing, now building, training
│   │   ├── year-archive.astro   # All posts by year
│   │   ├── projects.astro       # Project cards
│   │   ├── training.astro       # Training dashboard (Chart.js)
│   │   ├── about.md             # About page
│   │   ├── [slug].astro         # Blog post route
│   │   ├── og/[...slug].png.ts  # Generated OG images, one per page
│   │   ├── feed.xml.js          # RSS feed
│   │   ├── 404.astro
│   │   ├── yonkers-plan.md      # Standalone training plan pages
│   │   └── yonkers-lifting.md
│   └── styles/global.css        # Design tokens ("Gridline") — light + dark themes
│
├── public/                      # Static files served as-is
│   ├── assets/images/           # Site images
│   ├── assets/css/, assets/js/  # Legacy Jekyll theme assets — unused, pending cleanup
│   └── download/                # CV
│
├── _posts/                      # Blog posts (YYYY-MM-DD-Slug.md → served at /Slug/)
├── _data/
│   ├── training_data.yml        # Machine-generated dashboard data (daily cron)
│   ├── swim_prs.yml             # Swim personal records
│   └── _training_data/          # Raw .FIT files from Garmin / Zwift
│
├── scripts/                     # Training dashboard pipeline
│   ├── update_training_data.py  # Daily updater — writes _data/training_data.yml, commits, pushes
│   ├── strava_client.py         # Stdlib-only Strava OAuth client + sport map
│   ├── strava_auth.py           # One-time OAuth bootstrap
│   ├── strava_prs.py            # Run-PR cache logic
│   └── strava_backfill_prs.py   # One-time history seed
│
├── docs/workout-library.md      # Ironman workout library (key sessions, 2023–2026)
├── notebooks/                   # Jupyter notebooks for data analysis posts
├── _garage/                     # Archived Jekyll site + unpublished drafts
│
└── .github/workflows/deploy.yml # Build + deploy to GitHub Pages on push to main
```

## Development

```bash
npm install
npm run dev          # http://localhost:4321
npm run build        # static build to dist/
npm run preview      # serve the built site
```

## Content conventions

**Posts** live in `_posts/` as `YYYY-MM-DD-Slug.md`, with front matter that only needs a `title`. The content loader keeps the exact filename as the id, so a post is served at `/Slug/` with no date prefix and no slugifying — this preserves the Jekyll-era URLs. Internal links between posts use that same form: `/Slug/`.

**Projects** are defined once in `src/lib/projects.ts` and consumed by both `/projects/` and the homepage's "Now building" cell. The list is newest-first and the homepage shows the top entries, so adding a project at the top surfaces it in both places.

**Pages** are either `.astro` routes or standalone `.md` files using `MarkdownPage.astro`.

## Deployment

Push to `main`. The GitHub Actions workflow builds the site and publishes it to GitHub Pages (Pages source: "GitHub Actions").

The training dashboard (`/training/`) is fed by `_data/training_data.yml`, rewritten daily by `scripts/update_training_data.py` (Cowork cron job). Activity data comes from Strava, fitness metrics (CTL/ATL/TSB) and TSS from TrainingPeaks. The script's push to `main` triggers a rebuild, keeping the dashboard fresh.

The homepage heatmaps and OG images are also generated at build time — GitHub contributions are fetched from the public profile fragment, and each page's social image is rendered with satori.
