---
title: "What I'm Taking From How Anthropic Teams Use Claude Code"
---

I've been reading Anthropic's [How Anthropic teams use Claude Code](https://www-cdn.anthropic.com/58284b19e702b49db9302d5b6f135ad8871e7658.pdf). It's a collection of how different internal teams actually use the tool day to day, and a few of the use cases stuck with me — some because they match what I already do, some because they point at gaps I should close.

I'm still working through the full thing. These are first-draft reflections, grouped by the themes that landed for me.

---

## Understanding a codebase you didn't write

Two of the use cases are about onboarding: new hires using Claude Code to navigate an unfamiliar codebase, and teams asking it to explain how a system fits together before touching it.

This is the one I keep coming back to, because it's a real gap at Amazon. Our codebase documentation is not great — onboarding onto a new service often means reading code, pinging the one person who remembers why something works the way it does, and rebuilding context that should have been written down. A tool that can read the actual code and explain it on demand is a partial fix for that. Not a replacement for good docs, but a way to get oriented without blocking on someone else's calendar.

The related practice that caught my attention: **end-of-session documentation updates**. Have Claude summarize what changed and update the docs before you close out. It's the kind of thing everyone agrees they should do and nobody does, because it's friction at exactly the moment you want to be done. Pushing it onto the tool removes the friction. This feeds directly back into the onboarding problem — better docs make the next person's exploration easier. I'm going to start doing this.

---

## Knowing when to let Claude drive

The two use cases I found most useful together are fast prototyping with auto-accept mode and synchronous coding for core features. They're really one idea: matching your level of supervision to what the code is worth.

For new ideas and prototypes, the teams let Claude take the wheel with auto-accept on — but they start from a clean git slate and commit checkpoints often, so anything that goes sideways is one revert away. That's a smart safety net. The autonomy is only comfortable because the cost of being wrong is bounded.

For core business logic and critical fixes, they slow down: detailed prompts, close monitoring, careful review. The quality of the prompt does a lot of the work here.

The real skill is knowing which mode you're in. Peripheral features and prototypes — let it run. Core logic and anything load-bearing — supervise synchronously. I do this informally already, but naming it makes it easier to be deliberate about, and the clean-slate-plus-checkpoints habit is one I should adopt for the prototyping side.

---

## Leverage on the work I was doing anyway

Three more land as straightforward multipliers.

**Test generation and bug fixes.** The teams lean on Claude Code to write more complete tests than they'd write by hand. Tests are the thing that always gets cut when time is short, so handing them to the tool is a clean win. My side projects already live or die on their test suites — this is a habit to push harder on.

**Machine learning concept explanation.** This one has been genuinely great for me. Using it as a learning tool — ask it to explain a concept, then push back until it clicks — has been one of the better ways I've picked up ML ideas. Good to see it's not just me doing this.

**Cross-language code translation.** Teams use it to port code between languages they don't all know well. The selfish read: I mostly only need to be fluent in Python, and lean on the tool when something lives in a language I don't know. :)

---

## What I'm changing

Pulling it together, two things I'll actually do differently:

1. **Start the end-of-session documentation habit** — on my own projects first, where the discipline is cheap to build.
2. **Be deliberate about driving mode** — clean slate and checkpoint commits when I let it run, detailed prompts and close review when the code matters.

The throughline across all seven is that the tool is most useful when you've decided in advance how much to trust it. More notes once I finish the rest of the article.
