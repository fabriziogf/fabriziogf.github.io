---
title: "Building an Athlete Intelligence Platform: Three AI Projects, One Coherent System"
---

I have been thinking about how to build a portfolio of AI projects that actually hangs together — not a pile of isolated demos, but something with a coherent architecture and a real story to tell. The domain I landed on is triathlon. It is something I train for seriously, which means I have years of real data, genuine questions I want answered, and strong intuitions about where the existing tools fall short.

The result is a three-project system I am calling an **athlete intelligence platform**. Each project solves a distinct problem. Each one is independently interesting. But they are also explicitly designed to be composable — they share data pipelines, call each other as services, and together form something that is more than the sum of its parts.

Here is what I am building and why.

---

## The Problem with Existing Triathlon Tools

Strava and Garmin are excellent at data visualization. They are not intelligent. You can look at your CTL trend or your weekly TSS breakdown, but you cannot ask: *"How did my swim volume in the six weeks before my last A-race compare to this build?"* or *"What does my HRV trend look like relative to my CTL peaks?"*

On the coaching side, no consumer AI tool handles swim, bike, and run well simultaneously, because the optimization variables conflict. High bike volume depresses run economy. A recovery week that makes sense from a running perspective may not make sense for where you are in a swim build. Real triathlon coaches navigate these tradeoffs through experience and explicit priority logic. AI coaching tools generally do not.

And for bike fitting and aerodynamics — tools that give you structured, data-driven feedback on your position — the options are either expensive ($300–600 for a professional fit), inaccessible (wind tunnel testing costs thousands), or nonexistent (vision AI for aero analysis at the consumer level is basically a gap).

Three problems. Three projects.

---

## Project 6: TriBrain — A RAG-Based Training Memory System

The first project is a conversational, memory-augmented retrieval system over my own longitudinal training data.

The core technical challenge is not the LLM integration — that part is relatively straightforward. The hard problem is **chunking strategy for time-series data**. Most RAG tutorials chunk text documents. Here, I am chunking structured fitness data across three tiers:

**Tier 1 — Activity level.** Each workout becomes one chunk, serialized as natural language: duration, distance, heart rate, pace, TSS, zone distribution, RPE, and any notes. This is the atomic unit of retrieval.

**Tier 2 — Weekly summary.** Auto-generated rollups with total TSS, volume by discipline, CTL entering the week, ATL entering the week, form (TSB), and key session descriptions. This tier captures patterns that span multiple days.

**Tier 3 — Training block.** Twelve-week macro summaries anchored to race events: peak CTL, volume progression, identified limiters, race result. This is the context layer for strategic questions.

The retrieval tradeoff is real and interesting: Tier 1 is precise but loses temporal context. Tier 3 has context but loses specificity. Hybrid retrieval across all three tiers — dense semantic search combined with sparse BM25 over metadata fields, fused via Reciprocal Rank Fusion — is how I solve it.

On top of that, I am building a query understanding layer that parses natural language questions into structured retrieval parameters: sport, time anchor, metric focus, temporal window. *"How was my run fitness before my last race"* becomes `{sport: "run", time_anchor: "relative", metric_focus: "fitness", temporal_window: "6 weeks prior to 2024-04-07"}`.

For evaluation, I am using RAGAS with a manually verified ground truth dataset of 20 Q&A pairs. The metrics I care most about: faithfulness (does the answer contradict the retrieved chunks?), context recall (did retrieval surface the right chunks?), and a custom numerical accuracy metric for metric-specific questions, since those are where hallucination risk is highest.

**Tech stack:** Strava API + `stravalib`, `sweat` library for ATL/CTL/TSS computation, `sentence-transformers` for embeddings, Weaviate for hybrid search, Claude API for the reasoning layer, LlamaIndex for orchestration, Chainlit for the chat UI.

---

## Project 7: TriCoach AI — A Multi-Agent Training Planner

The second project is a multi-agent system that generates weekly training plans by dispatching to specialized discipline agents and synthesizing their outputs through an orchestrating "head coach."

The architecture mirrors how real triathlon coaching works. You have discipline specialists — a swim coach, a bike coach, a run coach — who optimize within their domains, and a head coach who balances their competing recommendations and manages overall load. Each agent in my system has an explicit contract: a defined role, a structured input schema, a set of tools it can call, and a JSON output schema it must produce.

The interesting design problems are in the **inter-agent dependencies** and the **conflict resolution logic**:

The Bike Agent and Swim Agent run in parallel. The Run Agent is downstream of the Bike Agent — it receives bike TSS as structured context and adjusts run volume recommendations accordingly. The Recovery Agent runs last, taking all three discipline outputs plus HRV data and computing overreach risk.

