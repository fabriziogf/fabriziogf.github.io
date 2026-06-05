---
title: "Expanding the Platform: Vision AI for Football and an LLM Evaluation Framework"
---

Two more projects to describe. The first extends the vision AI architecture I built for AeroLens into a new domain — football — with a live agentic layer added on top. The second is an evaluation framework designed to answer a question that comes up every time I talk to an AI team: how do you actually know if your LLM recommendation outputs are good?

Both projects were designed deliberately in relation to the three I described before. MatchLens reuses the AeroLens computer vision pipeline and asks what happens when you take it from a constrained single-athlete problem to a chaotic multi-athlete broadcast environment. RecEval wraps around TriCoach AI and provides the quality loop that closes the system. Neither one stands alone well, which is the point.

---

## Project 4: MatchLens — Vision AI for Football Performance

The starting observation for MatchLens is that football broadcasts generate enormous commentary but almost no structured analytical output. A pundit can tell you Mbappé is fast. What you cannot get is a sprint mechanics score, a body lean angle at peak velocity, and a statement about how that compares to his last five matches — formatted as something you could share or query.

The architecture reuses the MediaPipe + OpenCV + multimodal LLM stack from AeroLens, with two significant changes. The first is the switch from one athlete to many: broadcast footage contains 22 players, partial occlusions, camera cuts, and moving backgrounds. YOLOv8 handles player detection and generates per-player bounding boxes that serve as inputs to the pose estimation pipeline. MediaPipe runs on isolated crops rather than full frames, and confidence degrades explicitly when occlusion is high — the same uncertainty communication logic from AeroLens, adapted to a noisier context.

The second change is a **live data agent**, which is what makes MatchLens feel like an actual product rather than an offline analyzer. The LangGraph agent identifies the player in the video, fetches current tournament statistics from the football-data.org API, and contextualizes the visual analysis against live match state: scoreline, minute, opponent, sprint frequency this match versus tournament average. The output reads differently as a result — not "forward lean is optimal" but "forward lean is optimal, and he has run 14 sprints in this match versus his tournament average of 11, in minute 87, trailing 1–0." That situational awareness is the gap between a vision model and an intelligent system.

**The biomechanics analysis** covers five movement types: sprinting, shooting, heading, change of direction, and defensive stance. Each has a distinct set of CV measurements and a scoring rubric. The sprint mechanics scoring is structurally identical to AeroLens's aero scoring — measure against optimal ranges, compute deviation, compute weighted overall score, generate priority-ranked findings. I designed AeroLens with this reusability in mind; the transfer took less engineering work than building from scratch would have.

The harder CV problem is multi-player scenes with occlusion. In AeroLens there is one rider in a controlled frame. Here, players overlap constantly in broadcast footage, and the pose estimation quality degrades in ways that require per-player confidence logic rather than a single frame-level confidence score. The way I handle it: confidence multipliers on each player's measurements based on occlusion degree, bounding box overlap with adjacent players, and frame resolution at the crop level. Findings below a threshold surface a re-shoot or re-frame suggestion rather than a silent low-quality result.

The RAG layer has three separate corpora: sports science literature on biomechanics chunked by movement type and body region, tactical knowledge organized by pressing system and formation, and player profiles built from public career data. Retrieval is selective — biomechanics questions hit corpus 1, tactical questions hit corpus 2, player-specific questions hit corpus 3. The agent pulls from all three depending on what the visual analysis surfaces.

**The tactical analysis module** is the piece that goes furthest beyond what CV can do alone. For multi-player images — team shape, set pieces, pressing patterns — the multimodal LLM performs tactical interpretation that pose estimation cannot: what pressing trigger is being applied, where the space vulnerability is, which historical team's pattern this resembles. The prompt asks for structured JSON with a confidence score per finding, which lets the report distinguish between high-confidence formation identification and more interpretive tactical claims.

**Tech stack:** YOLOv8 (Ultralytics), MediaPipe Pose, GPT-4o Vision or Claude claude-sonnet-4, LangGraph for the data agent, football-data.org API, LlamaIndex + ChromaDB, OpenCV, Streamlit, Hugging Face Spaces.

---

## Project 5: RecEval — An LLM Recommendation Evaluation Framework

Every team building LLM-powered recommendation or personalization systems eventually hits the same problem: BLEU and ROUGE were designed for translation. RAGAS evaluates RAG pipelines. There is no standard, reusable framework for evaluating the specific failure modes of LLM-generated recommendations. RecEval is my attempt to build one.

The domain is triathlon training recommendations, because that is where I have both the data and the domain expertise to build credible ground truth. But the framework is explicitly domain-portable — the same evaluation harness can evaluate music playlist recommendations or e-commerce recommendations with a different config. That portability is the main structural choice, and it is what separates this from a one-off eval script.

The framework evaluates across five dimensions:

**Dimension 1: Factual accuracy.** The LLM might correctly cite the 10% weekly progression rule and in the same output hallucinate that a CTL of 120 is appropriate before an Ironman. Both statements are delivered with equal confidence. The eval extracts all specific numerical and factual claims, checks them against the RAG knowledge base from TriBrain, and returns a verification status — VERIFIED, UNVERIFIED, CONTRADICTED, or UNVERIFIABLE. The unverifiable precision rate is the most interesting metric here: it measures how often the model expresses specific numerical authority with no supporting source.

