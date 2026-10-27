---
title: "What I'm Taking From How Anthropic Teams Use Claude Code"
---

I've been reading Anthropic's [How Anthropic teams use Claude Code](https://www-cdn.anthropic.com/58284b19e702b49db9302d5b6f135ad8871e7658.pdf). It collects how different internal teams use the tool day to day. A few of the use cases stuck with me, some because they match what I already do and some because they point at gaps I should close.

I haven't finished it yet. These are first reflections, grouped by the themes that landed for me.

---

## Understanding a codebase you didn't write

Two of the use cases are about onboarding: new hires using Claude Code to find their way around an unfamiliar codebase, and teams asking it to explain how a system fits together before touching it.

This is the one I keep coming back to, because it's a real gap at Amazon. Our codebase documentation isn't great. Onboarding onto a new service often means reading code, pinging the one person who remembers why something works the way it does, and rebuilding context that should have been written down. A tool that reads the actual code and explains it on demand is a partial fix. It doesn't replace good docs, but it lets you get oriented without waiting on someone else's calendar.

A related practice caught my attention: **end-of-session documentation updates**. Have Claude summarize what changed and update the docs before you close out. Everyone agrees they should do this and nobody does, because it adds friction right when you want to be done. Handing it to the tool removes that friction. It also feeds back into the onboarding problem, since better docs make the next person's exploration easier. I'm going to start doing this.

---

## When to let Claude drive

The two use cases I found most useful together are fast prototyping with auto-accept mode and synchronous coding for core features. They're really one idea: match how closely you supervise to what the code is worth.

For new ideas and prototypes, the teams let Claude take the wheel with auto-accept on. But they start from a clean git state and commit checkpoints often, so anything that goes wrong is one revert away. That's a smart safety net. The autonomy is only comfortable because the cost of being wrong is limited.

For core business logic and critical fixes, they slow down: detailed prompts, close monitoring, careful review. The quality of the prompt does a lot of the work here.

The real skill is knowing which mode you're in. Peripheral features and prototypes: let it run. Core logic and anything load-bearing: supervise closely. I already do this informally, but naming it helps me be deliberate about it. The clean-slate-plus-checkpoints habit is one I should adopt for prototyping.

---

## Leverage on work I already do

Three more are straightforward multipliers.

**Test generation and bug fixes.** The teams use Claude Code to write more complete tests than they would by hand. Tests are the first thing cut when time is short, so handing them to the tool is an easy win. My side projects already live or die by their test suites, so this is a habit to push harder on.

**Explaining ML concepts.** This one has been great for me. Using it as a learning tool (ask it to explain a concept, then push back until it clicks) has been one of the better ways I've picked up ML ideas. Good to see it's not just me.

**Cross-language code translation.** Teams use it to port code between languages they don't all know well. My selfish takeaway: I really only need to be fluent in Python and can lean on the tool when something lives in a language I don't know. :)

---

## What I'm changing

Two things I'll actually do differently:

1. **Start the end-of-session documentation habit**, on my own projects first, where it's cheap to build.
2. **Be deliberate about driving mode**: clean slate and checkpoint commits when I let it run, detailed prompts and close review when the code matters.

**The common thread is that the tool is most useful when you've decided in advance how much to trust it.** More notes once I finish the rest.
