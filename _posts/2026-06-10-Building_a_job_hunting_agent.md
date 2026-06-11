---
title: "Building a Job-Hunting Agent from a 30-Million-Resume Playbook"
---

I came across a document that I couldn't stop thinking about: Laszlo Bock's *Apply Within* playbook. Bock ran People Operations at Google — his team sifted more than 30 million resumes, and he personally reviewed over 100,000 applicants. The playbook is what he learned distilled into eight short chapters. It's blunt, specific, and a little uncomfortable to read, because most of it is the opposite of how I've approached job hunting in the past.

So I'm turning it into an agent. This is the first post documenting how I'm building it — and, just as much, the insights from the guide that make it worth building.

---

## The insight that reframes everything

The first chapter is titled "Hiring is rigged," and the argument is that hiring isn't a search for the most qualified person. It's a tired manager picking someone who feels familiar, fast. Most interview decisions are made in the first four minutes and justified afterward.

Bock's point isn't to complain about this. It's that the unfairness is *good news*. If hiring were perfectly meritocratic, you'd have to be the single most qualified person in the room. Since it isn't, you don't. You just have to know how the game is played.

That reframing is what makes the whole thing automatable. The job hunt isn't a mysterious popularity contest — it's a set of repeatable, learnable moves. And repeatable, learnable moves are exactly what an agent should be good at.

---

## The eight insights I want the agent to encode

Reading the playbook, almost every chapter resolves into one sharp, mechanical rule. That's what convinced me an agent was the right form factor — each rule is concrete enough to build a skill around.

**The resume is a formula, not an art.** Every bullet should read "Accomplished [X] as measured by [Y] by doing [Z]." "Managed sorority budget" becomes "Managed a $31,000 budget and invested $10,000 of idle funds in capital notes returning 5% over the year." Same activity, completely different signal. A recruiter spends about six seconds on a resume — vague duties say nothing in six seconds, numbers do.

**You're mostly writing for a robot first.** 97% of Fortune 500 companies screen resumes with AI before a human sees them. So you mirror the job description's exact phrases, spell out acronyms once, and aim for a high keyword match. There's a nice recursion here: I'm using AI to beat the AI screener.

**The cover letter can only lose you the job, not win it.** Its entire purpose is to not screw up. A typo, the wrong company name, "Dear Hiring Manager" instead of a real name — those get you rejected. Spend 30 minutes max, then go back to the resume.

**Referrals get hired 5–10x more often.** And the move to get one is counterintuitive: ask for advice, not a job. The moment you ask for a job, you become a problem to solve and people step away. Ask for fifteen minutes of advice and you'll get it — and sometimes the job too.

**People hire people they like.** Qualifications are a distant second. Be kind to everyone in the lobby (hiring managers ask the receptionist). Make small talk. When you lack the exact experience, reframe rather than fake it — Bock got onto Google's exec team at 33 with three years of HR experience by arguing they didn't need someone with 20.

**Practice is just arithmetic.** 30 likely questions, 2 answers each, 3 reps out loud — about 13.5 hours, spread over a week. Most people skip it because they're afraid of sounding rehearsed, so they sound terrible instead. The few who practice get the jobs.

**Applying is the finish line, not the start.** This is why the chapter on actually applying comes seventh, not first. Start with B-tier companies to fine-tune on lower-stakes interviews, play the volume game (roughly 100 applications → 5 first rounds → 1 offer), and only approach your dream companies once you're sharp.

**Always negotiate.** Your maximum leverage is the single moment between the offer and your signature. A $5,000 raise at 25, compounded over a career, is worth over a million dollars. The risk of politely asking is essentially zero.

---

## Why this is a good fit for an agent

What struck me is how cleanly the playbook decomposes. Each chapter is a self-contained skill with clear inputs and outputs:

- a **Resume Builder** that rewrites bullets into the X/Y/Z formula and enforces the boring-but-critical formatting rules
- an **ATS Optimizer** that scores a resume against a specific job description
- a **Cover Letter / Outbound Email Writer** whose one job is to do no harm while proving you actually researched the company
- a **Networking Assistant** that drafts "ask for advice" outreach with a genuine, specific hook
- an **Interview Prep Coach** that generates the question bank and drills answers in a fixed structure
- a **Pipeline Tracker** that runs the volume game and follow-up cadence
- a **Negotiation Advisor** that knows your market range, your ask, and your walk-away number

Underneath all of them sits one shared **candidate profile** — the single source of truth for my real experience and metrics — and a **company research** capability that several skills draw on. That structure matters because of the playbook's most-repeated warning: don't lie, don't stretch. The agent's job is to surface and sharpen *real* achievements, never to invent them. Constraining it to a profile I've verified keeps it honest by construction.

---

## How I'm building it

I'm keeping it consistent with the lean setup I've written about before: Python 3.12 via `uv`, the Anthropic SDK for tool use, and Claude Code as the build environment. No framework sprawl.

The first thing I did was the least glamorous: I had Claude read the full PDF, then wrote a `CLAUDE.md` that maps every chapter to a planned skill and lays out the build order. The plan is to ship the highest-leverage piece first — the Resume Builder, because the resume "does the actual work" — and only move on once each skill is independently useful and has an eval behind it.

That sequencing is itself stolen from the playbook. Bock saves "actually apply" for chapter seven on purpose: do the unglamorous preparation first, and by the time you click submit, the hard part is already done. Same philosophy for the build.

I'll write up the Resume Builder in Part 2 — including how I evaluate whether an X/Y/Z rewrite is actually better, which turns out to be the genuinely hard problem.