**Dimension 2: Recommendation quality.** Technically accurate advice can still be bad advice if it ignores the athlete's context, is too vague to act on, or contradicts itself internally. I score three sub-dimensions: specificity (does this recommendation reference this athlete's actual data, or could it apply to anyone?), actionability (is this executable next week, or is it a vague platitude?), and coherence (do the recommendations in this set conflict with each other?). Coherence is checked deterministically: "increase bike volume" and "reduce total TSS" in the same plan is a logical conflict, detectable without an LLM judge.

**Dimension 3: Personalization fidelity.** This is the dimension most directly grounded in my professional background. At Amazon I measured personalization quality through production signals — click-through, purchase, satisfaction. RecEval does the pre-production equivalent. The **context sensitivity test** generates recommendations for a base athlete profile and five systematic variations — different fitness level, different weeks to race, different injury history, different available hours — and measures how much the outputs diverge. High personalization means high variance across variations; a model generating similar advice regardless of context is failing at personalization. The **phantom context test** catches a different failure mode: the model referencing context that was never provided, to appear personalized when it is not.

**Dimension 4: Safety and harm avoidance.** This is the deterministic layer. A set of explicit safety rules checks for weekly TSS spikes above 15%, three or more consecutive hard sessions without recovery, injury signals in the context being ignored, and double sessions recommended without recovery guidance. These checks do not require an LLM judge and are not probabilistic — they either pass or fail. Including this dimension maps the eval framework directly to the responsible AI concerns that every enterprise AI team has. It is not an afterthought.

**Dimension 5: LLM-specific failure modes.** The four failure modes I test for are not present in traditional recommendation systems and require adversarial test designs to surface.

*Sycophancy:* Generate a training plan, then push back with "I think I can handle way more volume." Does the model increase load beyond safe limits to satisfy the user? A good system holds its recommendation under pressure.

*Position bias:* Present the same set of training options in different orders across multiple runs. LLMs disproportionately favor options listed first or last. A well-calibrated recommender should rank identically regardless of presentation order.

*Calibration:* When the model says "I strongly recommend X," does that expressed confidence correlate with correctness? An uncalibrated model is confidently wrong — which is particularly dangerous in health advice. I measure expected calibration error and plot a reliability diagram against my ground truth annotations.

*Consistency:* Run the same prompt ten times at temperature > 0 and measure semantic variance in the factual claims made across outputs. High variance on specific numerical claims is a hallucination risk signal that is invisible from any single output.

**The ground truth problem** is the hardest part of building a rigorous eval, and I spent the most design effort here. I use three tiers. Tier 1 is deterministic — physiological limits and safety rules with clear right/wrong answers. No annotation needed. Tier 2 is a manually annotated golden dataset of 30–50 test cases where I wrote ideal recommendations and scored real outputs against them on a 1–5 rubric per dimension. My background in sports science, triathlon coaching, and ML makes me a credible annotator for this domain. Tier 3 uses a separate LLM as judge for subjective dimensions that do not scale to manual annotation.

The critical step is calibration: running the LLM judge against my Tier 2 annotations and verifying that it agrees with me at least 85% of the time before trusting it on new cases. If the agreement is lower, the rubric needs refinement. This is what distinguishes a rigorous eval from a vibe check, and it is the step that most eval frameworks skip.

**The domain portability layer** is a `DomainConfig` dataclass that packages everything domain-specific — recommendation schema, safety rules, factual knowledge base, quality rubric, ground truth dataset, and context variables — into a single swappable unit. Changing domains means instantiating a different config and passing it to the same eval pipeline. The framework logic is domain-agnostic by construction.

The UI is a Streamlit dashboard with four panels: an overview radar chart comparing dimensions across models, a filterable failure mode explorer with annotated breakdown on click, a regression tracker comparing version N to version N-1, and a calibration panel showing LLM judge vs. human annotation agreement. Most eval projects live in a Jupyter notebook. Having a dashboard changes how you interact with the results.

**Tech stack:** Custom Python + Pydantic for typed schemas, Claude claude-sonnet-4 as LLM judge, `sentence-transformers` for semantic similarity metrics, TriCoach AI as the primary test subject, SQLite for ground truth storage, Streamlit + Plotly for the dashboard.

---

## Where This Leaves the Platform

With these two projects, the platform has five components:

- **AeroLens** (vision layer for cycling): pose estimation, aero analysis, structured fit reports
- **MatchLens** (vision layer for football): multi-player detection, sprint mechanics, live data agent
- **TriBrain** (memory layer): longitudinal RAG over training history, hybrid retrieval
- **TriCoach AI** (planning layer): multi-agent weekly plan generation, calls TriBrain for guidelines
- **RecEval** (quality layer): evaluation harness that closes the loop on TriCoach outputs

MatchLens shares the CV pipeline and report format with AeroLens. RecEval consumes TriCoach AI's outputs and uses TriBrain's knowledge base for fact-checking. The five projects share embeddings (`all-mpnet-base-v2`), vector stores (ChromaDB or Weaviate), and agent frameworks (LangGraph). The shared infrastructure is not incidental — it is how I would build a production system, and building the portfolio this way is the demonstration of that.

The one-sentence pitch: I built a five-project athlete intelligence platform with a vision layer, a memory layer, a planning layer, and an evaluation layer. Every project is independently useful. Every project feeds the next one. Together they form a coherent system designed the same way I would design the platform at a company.

---

*If you are building evaluation frameworks for LLM recommendations, or applying vision AI to sports analysis, I am interested to compare notes. The calibration methodology for LLM-as-judge in particular is somewhere the field does not have a settled answer yet.*
