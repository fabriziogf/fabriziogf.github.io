---
title: "My Vibe Coding Setup for AI Prototyping"
---

Over the last few weeks I put together a coding setup for building AI projects in my spare time, without turning my laptop into a science experiment. This post describes what's in it and why.

## Why this setup

I didn't want a maximalist setup: fifteen half-configured tools, five overlapping agent frameworks, and a pile of MCP servers I'd never use. I wanted something lean that could still support the projects I actually want to build: agent workflows, eval tools, quick prototypes, and assistants for things I care about like triathlon, AI/ML, and sports.

The result is what I call my "vibe coding" setup. It's small and fast, but solid enough to build real things.

## Core environment

The base is **Node.js** and **pnpm** for JavaScript, and **Python 3.12** managed through **uv** for anything agentic or model-related. Node gives me MCP servers and browser tooling. Python is still the easiest place to build agent workflows and eval harnesses.

I also installed **Docker Desktop** for containerized tools, but I try not to depend on it. I want to open my laptop and start building right away.

The center of it all is **Claude Code**, my main coding interface. It supports MCP natively and runs as a terminal-first agent with full filesystem and shell access. So the real question was which external tools to wire in. I kept that list short.

## MCP tools

**Context7** is my current-docs layer. Models are often directionally right but fuzzy on fast-changing library details. Context7 gives the agent fresher documentation, which makes prototyping less brittle.

**Playwright MCP** (or Claude in Chrome) is the most important non-docs tool here. I want to build AI products that do things, not just talk. Browser control makes room for richer prototypes, web agents, and light testing.

**Filesystem MCP** is scoped to one projects directory, not my whole machine. That was on purpose. I want the agent to read, write, and organize project files, but not to have open access to everything on my computer. Limiting it to `~/ai-projects` is cleaner and safer.

**GitHub MCP** lets the agent work with repositories, issues, PRs, and code. That helps with my own projects and builds habits that carry over to real engineering workflows.

**Hugging Face MCP** was an easy call. It gives Claude Code paper search, model and dataset discovery, and Spaces. When I'm turning a paper into an experiment or exploring a new model family, I don't have to leave the workflow for browser tabs.

## Agent framework

On the Python side I standardized on the **Anthropic SDK** and Claude's native tool use. I did this to avoid framework sprawl. There are a lot of agent libraries right now, and it's easy to spend more time collecting them than building with them. The SDK handles tool use, multi-turn workflows, and structured agents without a heavy abstraction layer.

## The stack

* **Node.js + pnpm** for JS tooling and MCP compatibility
* **uv + Python 3.12** for agents, evals, and experiments
* **Docker Desktop** for optional containerized tools
* **Claude Code** as the main environment
* **Context7** for up-to-date library docs
* **Playwright MCP** for browser control
* **Filesystem MCP** for project-scoped file access
* **GitHub MCP** for repository and development workflows
* **Hugging Face MCP** for paper search, model discovery, and ML research
* **Anthropic SDK** as the main Python agent framework

## What I can build with it

The stack isn't built for following tutorials. It's built for making small, technically credible things quickly. For example:

* an eval workbench for prompts, tools, and models
* a PRD-to-prototype agent that generates working app scaffolds
* a triathlon training copilot with structured planning logic
* a research assistant that combines data retrieval and analysis
* a paper-to-experiment translator for ML and AI research

## Why it matters to me

The point is to cut the friction between an idea and a working version of it. I want to go from "this would be interesting to build" to a prototype in a night or a weekend.

I also think technical depth for a PM looks different in AI. It used to mean talking about metrics, systems, and cross-functional execution. Those still matter. But in AI it also means prototyping quickly, wiring tools together, reasoning about agents and evals, and building working artifacts that make product thinking concrete. Claude Code has sped that loop up a lot.

**Keep the stack small, keep the feedback loop fast, and make it easy to build real AI products on nights and weekends.**
