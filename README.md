# Fabrizio GF — Personal Website

Personal website built with [Astro](https://astro.build/), deployed to GitHub Pages via GitHub Actions.

## Directory Structure

```
.
├── astro.config.mjs             # Astro configuration (site URL, sitemap, code themes)
├── package.json                 # Node dependencies and scripts
├── tsconfig.json                # TypeScript configuration
│
├── src/
│   ├── content.config.ts        # Content collections (posts load from _posts/)
│   ├── layouts/                 # Base shell, markdown page layout
│   ├── lib/                     # Post helpers, training-data loader
│   ├── pages/                   # Routes: index, year-archive, projects, training, about, [slug]
│   └── styles/global.css        # Design tokens ("Gridline") — light + dark themes
│
├── public/                      # Static files served as-is
│   ├── assets/images/           # Site images
│   └── download/                # CV and other downloads
│
├── _posts/                      # Blog posts (filename: YYYY-MM-DD-Slug.md → served at /Slug/)
├── _data/
│   ├── training_data.yml        # Machine-generated dashboard data (daily cron)
│   └── _training_data/          # Raw training/fitness data archives
│
├── scripts/                     # Training dashboard updater (Strava + TrainingPeaks)
├── notebooks/                   # Jupyter notebooks for data analysis posts
├── _garage/                     # Staging area / work-in-progress content not yet published
│
└── .github/workflows/deploy.yml # Build + deploy to GitHub Pages on push to main
```

## Development

```bash
npm install
npx astro dev        # http://localhost:4321
npm run build        # static build to dist/
```

## Deployment

Push to `main`. The GitHub Actions workflow builds the site and publishes it to GitHub Pages (Pages source: "GitHub Actions").

The training dashboard (`/training/`) is fed by `_data/training_data.yml`, rewritten daily by `scripts/update_training_data.py` (Cowork cron job); its push to `main` triggers a rebuild, keeping the dashboard fresh.
