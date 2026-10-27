---
title: "Building a Knowledge Base for Product and AI Work"
---

Most of a PM's job is building and sharing context: which products you own, how their capabilities fit together, what shipped last quarter, why a decision was made, what a stakeholder cares about. That context lives in scattered docs, Slack threads, and my head. My head is the least reliable of the three, but it's the one that connects everything else. This post is about the knowledge base I built so I stop being the single point of failure for my own context.

---

## The scope problem

The hard part is my scope. I don't own one product but a set of products, each with its own capabilities and features. The value is in how they connect. A feature only makes sense against the capability it belongs to, which only makes sense against the product it serves, which only makes sense against what I'm accountable for.

So the knowledge base is organized around **product ownership**, not documents. The top level is what I own. Under each product are its capabilities, under each capability its features, with cross-links where they actually interact. When I ask a question, the AI can walk that structure the way I would in my head: start at ownership, drill down to the feature, and pick up the connections on the way.

Flat folders of meeting notes can't capture that, and the structure is what lets the LLM give strategically consistent answers. I deliberately skipped a vector database and a RAG pipeline. Andrej Karpathy [described](https://venturebeat.com/data/karpathy-shares-llm-knowledge-base-architecture-that-bypasses-rag-with-an) the same idea: for a personal corpus, let the model read a well-organized set of interlinked markdown files directly, navigating by index and summaries. Under roughly 100K tokens it tends to beat RAG and skips all the setup.

## The master file

Everything feeds one master `.md` file with the latest, most relevant context. It's the file the AI reads first, before answering anything. It's the same pattern Claude Code uses with `CLAUDE.md`, a curated file that tells the AI what it needs to know before every task, applied to product context instead of code.

The challenge is balancing **completeness and brevity.** Too sparse and the AI lacks the context that makes its answer useful. Too complete and it becomes a dump that goes stale, bloats, and is slow to read. So the master file isn't an archive. It's a running summary: the current state of each product, open decisions, recent changes, and pointers to deeper notes when detail is needed. The archive lives elsewhere, and the master file stays lean.

Every so often I reread it and ask: if a new teammate read only this file, would they understand what I own and where things stand? Outdated sections get deleted. I also have an agent do a pass to dedupe, prune stale sections, and keep it lean.

## Keeping it fresh

A knowledge base that isn't updated is just old notes. Two things keep mine current: artifacts and daily updates.

**Artifacts**: the actual outputs of my work are my highest-signal source. Specs, review docs, decision memos, prototypes. When I finish one, its key points go into the knowledge base. When information conflicts, the latest artifact wins.

**Daily updates**: a few lines at the end of the day on what moved and what changed. They keep things fresh and build up a record of how a product or project progressed.

Both are still manual, and that's what I most want to change. The direction I'm heading is live connections: wiring the knowledge base to the tools where context is created, like Slack, the issue tracker, docs, and analytics, so it pulls current state instead of me pasting it in.

## Handwritten notes, uploaded

I still take notes by hand because it helps me remember. Then, daily or weekly, I photograph them and upload the pictures to the knowledge base. The AI reads the images, pulls out what matters, and merges it in.

I get both: the memory benefit of writing by hand, and a knowledge base that doesn't lose what I wrote on paper. The same idea extends to meeting transcripts and voice memos, auto-summarized into notes. Anything that makes it easier to get reality into the base without extra writing time.

## Conclusion

This is a context system my AI tools pull from. The tools are getting better fast, but **they're only as good as the context I can give them.** Like a lot of things in daily life, building this knowledge base is a habit, and it makes both me and my agents more productive.
