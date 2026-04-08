---
title: "Building my personal website"
---

I have wanted to build a personal website for a while, partly as a way to showcase some of my technical interests and partly as a forcing function to write and code more consistently.

As a Product Manager, a lot of my day-to-day work is focused on strategy, prioritization, and execution across teams. I enjoy that work, but I also wanted a space that felt a little more personal and experimental. I wanted somewhere to share projects, write about things I am learning, and document ideas that sit at the intersection of product, data science, AI/ML, and sports.

This site is my attempt to create that space.

## Why build a personal website?

For me, the point of a personal website is not just to have an online resume. LinkedIn already does that well enough. What I wanted was something more flexible: a place where I could publish writing, share side projects, and gradually build a portfolio of things I have actually made.

I also wanted a project that was small enough to finish, but open-ended enough to keep improving over time. A personal site is perfect for that. It lets me work on writing, design, lightweight frontend customization, and developer tooling all in one place.

Another motivation was simply to get back into the habit of making things in public.

## Building a GitHub Pages site with Jekyll

I decided to build the site with GitHub Pages, Jekyll, and the Minimal Mistakes theme.

That combination appealed to me for a few reasons:

1. It is simple and lightweight.
2. It is easy to host and update through GitHub.
3. Jekyll has a straightforward content model for pages and posts.
4. Minimal Mistakes has strong documentation and enough structure to look polished without forcing me to build everything from scratch.

I liked this particular theme because it gave me a clean starting point while still letting me customize the homepage, About page, sidebar, social links, and overall formatting.

I also used VS Code as part of the process, partly because I wanted to explore some of the newer AI-assisted coding workflows. Even on a relatively small project like this one, it was helpful to move quickly through configuration files, markdown pages, theme includes, and small styling changes without constantly switching contexts.

## What I changed

Once the site was up and running, I started customizing it to make it feel more like my own.

Some of the first changes were basic but important:

1. Configuring the author profile
2. Adding links to relevant social media accounts
3. Adding a resume link
4. Updating the homepage and About page copy
5. Making small formatting and layout tweaks across the site

From there, I started making more personalized changes. I wanted the site to reflect both my professional background and some of the interests that take up a lot of my free time.

One feature I especially liked adding was the Strava widget. I spend way too much time biking, running, and swimming, so it felt fitting to include that on the site as well. It makes the site feel a little less like a static resume and a little more like an actual personal homepage.

You can see that on the [About page](/about/).

## What I learned while building it

One of the nice things about this project is that it was simple enough to get working quickly, but still gave me a chance to learn the structure of a Jekyll site in more detail.

A few things became much clearer once I started editing the site directly:

1. How Jekyll uses YAML front matter to control page metadata and layout behavior
2. How the site separates posts, pages, layouts, includes, and configuration
3. How much of the site behavior is driven by `_config.yml`
4. How themes like Minimal Mistakes make it easy to customize a site without writing everything from scratch

Even small edits, like changing sidebar links or adjusting homepage content, required understanding where the text actually lived and how Jekyll assembles the final site. That made the project feel like a good introduction to static-site customization rather than just a writing exercise.

One thing that surprised me was how much polish comes from small changes. Updating a few sidebar links, tightening spacing, and improving page structure can make a website feel much more intentional.

## Writing this first post

Writing this post was part of the project too.

It forced me to learn how posts are structured, how filenames and front matter work, and how content gets rendered into the site. It also made the site feel real. Until there is actual writing on a personal website, it is easy for it to feel like an unfinished shell.

Publishing even one post changes that. It turns the site from a setup project into an ongoing habit.

## What is next

Over time, I want this site to become a mix of technical writing, project notes, experiments, and personal interests.

Some of the topics I expect to write about include:

1. AI and ML tools that I am experimenting with
2. Data science and analytics ideas
3. Product development and technical prototyping
4. Endurance sports and side projects that are personally interesting to me

I do not want the site to be overly polished or overly corporate. I want it to be a place to think in public, share work, and keep building.

That is really the point of the site: not just to present a finished version of myself, but to document what I am learning as I go.

You can explore the repository here: [fabriziogf/fabriziogf.github.io](https://github.com/fabriziogf/fabriziogf.github.io)