The orchestrator then applies explicit priority rules, not just LLM reasoning: if Recovery flags overreach, reduce the highest-TSS session. If Bike and Run both want a Tuesday hard session, Bike wins if you are more than eight weeks out from race day, Run wins if you are within four weeks. If any agent confidence is below 0.6, surface a warning to the user with an explanation.

I am using **LangGraph** for the agent graph, specifically because it gives me explicit control over routing logic and stateful checkpointing. The state object carries the full athlete context, each agent's output, detected conflicts, and the final brief. I want to be able to reason about exactly where in the graph the orchestration logic lives — that transparency matters both for debugging and for being able to explain the system clearly.

One design choice I am pleased with: the `lookup_coaching_guidelines` tool in each agent's registry calls directly into the TriBrain vector store from Project 6. The multi-agent planning system uses the RAG memory system as a tool. They are composable by design, and that composability is the point.

**Tech stack:** LangGraph, Claude claude-sonnet-4 per agent, custom Python tool wrappers over Strava API, LangSmith for observability, SQLite for state persistence, Streamlit for UI.

---

## Project 3: AeroLens — Vision AI for Bike Fit and Aerodynamics

The third project is the most technically unusual. It uses pose estimation, multimodal LLM reasoning, image segmentation, and a RAG knowledge base to analyze photos and video of a rider on a bike — and produce a structured report on position compliance and aerodynamic drag exposure.

The architecture has two parallel analysis paths:

**The CV path** uses MediaPipe Pose to extract 33 body landmarks from images and compute precise joint angles: knee extension and flexion at each pedal stroke position, hip angle, torso angle, elbow angle, ankle dorsiflexion, shoulder angle. Fault detection for these measurements is **deterministic**, not LLM-based. LLMs hallucinate numerical values from images. MediaPipe gives pixel-precise landmark coordinates and sub-degree angle accuracy. I use the LLM for holistic reasoning around the numbers, not instead of them.

**The LLM path** uses GPT-4o Vision or Claude to analyze drag hotspots from side-profile images: head angle, shoulder width, elbow width vs. hip width, jersey fit, handlebar extensions, torso flatness, knee tracking. The LLM identifies what and where. Watts-saved estimates come from a lookup table grounded in published aerodynamics literature (Crouch et al., 2017; Defraeye et al., 2010) — not model output.

For frontal area estimation, I am using SAM (Meta's Segment Anything Model) to segment the rider-and-bike silhouette from a front-facing image, compute pixel area normalized by wheel diameter (700mm reference), and map to an approximate CDA range based on position category.

The video analysis module adds two things static images cannot: pedal stroke dynamics (position across all 12 crank positions, not just one snapshot) and temporal consistency (does the rider hold position under fatigue, or does torso angle drift in the back half of the video?). Dynamic faults like hip rock, knee flare, heel drop, and position drift are only visible in video.

Every finding in the output carries a **confidence score** that degrades based on image quality factors — resolution, partial occlusion, camera angle deviation, non-standard clothing. Low-confidence findings surface a warning and re-shoot guidance rather than silently producing a bad recommendation. That uncertainty communication is something a real product needs.

**Tech stack:** MediaPipe Pose, SAM for segmentation, Claude claude-sonnet-4 or GPT-4o Vision for multimodal reasoning, LlamaIndex + ChromaDB for the fitting standards RAG, OpenCV for annotation overlays, Streamlit for UI, Hugging Face Spaces for deployment (free GPU tier).

---

## How They Fit Together

```
Strava / Garmin Data Pipeline
           │
  ┌────────┼────────┐
  ▼        ▼        ▼
TriBrain  Shared  AeroLens
  RAG     Vector    Fit +
 Memory   Store    Aero AI
   │        │        │
   └────────┴────────┘
               │
               ▼
         TriCoach AI
       Multi-Agent Planner
    (calls TriBrain for guidelines,
     calls AeroLens for position data)
```

AeroLens analyzes your position and logs structured fit data. TriBrain remembers your training history and fit history longitudinally — so you can ask "what was my CTL when I made that saddle change?" TriCoach plans your next training week, informed by both your training memory and your current position analysis.

I did not build three demos. I built one athlete intelligence platform with a vision layer, a memory layer, and a planning layer. The architecture is composable by design — the same way I would think about building a production personalization system: shared retrieval infrastructure, specialized agents on top, a longitudinal memory layer underneath.

The build plans are roughly 12–14 days per project, working evenings. I am starting with TriBrain since it provides the shared data infrastructure the other two depend on, then TriCoach, then AeroLens. I will write up each one as I ship it.

---

*This is part of a broader series on building AI/ML projects I would actually use. If you are a triathlete building something similar, or have thoughts on the retrieval architecture, I would be interested to hear from you.*
