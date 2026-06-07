---
title: "Building an Athlete Intelligence Platform: Three AI Projects, One Coherent System"
---

I've been thinking about how to build a portfolio of AI projects that actually hangs together — not isolated demos, but something with a coherent architecture and a real story.

The domain I landed on is triathlon. I train for it seriously, which means I have years of real data, genuine questions I want answered, and strong intuitions about where the existing tools fall short.

The result is three projects I'm building together as one system. Each one solves a distinct problem. But they share data pipelines, call each other as services, and are designed to be composed.

Here's what I'm building and why.

---

## The problem with existing triathlon tools

Strava and Garmin are good at data visualization. They're not intelligent. You can look at your CTL trend or weekly TSS breakdown, but you can't ask: *"How did my swim volume in the six weeks before my last A-race compare to this build?"*

On the coaching side, no consumer AI tool handles swim, bike, and run well together. The optimization variables conflict — high bike volume depresses run economy. A recovery week that makes sense for running may not make sense mid-swim-build. Real coaches navigate these tradeoffs through experience and explicit rules. AI coaching tools generally don't.

And for bike fitting and aerodynamics — the options are expensive ($300–600 for a professional fit), inaccessible (wind tunnel testing costs thousands), or simply don't exist at the consumer level.

Three problems. Three projects.

---

## Project 6: TriBrain — A RAG-based training memory system

The first project is a conversational system that answers questions about my own longitudinal training data.

The hard part isn't the LLM integration. The hard part is **chunking strategy for time-series data**. Most RAG tutorials chunk text documents. Here I'm chunking structured fitness data across three tiers:

**Tier 1 — Activity level.** Each workout becomes one chunk, serialized as natural language: duration, distance, heart rate, pace, TSS, zone distribution, RPE, and any notes.

**Tier 2 — Weekly summary.** Auto-generated rollups with total TSS, volume by discipline, CTL and ATL entering the week, form (TSB), and key session descriptions.

**Tier 3 — Training block.** Twelve-week macro summaries anchored to race events: peak CTL, volume progression, identified limiters, race result.

The retrieval tradeoff is real: Tier 1 is precise but loses temporal context. Tier 3 has context but loses specificity. Hybrid retrieval across all three tiers — dense semantic search combined with sparse BM25, fused via Reciprocal Rank Fusion — is how I solve it.

On top of that, I'm building a query understanding layer that parses natural language questions into structured retrieval parameters: sport, time anchor, metric focus, temporal window. *"How was my run fitness before my last race"* becomes `{sport: "run", time_anchor: "relative", temporal_window: "6 weeks prior to 2024-04-07"}`.

For evaluation, I'm using RAGAS with a manually verified ground truth dataset of 20 Q&A pairs. The metrics I care about: faithfulness, context recall, and a custom numerical accuracy metric for metric-specific questions — that's where hallucination risk is highest.

**Tech stack:** Strava API + `stravalib`, `sweat` library for ATL/CTL/TSS, `sentence-transformers` for embeddings, Weaviate for hybrid search, Claude API for reasoning, LlamaIndex for orchestration, Chainlit for the chat UI.

---

## Project 7: TriCoach AI — A multi-agent training planner

The second project generates weekly training plans using specialized discipline agents and a synthesizing orchestrator.

The architecture mirrors how real triathlon coaching works. Discipline specialists optimize within their domains. A head coach balances their competing recommendations and manages overall load. Each agent in my system has an explicit contract: a defined role, a structured input schema, a set of tools it can call, and a JSON output schema it must produce.

The interesting design problems are the **inter-agent dependencies** and the **conflict resolution logic**.

The Bike Agent and Swim Agent run in parallel. The Run Agent is downstream of the Bike Agent — it receives bike TSS as structured context and adjusts run volume accordingly. The Recovery Agent runs last, taking all three discipline outputs plus HRV data and computing overreach risk.

The orchestrator applies explicit priority rules — not just LLM reasoning. If Recovery flags overreach, reduce the highest-TSS session. If Bike and Run both want a Tuesday hard session, Bike wins if you're more than eight weeks out; Run wins if you're within four. If any agent confidence is below 0.6, surface a warning with an explanation.

I'm using **LangGraph** for the agent graph because it gives me explicit control over routing logic and stateful checkpointing. I want to reason about exactly where in the graph the orchestration logic lives — that transparency matters for debugging.

One design choice I'm pleased with: the `lookup_coaching_guidelines` tool calls directly into the TriBrain vector store from Project 6. The multi-agent planning system uses the RAG memory system as a tool. They're composable by design.

**Tech stack:** LangGraph, Claude claude-sonnet-4 per agent, custom Python tool wrappers over Strava API, LangSmith for observability, SQLite for state persistence, Streamlit for UI.

---

## Project 3: AeroLens — Vision AI for bike fit and aerodynamics

The third project uses pose estimation, multimodal LLM reasoning, image segmentation, and a RAG knowledge base to analyze photos and video of a rider — and produce a structured report on position and aerodynamic drag.

The architecture has two parallel analysis paths:

**The CV path** uses MediaPipe Pose to extract 33 body landmarks and compute precise joint angles: knee extension and flexion, hip angle, torso angle, elbow angle, ankle dorsiflexion, shoulder angle. Fault detection is **deterministic**, not LLM-based. LLMs hallucinate numerical values from images. MediaPipe gives pixel-precise coordinates and sub-degree angle accuracy. The LLM handles holistic reasoning around the numbers, not instead of them.

**The LLM path** uses GPT-4o Vision or Claude to analyze drag hotspots from side-profile images: head angle, shoulder width, elbow width vs. hip width, jersey fit, handlebar extensions, torso flatness. The LLM identifies what and where. Watts-saved estimates come from a lookup table grounded in published aerodynamics literature — not model output.

For frontal area estimation, I'm using SAM (Meta's Segment Anything Model) to segment the rider-and-bike silhouette, compute pixel area normalized by wheel diameter, and map to an approximate CDA range based on position category.

The video analysis module adds two things static images can't: pedal stroke dynamics across all 12 crank positions, and temporal consistency — does the rider hold position under fatigue, or does torso angle drift later in the video? Dynamic faults like hip rock, knee flare, and position drift are only visible in video.

Every finding carries a **confidence score** that degrades based on image quality — resolution, partial occlusion, camera angle, non-standard clothing. Low-confidence findings surface a warning and re-shoot guidance rather than silently producing a bad recommendation.

**Tech stack:** MediaPipe Pose, SAM for segmentation, Claude claude-sonnet-4 or GPT-4o Vision, LlamaIndex + ChromaDB for the fitting standards RAG, OpenCV for annotation overlays, Streamlit for UI, Hugging Face Spaces for deployment.

---

## How they fit together

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

AeroLens analyzes your position and logs structured fit data. TriBrain remembers your training and fit history longitudinally. TriCoach plans your next training week, informed by both.

I didn't build three demos. I built one system with a vision layer, a memory layer, and a planning layer. The architecture is composable by design — shared retrieval infrastructure, specialized agents on top, a longitudinal memory layer underneath.

Build plans are roughly 12–14 days per project, working evenings. I'm starting with TriBrain since it provides the shared data infrastructure the other two depend on, then TriCoach, then AeroLens. I'll write each one up as I ship it.

---

*This is part of a broader series on building AI/ML projects I'd actually use. If you're a triathlete building something similar, or have thoughts on the retrieval architecture, I'd be interested to hear from you.*
