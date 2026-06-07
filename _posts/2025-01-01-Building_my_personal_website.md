---
title: "Building my personal website"
---

I've wanted a personal website for a while. Part of it was wanting a place to share technical projects. Part of it was wanting a reason to write and code more consistently.

As a Product Manager, most of my day is strategy, prioritization, and execution across teams. I enjoy that work. But I also wanted something more personal — somewhere to share projects, write about things I'm learning, and document ideas at the intersection of product, data science, AI/ML, and sports.

This site is that space.

## Why build a personal website?

For me, a personal website isn't just an online resume. LinkedIn already does that. I wanted something more flexible: a place to publish writing, share side projects, and build a portfolio of things I've actually made.

I also wanted a project small enough to finish but open-ended enough to keep improving. A personal site is good for that. It lets you work on writing, design, lightweight frontend customization, and developer tooling all in one place.

Another reason: I wanted to get back into the habit of making things in public.

## Building it with GitHub Pages and Jekyll

I built the site with GitHub Pages, Jekyll, and the Minimal Mistakes theme.

That combination made sense for a few reasons:

1. It's simple and lightweight.
2. It's easy to host and update through GitHub.
3. Jekyll has a clean content model for pages and posts.
4. Minimal Mistakes is well-documented and looks polished without requiring me to build everything from scratch.

I used VS Code to work through configuration files, markdown pages, theme includes, and small styling changes. Even on a small project like this, having good tooling made a difference.

## What I changed

Once the site was running, I started customizing it.

The basics first:

1. Configuring the author profile
2. Adding links to social accounts
3. Adding a resume link
4. Updating the homepage and About page
5. Small formatting and layout tweaks

Then more personal changes. One feature I liked adding was the Strava widget. I spend a lot of time biking, running, and swimming, so it made sense to include that on the site. It makes it feel less like a static resume and more like an actual homepage.

You can see it on the [About page](/about/).

## What I learned

This project was simple enough to finish quickly, but it taught me a lot about how Jekyll works.

A few things that became clear once I started editing directly:

1. How Jekyll uses YAML front matter to control page metadata and layout
2. How the site separates posts, pages, layouts, includes, and configuration
3. How much behavior is driven by `_config.yml`
4. How themes like Minimal Mistakes make it easy to customize without starting from scratch

Even small edits — changing sidebar links, adjusting homepage content — required understanding where things actually lived and how Jekyll builds the final site. That made it feel like a real introduction to static-site development, not just a writing exercise.

One thing that surprised me: how much polish comes from small changes. Updating a few links, tightening spacing, and cleaning up the page structure can make a site feel much more intentional.

## Writing this first post

Writing this post was part of the project too.

It forced me to learn how posts are structured, how filenames and front matter work, and how content gets rendered. It also made the site feel real. Until there's actual writing on a personal website, it's easy for it to feel like an unfinished shell.

Publishing one post changes that.

## What's next

Over time, I want this site to be a mix of technical writing, project notes, experiments, and personal interests.

Some topics I expect to write about:

1. AI and ML tools I'm experimenting with
2. Data science and analytics ideas
3. Product development and technical prototyping
4. Endurance sports and side projects

I don't want the site to be overly polished or corporate. I want it to be a place to think in public, share work, and keep building.

That's really the point — not to present a finished version of myself, but to document what I'm learning as I go.

You can explore the repository here: [fabriziogf/fabriziogf.github.io](https://github.com/fabriziogf/fabriziogf.github.io)
