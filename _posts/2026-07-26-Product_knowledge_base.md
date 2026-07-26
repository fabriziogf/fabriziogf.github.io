---
title: "Building a Knowledge Base for Product Work"
---

Most of a PM's job is building and disseminating context. Which products you own, how their capabilities fit together, what shipped last quarter, why a decision was made, what a stakeholder cares about. That context lives in scattered docs, Slack threads, and my head. The latter is the least reliable of the three, but the one which connects all the other disparate information. This post is about how I have build a knowledge base so I stop being the single point of failure for my own context.

---

## The scope problem

The hard part about building this knowledhe base is my scope as a PM. I don't own one product, but a set of products, each with its own capabilities and features. The value of the context is in how they connect. A feature only makes sense against the capability it belongs to, which only makes sense against the product it serves, which only makes sense against what I'm accountable for.

So the knowledge base is organized around **product ownership**, not around documents. The top level is what I own. Under each product are its capabilities, under each capability its features, and cross-links between them where they actually interact. When I ask a question, the AI can walk that structure the way I would in my head: start at ownership, drill down to the feature, and pick up the connections on the way.

Flat folders of meeting notes don't reflect this complexity, and the context is structured so that the LLM can provide strategically-consistent reponses. This is a deliberate choice to skip a vector database and a RAG pipeline. Andrej Karpathy [described](https://venturebeat.com/data/karpathy-shares-llm-knowledge-base-architecture-that-bypasses-rag-with-an) the same idea: for a personal corpus, let the model read a well-organized set of interlinked markdown files directly, navigating by index and summaries. Under roughly 100K tokens it tends to beat RAG and saves all the setup.

## The master file

Everything funnels into one master `.md` file that holds the latest, most relevant context. It's the file an AI reads first, before it answers anything — the same pattern Claude Code uses with a `CLAUDE.md`, a curated file that tells the AI what it needs to know before every task, applied to product context instead of code.

The whole challenge of that file is that it must balance **completeness and brevity.** Too sparse and the AI is missing the context that makes its answer useful. Too complete and it's a dump that can become stale, bloated, and slow to read. So the master file isn't an archive. It's a running summary: current state of each product, live decisions, what's changed recently, and pointers to the deeper notes when detail is needed. The archive lives elsewhere, while the master file stays lean.

Every so often, I read it and evaluate on whether a new teammate would understand what I own and where things stand if they only read that file. If a section is outdated, it should be deleted. I also have an agent do this pass to dedupe, prune stale sections, and keep the file lean.

## Keeping it fresh

A knowledge base that isn't updated is just old notes. The two things that keep mine current are artifacts and daily updates:

**Artifacts** — The actual outputs of my work are the highest-signal source I have. Specs, review docs, decision memos, prototypes. When I finish one, its key points get folded into the knowledge base. If there is conflicting information, the latest artifact takes precedence.

**Daily updates** - A few lines at the end of the day on what moved and what changed. These snipets ensure freshness but also build context about the progression of a product or project.

Both of these are still manual, and that's the part I most want to change. The direction I'm heading is live connections — wiring the knowledge base to the tools where context is actually created, like Slack, the issue tracker, docs, and analytics, so it pulls current state instead of me pasting it in.

## Notes by hand, uploaded

I still write notes by hand, as it helps me remember it. Then, daily or weekly, I photograph the notes and upload the pictures into the knowledge base. The AI reads the images, pulls out what matters, and merges it in.

I get both things: the memory benefit of writing by hand, and a knowledge base that doesn't lose what I wrote on paper. The same principle extends to meeting transcripts and voice memos, auto-summarized into notes — anything that lowers the friction of getting reality into the base without extra writing time.

## Conclusion

The overall approach is that this is a context system my AI tools retrieve from. The tools are getting better fast, but they're only as good as the context I can hand them. Like many things in daily life, building this knowledge base is a habit that makes me and my agents more productive.
