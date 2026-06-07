---
title: "Expanding the Platform: Vision AI for Football and an LLM Evaluation Framework"
---

Two more projects to describe. The first takes the vision AI architecture I built for AeroLens and applies it to football, with a live data agent added on top. The second is an evaluation framework for a question that comes up every time I talk to an AI team: how do you actually know if your LLM recommendation outputs are good?

Both projects were designed in relation to the three I described before. MatchLens reuses the AeroLens computer vision pipeline and asks what happens when you move from a single athlete in a controlled frame to 22 players in broadcast footage. RecEval wraps around TriCoach AI and provides the quality loop that closes the system. Neither one stands alone well, which is the point.

---

## Project 4: MatchLens — Vision AI for football performance

Football broadcasts generate enormous commentary but almost no structured analytical output. A pundit can tell you Mbappé is fast. What you can't get is a sprint mechanics score, a body lean angle at peak velocity, and a comparison to his last five matches — formatted as something you could share or query.

The architecture reuses the MediaPipe + OpenCV + multimodal LLM stack from AeroLens, with two significant changes.

The first is the switch from one athlete to many. Broadcast footage has 22 players, partial occlusions, camera cuts, and moving backgrounds. YOLOv8 handles player detection and generates per-player bounding boxes that feed into the pose estimation pipeline. MediaPipe runs on isolated crops rather than full frames. Confidence degrades explicitly when occlusion is high — the same uncertainty logic from AeroLens, adapted to a noisier context.

The second change is a **live data agent**. The LangGraph agent identifies the player in the video, fetches current tournament stats from the football-data.org API, and contextualizes the visual analysis against live match state: scoreline, minute, opponent, sprint frequency this match versus tournament average. The output changes meaningfully — not "forward lean is optimal" but "forward lean is optimal, and he's run 14 sprints in this match versus his tournament average of 11, in minute 87, trailing 1–0." That context is what separates a vision model from a useful tool.

**The biomechanics analysis** covers five movement types: sprinting, shooting, heading, change of direction, and defensive stance. The sprint mechanics scoring is structurally identical to AeroLens's aero scoring — measure against optimal ranges, compute deviation, generate priority-ranked findings. I designed AeroLens with this reusability in mind; the transfer took less engineering work than building from scratch.

The harder CV problem is multi-player scenes with occlusion. In AeroLens there's one rider in a controlled frame. In broadcast footage, players overlap constantly, and pose estimation quality degrades in ways that require per-player confidence logic rather than a single frame-level score. I handle it with confidence multipliers based on occlusion degree, bounding box overlap with adjacent players, and frame resolution at the crop level. Findings below a threshold surface a re-frame suggestion rather than a silent low-quality result.

The RAG layer has three corpora: sports science literature on biomechanics chunked by movement type, tactical knowledge organized by pressing system and formation, and player profiles from public career data. Retrieval is selective — biomechanics questions hit corpus 1, tactical questions hit corpus 2, player-specific questions hit corpus 3.

**The tactical analysis module** is where the LLM does what CV can't. For multi-player images — team shape, set pieces, pressing patterns — the LLM performs tactical interpretation: what pressing trigger is being applied, where the space vulnerability is, which historical team's pattern this resembles. Outputs come as structured JSON with a confidence score per finding, so the report can distinguish between high-confidence formation identification and more interpretive claims.

**Tech stack:** YOLOv8 (Ultralytics), MediaPipe Pose, GPT-4o Vision or Claude claude-sonnet-4, LangGraph for the data agent, football-data.org API, LlamaIndex + ChromaDB, OpenCV, Streamlit, Hugging Face Spaces.

---

## Project 5: RecEval — An LLM recommendation evaluation framework

Every team building LLM-powered recommendations hits the same wall eventually: BLEU and ROUGE were designed for translation. RAGAS evaluates RAG pipelines. There's no standard, reusable framework for evaluating the specific failure modes of LLM-generated recommendations. RecEval is my attempt to build one.

The domain is triathlon training recommendations — I have the data and the domain expertise to build credible ground truth. But the framework is explicitly domain-portable. The same eval harness can evaluate music playlist recommendations or e-commerce recommendations with a different config. That portability is the main structural choice.

The framework evaluates across five dimensions:

**Factual accuracy.** The LLM might correctly cite the 10% weekly progression rule and in the same output hallucinate that a CTL of 120 is appropriate before an Ironman. Both delivered with equal confidence. The eval extracts all specific numerical and factual claims, checks them against the TriBrain knowledge base, and returns a verification status: VERIFIED, UNVERIFIED, CONTRADICTED, or UNVERIFIABLE. The unverifiable precision rate is the most interesting metric — it measures how often the model expresses specific numerical authority with no supporting source.

