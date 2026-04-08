---
title: "My Vibe Coding Setup for AI Prototyping"
---

Over the last few weeks, I’ve been trying to put together a coding setup that makes it easy to build AI projects quickly in my spare time without turning my laptop into a science experiment.

My goal was not to create the most maximalist setup possible. I did not want fifteen half-configured tools, five overlapping agent frameworks, and a giant pile of MCP servers I would never use. I wanted something lean, practical, and technically serious enough to support the kinds of projects I actually want to build: agent workflows, eval tools, rapid prototypes, research copilots, and domain-specific assistants around things I genuinely care about, like triathlon, AI/ML learning, and sports.

The result is what I think of as my “vibe coding” setup: a small stack that feels fast, modern, and flexible, but still grounded enough to build real things.

At the base of the setup, I use **Node.js** and **pnpm** for the JavaScript side of the world, and **Python 3.12** managed through **uv** for everything agentic, experimental, and model-related. I like this combination because it keeps both ecosystems available without making environment management painful. Node gives me access to the growing universe of MCP servers and browser tooling, while Python remains the easiest place to build agent workflows, eval harnesses, and experimentation pipelines.

For containerized tools and future extensibility, I also installed **Docker Desktop**, although I am trying not to depend on it unless I need to. I prefer to keep the core workflow simple enough that I can open my laptop and start building immediately.

The center of the setup is **Codex**, which I’m using as the main coding interface. Since Codex supports MCP, the real question became: which external tools are actually worth wiring in?

I decided to keep that list intentionally short.

The first MCP I added was the **OpenAI Developer Docs MCP**. This is the one that keeps me from constantly context-switching into browser tabs every time I need to double-check the latest syntax, SDK patterns, or agent guidance. If I’m building with the OpenAI stack, I want the docs available directly inside the coding workflow.

The second was **Context7**, which I think of as my “current docs” layer. One of the biggest problems with AI-assisted coding is that models are often directionally helpful but fuzzy on rapidly changing library details. Context7 helps close that gap by giving the agent access to fresher documentation for frameworks and packages. It makes rapid prototyping feel less brittle.

The third was **Playwright MCP**, which is probably the most important non-docs tool in the whole setup. I’m interested in building AI products that do things, not just talk. Playwright gives the environment the ability to interact with web apps, navigate pages, and support browser-based workflows. That opens the door to richer prototypes, web agents, product demos, and lightweight testing.

Next, I added the **Filesystem MCP**, but scoped to a specific projects directory rather than my whole machine. That was an important design choice for me. I wanted the coding environment to be able to read, write, search, and organize project files, but I did not want to create a setup where an agent effectively has open-ended access to everything on my computer. Constraining it to a dedicated `~/ai-projects` folder keeps the workflow cleaner and safer.

Finally, I added the **GitHub MCP**, which makes the whole setup feel much more real. Once GitHub is connected, the environment can reason about repositories, issues, PRs, and code in a way that is much closer to an actual working engineering workflow. That is useful both for building my own projects and for developing the kinds of habits that matter in real AI product and prototyping environments.

On the Python side, I chose to standardize on the **OpenAI Agents SDK** as my main framework. That was a deliberate decision to avoid framework sprawl. There are a lot of agent libraries right now, and it is easy to fall into the trap of collecting them instead of building with them. I wanted one primary framework that supports tools, handoffs, and structured agent workflows without adding too much abstraction too early.

So the overall setup is pretty simple:

* **Node.js + pnpm** for JS tooling and MCP compatibility
* **uv + Python 3.12** for agents, evals, and experiments
* **Docker Desktop** for optional containerized tools
* **Codex** as the main environment
* **OpenAI Docs MCP** for first-party documentation
* **Context7** for up-to-date external library docs
* **Playwright MCP** for browser control
* **Filesystem MCP** for project-scoped file access
* **GitHub MCP** for repository and development workflow integration
* **OpenAI Agents SDK** as the main Python agent framework

What I like most about this stack is that it matches the kind of builder I want to become. It is not optimized for tutorials. It is optimized for making small, technically credible things quickly.

With this setup, I can build:

* an eval workbench for prompts, tools, and models
* a PRD-to-prototype agent that generates working app scaffolds
* a triathlon training copilot with structured planning logic
* an NBA or NFL research assistant that combines data retrieval and analysis
* a paper-to-experiment translator for ML and AI research workflows

That is really the point of the setup. It is less about the tools themselves and more about reducing friction between idea and implementation. I want to be able to go from “this would be interesting to build” to a working prototype in a night or a weekend.

I also like that this setup reflects a broader shift in how I think about technical depth. For a long time, showing technical ability as a product manager often meant talking about metrics, systems, prioritization, and cross-functional execution. Those things still matter. But in AI, I increasingly think technical depth also means being able to prototype quickly, wire tools together, reason about agents and evals, and build working artifacts that clarify product thinking.

That is what this setup is for.

It is my attempt to create a lightweight, modern environment that supports serious experimentation without requiring a massive time investment just to get started.

If I were summarizing the philosophy in one sentence, it would be this:

**Keep the stack small, keep the feedback loop fast, and make it easy to build real AI products on nights and weekends.**