# Fabrizio GF — Personal Website

Personal website built with [Jekyll](https://jekyllrb.com/) using the [Minimal Mistakes](https://mmistakes.github.io/minimal-mistakes/) theme, hosted on GitHub Pages.

## Directory Structure

```
.
├── _config.yml                  # Jekyll site-wide configuration (theme, title, author, plugins)
├── index.html                   # Site homepage
├── Gemfile / Gemfile.lock       # Ruby gem dependencies
├── package.json                 # Node.js dev dependencies (e.g. for asset tooling)
├── Rakefile                     # Rake tasks (tests, asset compilation)
├── staticman.yml                # Staticman configuration for static comment submissions
├── minimal-mistakes-jekyll.gemspec  # Gem spec if using the theme as a local gem
├── CHANGELOG.md                 # Upstream theme changelog
├── LICENSE                      # Theme license
│
├── _posts/                      # Published blog posts (filename: YYYY-MM-DD-title.md)
├── _pages/                      # Static pages (about, home, archive, 404)
├── _data/                       # YAML data files
│   ├── navigation.yml           # Site navigation links
│   ├── ui-text.yml              # Localised UI strings
│   └── _training_data/          # Raw training/fitness data used by posts and notebooks
│
├── _layouts/                    # Page layout templates (HTML)
├── _includes/                   # Reusable HTML partials (header, footer, SEO tags, etc.)
├── _sass/                       # SASS source files
│   ├── minimal-mistakes/        # Theme SASS partials
│   └── minimal-mistakes.scss    # Main SASS entry point
│
├── assets/                      # Compiled/static assets served directly
│   ├── css/                     # Compiled stylesheets
│   ├── js/                      # JavaScript files
│   └── images/                  # Site images
│
├── notebooks/                   # Jupyter notebooks for data analysis posts
│   └── fit_training_analysis.ipynb
│
├── _garage/                     # Staging area / work-in-progress content not yet published
├── docs/                        # Theme documentation
├── download/                    # Downloadable files linked from pages
└── test/                        # Theme test suite
```

The site is available at https://fabriziogf.github.io/
