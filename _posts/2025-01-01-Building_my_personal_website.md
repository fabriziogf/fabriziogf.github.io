---
title: "Building my personal website"
---

I've wanted a personal website for a while. Partly to share technical projects, partly to give myself a reason to write and code more often.

As a Product Manager, most of my day is strategy, prioritization, and execution across teams. I like that work. But I also wanted something of my own: a place to share projects, write about what I'm learning, and work through ideas across product, data science, AI/ML, and sports.

This site is that place.

## Why a personal website

LinkedIn already works as an online resume. I wanted something more flexible: a place to publish writing, share side projects, and keep a portfolio of things I've actually built.

I also wanted a project small enough to finish but open-ended enough to keep improving. A personal site fits. It touches writing, design, some frontend work, and developer tooling all at once.

And I wanted to get back into the habit of making things in public.

## GitHub Pages and Jekyll

I built the site with GitHub Pages, Jekyll, and the Minimal Mistakes theme. A few reasons:

1. It's simple and lightweight.
2. It's easy to host and update through GitHub.
3. Jekyll has a clean model for pages and posts.
4. Minimal Mistakes is well documented and looks good without building everything from scratch.

I used VS Code to work through config files, markdown pages, theme includes, and small styling changes. Good tooling helped even on a project this small.

## What I changed

Once the site was running, I started with the basics:

1. Configuring the author profile
2. Adding links to social accounts
3. Adding a resume link
4. Updating the homepage and About page
5. Small formatting and layout tweaks

Then some personal touches. My favorite was the Strava widget. I spend a lot of time biking, running, and swimming, so it belonged on the site. It makes the page feel like a homepage instead of a static resume.

You can see it on the [About page](/about/).

## What I learned

The project was quick to finish, but it taught me a lot about how Jekyll works:

1. How YAML front matter controls page metadata and layout
2. How the site separates posts, pages, layouts, includes, and configuration
3. How much behavior is driven by `_config.yml`
4. How themes like Minimal Mistakes let you customize without starting over

Even small edits, like changing sidebar links or homepage content, meant figuring out where things lived and how Jekyll builds the final site. It ended up being a real introduction to static-site development, not just a writing exercise.

What surprised me was how much polish comes from small changes. Fixing a few links, tightening spacing, and cleaning up page structure made the site feel much more deliberate.

## This first post

Writing this post was part of the project. It taught me how posts are structured, how filenames and front matter work, and how content gets rendered.

It also made the site feel real. Without any writing on it, a personal website feels like an empty shell. One post changes that.

## What's next

I want this site to be a mix of technical writing, project notes, experiments, and personal interests. Topics I expect to cover:

1. AI and ML tools I'm experimenting with
2. Data science and analytics ideas
3. Product development and technical prototyping
4. Endurance sports and side projects

I don't want it to be overly polished or corporate. **The point is to think in public and document what I'm learning as I go**, not to present a finished version of myself.

You can explore the repository here: [fabriziogf/fabriziogf.github.io](https://github.com/fabriziogf/fabriziogf.github.io)
