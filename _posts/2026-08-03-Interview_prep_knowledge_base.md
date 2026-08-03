---
title: "Turning Interview Prep Into a Knowledge Base"
---

I recently [wrote about the knowledge base](/Product_knowledge_base/) I'm building for my product and AI work — how it's structured and how I keep it current. This post is about what actually went into it first, and where that material came from.

It came from a folder in my Documents called `Job Search`. It has 172 files in it. Until recently it was a graveyard.

That's the honest description. Job search folders accumulate the way garages do. Every application generates a tailored resume. Every phone screen generates a study guide. Every onsite generates a prep doc, a case deck, a list of questions to ask, and a `_garage` folder where the previous three versions go to die. Then you take a job, or you don't, and the whole thing goes quiet.

What made me look at it again was noticing something uncomfortable: the most rigorous writing I'd done was sitting in that folder. Not in a PRD. Not in a strategy doc. In interview prep.

That's a strange thing to admit, so let me explain why it's true, and what I did about it.

---

## Why interview prep is good source material

Interview prep has a property most work writing doesn't: an adversarial reader.

When you write a PRD, the reader is a colleague who already shares your context and mostly wants to know what to build. When you write a study guide for a technical interview, the imagined reader is a skeptical expert who will ask "why?" three times and is looking for the seams in your understanding. You write differently for that reader. You go a layer deeper than you'd otherwise bother to, because you can feel exactly where you'd get caught.

Prep also forces synthesis across sources. To prepare for a platform role you read engineering blogs, papers, product announcements, and job descriptions, and then you compress all of it into something you can say out loud in ninety seconds. Compression under a speaking constraint is a real filter. Vague ideas don't survive it.

The third property is less flattering but just as useful: prep is where you're most honest about your own gaps. One guide in that folder has a section that says, in effect, "you don't have deep RAG project experience, here's how you bridge that credibly without overclaiming." You don't write that sentence about yourself anywhere else.

So the folder wasn't a graveyard. It was a badly organized library.

---

## What was actually in there

The 172 files broke into three categories, and only one of them mattered.

**About a hundred were resumes.** Versions and re-versions, tailored per company, per role family, per ATS. Zero durable knowledge. These are artifacts of a process, not products of thinking.

**A handful were company research.** Market share tables, revenue figures, product roadmaps, competitive positioning. This is the category I was most tempted by and most wrong about. It reads as substantial because it's dense with numbers. But it has a shelf life measured in months, and almost none of it generalizes. A competitor's market share in a given quarter isn't knowledge. It's a fact with an expiration date.

**Fifteen or so were study guides and cheat sheets, and those were the whole point.** Agent architecture. Evaluation frameworks for agentic products. Metrics. Experimentation and causal inference. Platform migration strategy. Prioritization under a hard deadline. Engineering concepts for a PM who has to be credible with engineers without pretending to be one.

There was also one document I didn't expect to be valuable: a design handoff brief I'd written for a take-home case presentation. It was ostensibly about fonts and slide layouts. Buried in it were the load-bearing ideas of the entire case, stated more plainly than they were on any slide, because I was explaining them to someone who had to preserve them without understanding the domain. Writing for a designer forced a clarity that writing for a hiring panel didn't.

---

## The generalization problem

Here's the constraint that shaped everything: most of this material was company-specific, and I wanted the knowledge base to be public.

That could have been a blocker. It turned out to be the most useful editorial rule I've applied to my own notes.

The rule was: **extract the concept, drop the instance.** Not "here's how Company X handles tool schema versioning" but "tool schemas are API contracts, and every change is a migration event for every team downstream." Not "here's that company's eval stack" but "agent quality, retrieval quality, and end-to-end quality are independent failure modes, and the aggregate metric is the enemy of root cause analysis."

What surprised me is how much *stronger* the notes got. The company-specific framing had been doing a lot of hiding. When you write "Team A needs streaming, Team B needs eval integration, six weeks, go," you can produce a confident-sounding answer without ever articulating the general principle. Strip the scenario out and you're forced to say the actual thing: *platform prioritization is multiplier math, not feature math.* That sentence is worth more than the worked example it came from.

The same rule killed a lot of material, and it should have. Company values, interview logistics, "questions to ask your interviewer," the competitive research. All of it went. So did every personal detail, every resume line, every "lead with your edge, you led 40 engineers" passage. Those were scaffolding for a specific conversation on a specific day, not knowledge.

---

## What ended up in it

Thirty-one topics across six areas.

**AI agents.** What actually makes something an agent, and why the useful question is never "is this an agent?" but "what does it do autonomously, and what happens when a wrong action goes through?" The ReAct loop and its four termination conditions. The four memory types. Tool schema design, including the observation that an agent with fifty tools makes *worse* selections than one with ten, because the model has to reason over a noisier action space. Orchestration patterns, with a strong bias toward starting single-agent and making the architecture earn its complexity. Guardrails as three distinct layers. Why agent cost grows quadratically rather than linearly with step count.

**Evaluation.** The area I care most about, and where the gap between good teams and bad teams is widest. The three-layer decomposition, and the argument that a single aggregate quality metric actively prevents root cause analysis. Golden trace datasets, where the hard part is representative sampling rather than labeling. LLM-as-judge, its four known biases, and the claim that the rubric matters far more than the judge model. The gap between offline and online eval as the place quality surprises live. And eval infrastructure as a product with its own users and roadmap, not a one-time engineering task.

**Retrieval and context.** RAG architecture and specifically where it breaks. Dense versus sparse versus hybrid. Context engineering, prompt anatomy, and treating prompts as code with regression tests and rollback triggers.

**Platform PM.** The migration playbook: audit, contract, parallel run, sunset. Its central claim is that migrations fail socially before they fail technically, and that the four sources of resistance need four genuinely different interventions. Throwing engineering support at an institutional resistance problem doesn't work.

**Measurement.** Causal inference for when you can't randomize. Goodhart's Law as the dominant failure mode in AI products rather than an abstraction. Why containment rate must never be read alone. And the context on-off test, which is the cleanest way I know to answer whether personalization caused an improvement or the automation just got better.

**AI product strategy.** The autonomy throttle — reversibility times confidence times risk — and the separation it enforces: citation accuracy gates the *claim*, reversibility and risk gate the *action*. A well-grounded answer earns the right to say something. It doesn't earn the right to do something.

---

## The one idea I'd keep

If the whole exercise produced one durable line, it's this: **capability is not authority.**

It came out of a case about AI customer support. The observation was that on genuinely hard interactions, the binding constraint usually isn't knowledge. The system already knows the right answer. It isn't permitted to act on it. Which means the unlock is a governed permission model, not a better retrieval index.

I've since found that idea useful well outside support, and well outside AI. It's a good question to ask about any system that seems stuck: is this a knowledge problem or an authority problem? They look identical from the outside and they have completely different fixes.

That's the argument for doing this at all. Interview prep is written to be thrown away. Some of it shouldn't be.

---

*The knowledge base lives at [github.com/fabriziogf/fgf-kb](https://github.com/fabriziogf/fgf-kb). It's fed by [NoteKB](https://github.com/fabriziogf/noteKB), a tool that turns photos of handwritten notes into pull requests against it. Nothing merges without review, which is the only reason I trust it.*
