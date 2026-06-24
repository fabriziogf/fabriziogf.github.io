---
title: "Inside the Job-Hunting Agent: How It's Built"
---

A while back I wrote about [turning Laszlo Bock's *Apply Within* playbook into an agent](/Building_a_job_hunting_agent/) — the idea being that a job hunt can be distilled down to a set of repeatable, learnable moves.. That is what an agent should be good at.

Given that idea, I built it: seven skills, plus job discovery, an orchestrator, live web search, persistence, and a command-line tool. This blog describes the underlying tech.

---

## Determinism vs. LLM

Almost every chapter of the playbook is a mix of two very different kinds of rules.

Some are mechanical: "GPA below 3.5? Leave it off." "Every bullet needs a number." "Never write 'Dear Hiring Manager.'" These are pure logic — no judgement required.

Others are judgement calls: rewriting "Managed sorority budget" into a crisp, quantified bullet in the candidate's voice. That needs a language model.

The whole system is organized around keeping these two apart. Each skill has a **deterministic core** and a **thin, optional LLM layer**. The deterministic part does most of the work — linting, selection, ordering, scoring, all the arithmetic. The model is only called for the few genuinely generative tasks, and it's always injected behind an interface so tests can swap in a fake.

This split pays off three ways:

- **Tests need no API key.** The deterministic parts are most of the value and are fully unit-tested offline. All 136 tests run with no network and no key.
- **It's fast and cheap.** Rejecting a resume for a missing email shouldn't cost a model call. The linters and scorers run instantly and free.
- **Honesty gets multiple enforcement points** — more on that next.

---

## "Never fabricate" enforcement

The playbook's most-repeated warning is *don't lie, don't stretch*. The hard part is turning that from a hope into a guarantee.

The answer is a `verified` flag on every achievement, defaulting to `False`. The convention is simple: only a human sets `verified=True`. The agent can draft achievements, but until a person confirms one, it isn't usable material. The profile then exposes a filtered view — `verified_achievements()` — and every skill is written to consume only that. Unconfirmed data simply isn't in the pipeline.

For the resume, this is implemented across three independent layers:

1. **The profile** only treats verified achievements as usable.
2. **The assembler** selects exclusively from verified achievements — unverified ones never reach the model or the output.
3. **The rewriter** refuses an unverified achievement outright, and its system prompt forbids inventing metrics, employers, or outcomes. If a bullet has no number, the model must keep it qualitative and report `has_metric=False` — never manufacture a figure.

Each skill guards against its *own* possible dishonesty: networking must never invent a shared "I loved your talk at X" hook, negotiation must never invent a fake competing offer, and the cover letter writer may only use company facts that were actually researched.

---

## The foundation: profile store and playbook loader

Before any skill, two things had to exist that every skill depends on.

**The candidate profile** is one validated, in-memory representation of the job seeker's experience. It's a tree of Pydantic models, and at its heart is the X/Y/Z achievement, modeled directly from the playbook's resume formula:

> Accomplished [X] as measured by [Y] by doing [Z].

```python
class Achievement(BaseModel):
    what: str                       # X — required
    measured_by: str | None = None  # Y — the metric
    how: str | None = None          # Z — the method
    verified: bool = False
    tags: list[str] = []
```

The metric and method are optional on purpose. Real data starts incomplete — you know *what* you did before you've pinned down the number. The model captures that partial state instead of forcing a made-up figure, and a derived `unquantified_achievements()` view becomes the concrete to-do list for the resume builder.

**The playbook loader** is the other half. The loader holds a hand-curated, paraphrased distillation of all eight chapters — each as a structured object with a core principle, actionable rules, memorable formulas, and grounding stats. The result is one method, `PLAYBOOK.as_prompt(skill)`, which renders the chapters relevant to a given skill into a ready-to-inject prompt block. Every skill builds its system prompt this way, so the guidance is chapter-cited and consistent rather than hand-copied into each one.

A note on what isn't committed: the PDF and any real profile are gitignored. The repo is public, the PDF is copyrighted, and a real profile is full of personal data. Testing runs against a synthetic fictional candidate instead — built through the schema so it's guaranteed valid, and seeded with deliberate "teaching" gaps (a sub-3.5 GPA, an achievement with no metric) so the skills have something to detect.

---

## The seven skills

Each skill maps to chapters in the guide:

**Resume Builder + ATS Optimizer (Ch. 2).** A deterministic linter flags rule violations, each tagged with a severity and the chapter it comes from. An LLM rewriter polishes one verified achievement into an X/Y/Z bullet, returning validated structured output rather than free text. An assembler ties it together — lint, select verified only, order most-recent-first with quantified bullets ahead of unquantified, trim to a one-page-per-decade budget, drop a sub-3.5 GPA. The ATS Optimizer then scores the result against a job description: it extracts the posting's keywords and phrases, checks which appear in the resume, flags unexpanded acronyms, and targets a 75%+ match. Most importantly, it *reports* — it never edits the resume to add a keyword, because that could represent a claim the candidate can't back up.

**Cover Letter / Email Writer + Company Research (Ch. 3).** The chapter's thesis is that you can't win a job with a cover letter, but you can lose one. So the deterministic linter catches every downside — generic salutation, missing or wrong company name, leftover `[Company]` placeholders, a third paragraph that claims to be customized but doesn't actually reference any researched fact. The LLM writer composes the four paragraphs. Company research is its own capability behind an interface, because that "why you, specifically" paragraph depends on real, current, verifiable facts.

**Interview Prep Coach (Ch. 5 & 6).** This skill is mostly deterministic. The 12 questions you'll almost certainly be asked are encoded as data. The practice math turns a question count into the chapter's arithmetic — 30 questions × 2 answers × 3 reps ≈ 13.5 hours, surfaced because that number is the motivational lever. The LLM is only needed to invent role-specific questions and draft answers.

**Networking, Pipeline Tracker, Negotiation (Ch. 4, 7, 8).** The Pipeline Tracker is the first skill with no model at all. It follows the volume game outlined in the guide (roughly 100 applications → 5 first rounds → 1 offer), encodes the follow-up cadence (every 2 weeks, for 6 weeks) as a date predicate, and sequences B-tier companies first so an offer there becomes leverage with the A-tier ones. The Negotiation Advisor computes the 10–20% ask band and the compounding lifetime value of a raise. With the defaults, a $5,000 raise won today is worth about $944k over a career, which is the single most motivating number in the chapter.

---

## Tying it together: discovery and orchestration

Now that the skills were built, I added two capabilities to orchestrate the full job-seeking journey:

**Job discovery** reuses what already existed instead of inventing new scoring: a job's fit score *is* the ATS keyword match between the candidate's assembled resume and the posting. The same signal that says "this is a good job to pursue" also tells the resume and cover letter which keywords to address.

**The orchestrator** takes one posting and produces a single consolidated `ApplicationPackage`. This includes a tailored resume, ATS score, interview question bank, and a cover letter. The key design choice is that it's *deterministic by default*: with nothing injected, `prepare()` runs fully offline and still returns a usable package. Inject the LLM writers and each step upgrades to model quality with no change to the calling code. It's the same injection seam used everywhere else, applied one level up.

```
        profile (verified facts)            company research
              │                                    │
              ▼                                     ▼
   rank_jobs ─▶ JobPosting ─▶ ApplicationOrchestrator.prepare ──────────┐
                                  │  resume (Ch.2) ──▶ ATS score (Ch.2)  │
                                  │  cover letter (Ch.3) ◀── research    │
                                  │  question bank (Ch.5/6)              │
                                  └──────────────┬──────────────────────┘
                                                 ▼
                                   to_application ─▶ Pipeline (Ch.7)
                                                          │
                                          offer ──▶ Negotiation (Ch.8)
```

---

## Enhancement 1: Web search

After implementing this MLP functionality, I decided to build a live company research and job postings tool.

The tempting shortcut is to ask the model what it knows about a company. However, Chapter 3 is explicit that a *wrong* fact in a cover letter is what gets it rejected, and model memory is stale and confabulation-prone. So instead the live providers use Claude's server-side web search tool, in a deliberate two-call pattern: first a search call that returns real, cited findings, then a separate structuring call that shapes *only those findings* into the target schema. Splitting them keeps a clean honesty boundary, where the structuring step never sees outside "knowledge" it could smuggle in. Every fact carries its source, URL, and date, so the candidate can verify it before sending.

---

## Enhancement 2: Persistence

Most of the system is stateless, building a resume is a pure function of its inputs. But a real job hunt runs over months, and a few things accumulate: the pipeline of applications, interview logs, saved packages, cached research.

The storage layer is deliberately not a database, as every model is already JSON-able Pydantic. The job, therefore, is just organizing JSON files well. One important detail is the atomic writes: saving goes to a temp file, then `os.replace()`s it into place. That's atomic on the same filesystem, so a crash mid-write can't corrupt `pipeline.json` — you either have the old complete file or the new one. A `Workspace` directory holds one job hunt's state with typed accessors, and a `CachedResearchProvider` wraps any research provider to turn an expensive live lookup into a once-per-company cost — the payoff of having kept research behind an interface since the beginning.

---

## How to run it

The project is on GitHub at [fabriziogf/job-hunt-assistant](https://github.com/fabriziogf/job-hunt-assistant), and everything except the optional AI features works for free and offline.

A thin `job-hunt` command wraps the common workflows. It's built on standard-library `argparse` — no new dependencies, keeping faith with the lean-stack rule. It's deterministic (every command runs with no API key; the model steps are opt-in behind a single `--llm` flag) and safe (it defaults to the synthetic profile and writes nothing unless you pass `--out`).


**1. Install `uv`** (the tool that runs everything):

```bash
# Mac or Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell):
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**2. Download the project and set it up:**

```bash
git clone https://github.com/fabriziogf/job-hunt-assistant.git
cd job-hunt-assistant
uv sync
```

**3. Try it immediately** with the built-in example candidate:

```bash
uv run job-hunt practice
```

That prints an interview-practice plan and the 12 questions you'll almost certainly be asked. If you see a list, everything works.

**4. Add your own profile.** Copy the shape of `examples/sample_profile.json` into a new file at `profiles/my_profile.json` (anything in `profiles/` stays private and is never uploaded). Set `"verified": true` only on achievements that are genuinely true — the agent refuses to use anything else. Then point any command at it:

```bash
# Check your resume against the playbook's rules:
uv run job-hunt lint --profile profiles/my_profile.json

# Prepare a tailored application for one job:
uv run job-hunt prepare \
    --profile profiles/my_profile.json \
    --company "Acme Corp" \
    --role "Product Manager" \
    --description "Paste the job description here" \
    --out ./acme
```

`prepare` tailors your resume to the job, scores how well it matches (aim for 75%+), lists the keywords you're missing, and writes the files into `./acme`.

**5. Track applications over time.** Add `--save` to a `prepare` command to log it, then:

```bash
uv run job-hunt pipeline
```

Your tracker lives in a `.jobhunt` folder. Come back any time to see which follow-ups are due — the playbook says every 2 weeks, for 6 weeks.

**6. (Optional) Turn on the AI features.** Resume rewriting, cover-letter drafting, and live job search need an Anthropic API key (a paid service, billed per use):

```bash
# Mac or Linux:
export ANTHROPIC_API_KEY="paste-your-key-here"

# Windows (PowerShell):
$env:ANTHROPIC_API_KEY="paste-your-key-here"
```

Then add `--llm` to draft a cover letter, or use `find` to search live listings:

```bash
uv run job-hunt prepare --profile profiles/my_profile.json \
    --company "Acme Corp" --role "Product Manager" \
    --description "..." --llm --out ./acme

uv run job-hunt find --query "product manager" --location "Boston" --rank
```

Add `--help` to any command to see all its options.

---

## Learnings from this project

The most interesting learning is how much of this supposedly AI project turned out to be deterministic. The model writes bullets and drafts letters, but the rules (what gets included, in what order, scored how, held back when unverified) are deterministic. Keeping the use of an LLM limited made the project testable offline, cheap to run, and honest by construction. The model is a tool the system calls only when it needs judgement.

The code is on [GitHub](https://github.com/fabriziogf/job-hunt-assistant), and each phase has its own write-up in the repo's technical documentation if you want the full detail.
