---
title: "Inside the Job-Hunting Agent: How It's Built"
---

A while back I wrote about [turning Laszlo Bock's *Apply Within* playbook into an agent](/Building_a_job_hunting_agent/). The idea was that a job hunt comes down to a set of repeatable, learnable moves, and that's what an agent should be good at.

So I built it: seven skills, plus job discovery, an orchestrator, live web search, persistence, and a command-line tool. This post describes the tech underneath.

---

## Determinism vs. LLM

Almost every chapter of the playbook mixes two very different kinds of rules.

Some are mechanical: "GPA below 3.5? Leave it off." "Every bullet needs a number." "Never write 'Dear Hiring Manager.'" These are pure logic. No judgement needed.

Others are judgement calls, like rewriting "Managed sorority budget" into a crisp, quantified bullet in the candidate's voice. That needs a language model.

The whole system is built around keeping the two apart. Each skill has a **deterministic core** and a **thin, optional LLM layer**. The deterministic part does most of the work: linting, selection, ordering, scoring, all the arithmetic. The model is only called for the few truly generative tasks, and it always sits behind an interface so tests can swap in a fake.

The split pays off three ways:

- **Tests need no API key.** The deterministic parts carry most of the value and are fully unit-tested offline. All 136 tests run with no network and no key.
- **It's fast and cheap.** Rejecting a resume for a missing email shouldn't cost a model call. The linters and scorers run instantly and for free.
- **Honesty gets several enforcement points.** More on that next.

---

## Enforcing "never fabricate"

The playbook's most repeated warning is *don't lie, don't stretch*. The hard part is turning that from a hope into a guarantee.

The answer is a `verified` flag on every achievement, defaulting to `False`. Only a human sets `verified=True`. The agent can draft achievements, but until a person confirms one, it isn't usable. The profile exposes a filtered view, `verified_achievements()`, and every skill only reads from that. Unconfirmed data never enters the pipeline.

For the resume, this is enforced in three independent layers:

1. **The profile** only treats verified achievements as usable.
2. **The assembler** selects only verified achievements. Unverified ones never reach the model or the output.
3. **The rewriter** refuses an unverified achievement outright, and its system prompt forbids inventing metrics, employers, or outcomes. If a bullet has no number, the model has to keep it qualitative and report `has_metric=False`. It never makes up a figure.

Each skill guards against its *own* kind of dishonesty. Networking must never invent a shared "I loved your talk at X" hook. Negotiation must never invent a competing offer. The cover letter writer can only use company facts that were actually researched.

---

## Foundation: profile store and playbook loader

Before any skill, two things had to exist that every skill depends on.

**The candidate profile** is one validated, in-memory representation of the job seeker's experience. It's a tree of Pydantic models, and at its center is the X/Y/Z achievement, modeled directly on the playbook's resume formula:

> Accomplished [X] as measured by [Y] by doing [Z].

```python
class Achievement(BaseModel):
    what: str                       # X — required
    measured_by: str | None = None  # Y — the metric
    how: str | None = None          # Z — the method
    verified: bool = False
    tags: list[str] = []
```

The metric and method are optional on purpose. Real data starts incomplete. You know *what* you did before you've pinned down the number. The model captures that partial state instead of forcing a made-up figure, and a derived `unquantified_achievements()` view becomes the to-do list for the resume builder.

**The playbook loader** is the other half. It holds a hand-curated, paraphrased summary of all eight chapters, each as a structured object with a core principle, actionable rules, formulas, and supporting stats. It exposes one method, `PLAYBOOK.as_prompt(skill)`, which renders the chapters relevant to a skill into a ready-to-use prompt block. Every skill builds its system prompt this way, so the guidance cites its chapter and stays consistent instead of being copied by hand into each skill.

What isn't committed: the PDF and any real profile are gitignored. The repo is public, the PDF is copyrighted, and a real profile is full of personal data. Tests run against a fictional candidate instead, built through the schema so it's guaranteed valid and seeded with deliberate gaps (a sub-3.5 GPA, an achievement with no metric) so the skills have something to catch.

---

## The seven skills

Each skill maps to chapters in the guide:

**Resume Builder + ATS Optimizer (Ch. 2).** A deterministic linter flags rule violations, each tagged with a severity and its source chapter. An LLM rewriter turns one verified achievement into an X/Y/Z bullet and returns validated structured output, not free text. An assembler ties it together: lint, select verified only, order most recent first with quantified bullets ahead of unquantified ones, trim to a one-page-per-decade budget, and drop a sub-3.5 GPA. The ATS Optimizer then scores the result against a job description. It extracts the posting's keywords and phrases, checks which appear in the resume, flags unexpanded acronyms, and targets a 75%+ match. Most importantly, it only *reports*. It never edits the resume to add a keyword, because that could be a claim the candidate can't back up.

**Cover Letter / Email Writer + Company Research (Ch. 3).** The chapter's thesis is that a cover letter can't win you a job, but it can lose you one. So the deterministic linter catches every downside: generic salutation, missing or wrong company name, leftover `[Company]` placeholders, and a third paragraph that claims to be tailored but doesn't reference any researched fact. The LLM writer drafts the four paragraphs. Company research is its own capability behind an interface, because the "why you, specifically" paragraph depends on real, current, verifiable facts.

**Interview Prep Coach (Ch. 5 & 6).** Mostly deterministic. The 12 questions you'll almost certainly be asked are encoded as data. The practice math turns a question count into the chapter's arithmetic (30 questions × 2 answers × 3 reps ≈ 13.5 hours), shown because that number is what gets people to practice. The LLM is only needed for role-specific questions and draft answers.

**Networking, Pipeline Tracker, Negotiation (Ch. 4, 7, 8).** The Pipeline Tracker is the first skill with no model at all. It follows the guide's volume game (roughly 100 applications → 5 first rounds → 1 offer), encodes the follow-up cadence (every 2 weeks, for 6 weeks) as a date check, and puts B-tier companies first so an offer there becomes leverage with the A-tier ones. The Negotiation Advisor computes the 10–20% ask band and the lifetime value of a raise. With the defaults, a $5,000 raise won today is worth about $944k over a career, the most motivating number in the chapter.

---

## Discovery and orchestration

With the skills built, I added two pieces to cover the full job search:

**Job discovery** reuses what already existed instead of inventing new scoring. A job's fit score *is* the ATS keyword match between the candidate's assembled resume and the posting. The same signal that says "this job is worth pursuing" also tells the resume and cover letter which keywords to address.

**The orchestrator** takes one posting and produces a single `ApplicationPackage`: a tailored resume, ATS score, interview question bank, and cover letter. The key design choice is that it's *deterministic by default*. With nothing injected, `prepare()` runs fully offline and still returns a usable package. Inject the LLM writers and each step upgrades to model quality with no change to the calling code. It's the same injection seam used everywhere else, one level up.

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

With the MVP working, I built live company research and job search.

The tempting shortcut is to ask the model what it knows about a company. But Chapter 3 is explicit that a *wrong* fact in a cover letter is what gets it rejected, and model memory is stale and prone to making things up. So the live providers use Claude's server-side web search tool in two separate calls. First, a search call returns real, cited findings. Then a structuring call shapes *only those findings* into the target schema. Splitting them keeps a clean boundary: the structuring step never sees outside "knowledge" it could slip in. Every fact carries its source, URL, and date, so the candidate can check it before sending.

---

## Enhancement 2: Persistence

Most of the system is stateless. Building a resume is a pure function of its inputs. But a real job hunt runs for months, and some things accumulate: the application pipeline, interview logs, saved packages, cached research.

The storage layer is deliberately not a database. Every model is already JSON-serializable Pydantic, so the job is just organizing JSON files well. One important detail is atomic writes: saving goes to a temp file, then `os.replace()` moves it into place. That's atomic on the same filesystem, so a crash mid-write can't corrupt `pipeline.json`. You have either the old complete file or the new one. A `Workspace` directory holds one job hunt's state with typed accessors, and a `CachedResearchProvider` wraps any research provider so an expensive live lookup costs once per company. That's the payoff of keeping research behind an interface from the start.

---

## How to run it

The project is on GitHub at [fabriziogf/job-hunt-assistant](https://github.com/fabriziogf/job-hunt-assistant). Everything except the optional AI features works free and offline.

A thin `job-hunt` command wraps the common workflows. It's built on the standard library's `argparse`, so no new dependencies, in line with the lean-stack rule. It's deterministic (every command runs without an API key; model steps are opt-in behind one `--llm` flag) and safe (it defaults to the synthetic profile and writes nothing unless you pass `--out`).

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

**3. Try it** with the built-in example candidate:

```bash
uv run job-hunt practice
```

That prints an interview practice plan and the 12 questions you'll almost certainly be asked. If you see a list, everything works.

**4. Add your own profile.** Copy the shape of `examples/sample_profile.json` into a new file at `profiles/my_profile.json` (anything in `profiles/` stays private and is never uploaded). Set `"verified": true` only on achievements that are actually true. The agent won't use anything else. Then point any command at it:

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

`prepare` tailors your resume to the job, scores the match (aim for 75%+), lists missing keywords, and writes the files to `./acme`.

**5. Track applications.** Add `--save` to a `prepare` command to log it, then:

```bash
uv run job-hunt pipeline
```

Your tracker lives in a `.jobhunt` folder. Come back any time to see which follow-ups are due. The playbook says every 2 weeks, for 6 weeks.

**6. (Optional) Turn on the AI features.** Resume rewriting, cover letter drafting, and live job search need an Anthropic API key (a paid service, billed per use):

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

Add `--help` to any command to see its options.

---

## What I learned

The most interesting lesson is how much of this supposedly AI project turned out to be deterministic. The model writes bullets and drafts letters, but the rules (what gets included, in what order, how it's scored, what's held back when unverified) are plain code. **Keeping the LLM's role small made the project testable offline, cheap to run, and honest.** The model is a tool the system calls only when it needs judgement.

The code is on [GitHub](https://github.com/fabriziogf/job-hunt-assistant), and each phase has its own write-up in the repo's technical docs if you want the full detail.
