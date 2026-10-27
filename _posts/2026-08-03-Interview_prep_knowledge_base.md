---
title: "Adding Interview Prep to My Knowledge Base"
---

I recently [wrote about the knowledge base](/Product_knowledge_base/) I'm building for my product and AI work. This post is about how I'm filling it.

The knowledge base is meant to hold lasting AI and product knowledge: how agents are actually built, how you evaluate them, how platform work really goes. What it needed was content. The first batch came from the prep docs and case decks I put together for my job search.

Those files had deep dives on agent architecture, evaluation frameworks for agentic products, metrics, experimentation and causal inference, platform migration strategy, prioritization under a hard deadline, and engineering concepts for a PM who needs to be credible with engineers without pretending to be one.

---

## What the first pass added

Thirty-one topics across six areas, including:

**AI agents.** What actually makes something an agent, and why the useful question is never "is this an agent?" but "what does it do on its own, and what happens when a wrong action goes through?" The ReAct loop and its four termination conditions. The four memory types. Tool schema design, including the point that an agent with fifty tools picks *worse* than one with ten, because the model has to reason over a noisier action space. Orchestration patterns, with a strong bias toward starting with a single agent and making the architecture earn its complexity. Guardrails as three separate layers. Why agent cost grows quadratically, not linearly, with step count.

**Evaluation.** The area I care about most, and where the gap between good and bad teams is widest. The three-layer breakdown, and the argument that a single aggregate quality metric actively blocks root cause analysis. Golden trace datasets, where the hard part is representative sampling, not labeling. LLM-as-judge, its four known biases, and the claim that the rubric matters far more than the judge model. The gap between offline and online eval as the place quality surprises show up. And eval infrastructure as a product with its own users and roadmap, not a one-time engineering task.

**Retrieval and context.** RAG architecture and exactly where it breaks. Dense vs. sparse vs. hybrid. Context engineering, prompt anatomy, and treating prompts as code with regression tests and rollback triggers.

**Platform PM.** The migration playbook: audit, contract, parallel run, sunset. Its central claim is that migrations fail socially before they fail technically, and that the four sources of resistance need four different responses. Throwing engineering support at an institutional resistance problem doesn't work.

**Measurement.** Causal inference for when you can't randomize. Goodhart's Law as the main failure mode in AI products, not an abstraction. Why containment rate should never be read alone. And the context on-off test, the cleanest way I know to tell whether personalization caused an improvement or the automation just got better.

**AI product strategy.** The autonomy throttle (reversibility × confidence × risk) and the separation it enforces: citation accuracy gates the *claim*, while reversibility and risk gate the *action*. **A well-grounded answer earns the right to say something. It doesn't earn the right to do something.**

---

*The knowledge base lives at [github.com/fabriziogf/fgf-kb](https://github.com/fabriziogf/fgf-kb). It's fed by [NoteKB](https://github.com/fabriziogf/noteKB), a tool that turns photos of handwritten notes into pull requests against it. Nothing merges without review, which is the only reason I trust it.*
