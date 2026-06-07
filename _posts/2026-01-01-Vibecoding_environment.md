---
title: "My Vibe Coding Setup for AI Prototyping"
---

## Why I wanted a setup like this

Over the last few weeks I've been putting together a coding setup that makes it easy to build AI projects quickly in my spare time — without turning my laptop into a science experiment.

The goal wasn't a maximalist setup. I didn't want fifteen half-configured tools, five overlapping agent frameworks, and a pile of MCP servers I'd never use. I wanted something lean, practical, and technically serious enough to support the kinds of projects I actually want to build: agent workflows, eval tools, rapid prototypes, and domain-specific assistants around things I care about — triathlon, AI/ML, and sports.

The result is what I think of as my "vibe coding" setup: a small stack that's fast and flexible, but grounded enough to build real things.

## The core environment

At the base, I use **Node.js** and **pnpm** for the JavaScript side, and **Python 3.12** managed through **uv** for everything agentic and model-related. Node gives me access to MCP servers and browser tooling. Python is still the easiest place to build agent workflows and eval harnesses.

I also installed **Docker Desktop** for containerized tools, though I'm trying not to depend on it unless I need to. I prefer to keep the workflow simple enough that I can open my laptop and start building immediately.

The center of the setup is **Claude Code** — my main coding interface. It supports MCP natively and runs as a terminal-first agent with full filesystem and shell access. The real question was: which external tools are worth wiring in?

I kept that list short.

## The MCP tools I chose

**Context7** is my "current docs" layer. One of the biggest problems with AI-assisted coding is that models are often directionally right but fuzzy on rapidly changing library details. Context7 closes that gap by giving the agent access to fresher documentation. It makes rapid prototyping feel less brittle.

**Playwright MCP** (or Claude in Chrome) is probably the most important non-docs tool in the setup. I'm interested in building AI products that do things, not just talk. Browser control opens the door to richer prototypes, web agents, and lightweight testing workflows.

**Filesystem MCP** is scoped to a specific projects directory rather than my whole machine. That was a deliberate choice. I wanted the coding environment to be able to read, write, and organize project files — but not have open-ended access to everything on my computer. Constraining it to `~/ai-projects` keeps the workflow cleaner and safer.

**GitHub MCP** makes the setup feel more real. Once GitHub is connected, the environment can reason about repositories, issues, PRs, and code. That's useful both for building my own projects and for developing habits that matter in real engineering workflows.

**Hugging Face MCP** was an easy call. It gives Claude Code access to paper search, model and dataset discovery, and Spaces. When I'm building a paper-to-experiment pipeline or exploring a new model family, I don't have to break out of the workflow and search through browser tabs.

## My main agent framework

On the Python side, I standardized on the **Anthropic SDK** and Claude's native tool-use and agent capabilities. That was a deliberate choice to avoid framework sprawl. There are a lot of agent libraries right now, and it's easy to spend more time collecting them than building with them. The Anthropic SDK is expressive enough for tool use, multi-turn workflows, and structured agents without a heavy abstraction layer on top.

## The stack at a glance

* **Node.js + pnpm** for JS tooling and MCP compatibility
* **uv + Python 3.12** for agents, evals, and experiments
* **Docker Desktop** for optional containerized tools
* **Claude Code** as the main environment
* **Context7** for up-to-date external library docs
* **Playwright MCP** for browser control
* **Filesystem MCP** for project-scoped file access
* **GitHub MCP** for repository and development workflow integration
* **Hugging Face MCP** for paper search, model discovery, and ML research
* **Anthropic SDK** as the main Python agent framework

## What this setup lets me build

What I like most about this stack is that it matches the kind of builder I want to be. It's not optimized for tutorials. It's optimized for making small, technically credible things quickly.

With this setup I can build:

* an eval workbench for prompts, tools, and models
* a PRD-to-prototype agent that generates working app scaffolds
* a triathlon training copilot with structured planning logic
* a research assistant that combines data retrieval and analysis
* a paper-to-experiment translator for ML and AI research

## Why this matters to me

The point of the setup is reducing friction between idea and implementation. I want to go from "this would be interesting to build" to a working prototype in a night or a weekend.

I also think technical depth looks different in AI than it used to. For a long time, showing technical ability as a PM meant talking about metrics, systems, and cross-functional execution. Those things still matter. But in AI, technical depth also means being able to prototype quickly, wire tools together, reason about agents and evals, and build working artifacts that clarify product thinking. Claude Code, in particular, has changed how fast that loop can move.

That's what this setup is for.

**Keep the stack small, keep the feedback loop fast, and make it easy to build real AI products on nights and weekends.**