**Recommendation quality.** Accurate advice can still be bad advice if it ignores the athlete's context, is too vague to act on, or contradicts itself. I score three sub-dimensions: specificity (does this reference this athlete's actual data, or could it apply to anyone?), actionability (is this executable next week, or is it a platitude?), and coherence (do the recommendations conflict with each other?). Coherence is checked deterministically: "increase bike volume" and "reduce total TSS" in the same plan is a logical conflict, detectable without an LLM judge.

**Personalization fidelity.** The **context sensitivity test** generates recommendations for a base athlete profile and five systematic variations — different fitness level, different weeks to race, different injury history, different available hours — and measures how much the outputs diverge. High personalization means high variance across variations. A model generating similar advice regardless of context is failing at personalization. The **phantom context test** catches a different failure: the model referencing context that was never provided, to appear personalized when it isn't.

**Safety and harm avoidance.** A deterministic layer. Explicit rules check for weekly TSS spikes above 15%, three or more consecutive hard sessions without recovery, injury signals in the context being ignored, and double sessions recommended without recovery guidance. These either pass or fail. No LLM judge needed.

**LLM-specific failure modes.** Four failure modes that don't exist in traditional recommendation systems.

*Sycophancy:* Generate a training plan, then push back with "I think I can handle way more volume." Does the model increase load beyond safe limits to satisfy the user? A good system holds its ground.

*Position bias:* Present the same training options in different orders across multiple runs. LLMs disproportionately favor options listed first or last. A well-calibrated recommender should rank identically regardless of presentation order.

*Calibration:* When the model says "I strongly recommend X," does that confidence correlate with correctness? An uncalibrated model is confidently wrong — which is particularly dangerous in health advice.

*Consistency:* Run the same prompt ten times at temperature > 0 and measure semantic variance in the factual claims across outputs. High variance on specific numerical claims is a hallucination risk signal that's invisible from any single output.

**Ground truth** is the hardest part. I use three tiers. Tier 1 is deterministic — physiological limits and safety rules with clear right/wrong answers. Tier 2 is a manually annotated golden dataset of 30–50 test cases where I wrote ideal recommendations and scored real outputs against them on a 1–5 rubric per dimension. Tier 3 uses a separate LLM as judge for subjective dimensions that don't scale to manual annotation.

The critical step is calibration: running the LLM judge against my Tier 2 annotations and verifying that it agrees with me at least 85% of the time before trusting it on new cases. If the agreement is lower, the rubric needs refinement. That's what separates a rigorous eval from a vibe check.

**The domain portability layer** is a `DomainConfig` dataclass that packages everything domain-specific — recommendation schema, safety rules, factual knowledge base, quality rubric, ground truth dataset, context variables — into a single swappable unit. Changing domains means instantiating a different config. The pipeline logic is domain-agnostic.

The UI is a Streamlit dashboard with four panels: a radar chart comparing dimensions across models, a filterable failure mode explorer, a regression tracker comparing version N to version N-1, and a calibration panel showing LLM judge vs. human annotation agreement.

**Tech stack:** Custom Python + Pydantic for typed schemas, Claude claude-sonnet-4 as LLM judge, `sentence-transformers` for semantic similarity metrics, TriCoach AI as the primary test subject, SQLite for ground truth storage, Streamlit + Plotly for the dashboard.

---

## Where this leaves the platform

Five components now:

- **AeroLens** (vision layer for cycling): pose estimation, aero analysis, structured fit reports
- **MatchLens** (vision layer for football): multi-player detection, sprint mechanics, live data agent
- **TriBrain** (memory layer): longitudinal RAG over training history, hybrid retrieval
- **TriCoach AI** (planning layer): multi-agent weekly plan generation, calls TriBrain for guidelines
- **RecEval** (quality layer): evaluation harness that closes the loop on TriCoach outputs

MatchLens shares the CV pipeline with AeroLens. RecEval consumes TriCoach AI's outputs and uses TriBrain's knowledge base for fact-checking. All five share embeddings (`all-mpnet-base-v2`), vector stores (ChromaDB or Weaviate), and agent frameworks (LangGraph). That shared infrastructure isn't incidental — it's how I'd build a production system.

Every project is independently useful. Every project feeds the next one. Together they form one system.

---

*If you're building evaluation frameworks for LLM recommendations, or applying vision AI to sports analysis, I'd be interested to compare notes. The calibration methodology for LLM-as-judge is somewhere the field doesn't have a settled answer yet.*
