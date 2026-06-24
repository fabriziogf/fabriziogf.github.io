---
permalink: /projects/
title: "Projects"
layout: single
author_profile: true
classes: wide
---

<p style="font-size: 1.1em; line-height: 1.7; margin-bottom: 0.5em;">
  This page collects the <strong>live outputs</strong> of projects I'm actively building — tools, models, dashboards, and experiments. Each card links directly to the finished artifact.
</p>
<p style="color: var(--global-font-color, #888); font-size: 0.88em; margin-bottom: 2rem;">
  I work across AI/ML, GenAI tooling, sports analytics, and decision systems. Projects here range from polished prototypes to early releases.
</p>

---

<div class="proj-grid">

  <!-- ── TEMPLATE CARD — duplicate and fill in for each project ── -->

  <div class="proj-card proj-status-active">
    <div class="proj-header">
      <span class="proj-tag">Sports Analytics</span>
      <span class="proj-status-badge">Active</span>
    </div>
    <h3 class="proj-title">World Cup 2026 Prediction Model</h3>
    <p class="proj-desc">
      Monte Carlo tournament simulator built on Dixon-Coles and Elo ratings. Backtested across 2014–2022 World Cups with Brier score and calibration analysis.
    </p>
    <div class="proj-meta">
      <span>Python · Monte Carlo · Dixon-Coles</span>
    </div>
    <div class="proj-links">
      <a href="/World_Cup_prediction_model_part10/" class="proj-cta">Read the writeup →</a>
      <a href="https://github.com/fabriziogf/world_cup_model" class="proj-cta" target="_blank" rel="noopener">View code →</a>
    </div>
  </div>

  <div class="proj-card proj-status-active">
    <div class="proj-header">
      <span class="proj-tag">Triathlon</span>
      <span class="proj-status-badge">Active</span>
    </div>
    <h3 class="proj-title">Training Dashboard</h3>
    <p class="proj-desc">
      Live 7-day rolling window of swim, bike, run, and strength training. Activity data is pulled from Strava daily, with fitness metrics (CTL, ATL, TSB) and training load (TSS) from TrainingPeaks. Shows session-level detail, 12-month trends, and personal records.
    </p>
    <div class="proj-meta">
      <span>Python · Jekyll · Strava API · TrainingPeaks API</span>
    </div>
    <a href="/training/" class="proj-cta">View dashboard →</a>
  </div>

  <div class="proj-card proj-status-wip">
    <div class="proj-header">
      <span class="proj-tag">GenAI</span>
      <span class="proj-status-badge proj-badge-wip">In progress</span>
    </div>
    <h3 class="proj-title">Job Hunting Agent</h3>
    <p class="proj-desc">
      An AI agent that helps a candidate run a full job search end-to-end — resume, cover letter, networking, interview prep, application tracking, and offer negotiation — with advice grounded in a concrete playbook rather than generic LLM intuition.
    </p>
    <div class="proj-meta">
      <span>Python · Anthropic SDK · Claude Code</span>
    </div>
    <div class="proj-links">
      <a href="/Job_hunting_agent_technical_implementation/" class="proj-cta">Read the writeup →</a>
      <a href="https://github.com/fabriziogf/job-hunt-assistant" class="proj-cta" target="_blank" rel="noopener">View code →</a>
    </div>
  </div>

</div>

---

<p style="font-size: 0.85em; color: var(--global-font-color, #888);">
  For context on how these projects were built, see the <a href="/year-archive/">blog posts</a>.
</p>

<style>
.proj-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  margin: 2rem 0;
}

.proj-card {
  border-radius: 8px;
  padding: 1.4rem 1.5rem;
  background: rgba(128, 128, 128, 0.07);
  border: 1px solid rgba(128, 128, 128, 0.15);
  border-top: 3px solid #4fc3f7;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  transition: box-shadow 0.2s, transform 0.2s;
}

.proj-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.proj-card.proj-status-wip {
  border-top-color: #ffb74d;
  opacity: 0.8;
}

.proj-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.proj-tag {
  font-size: 0.72em;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #4fc3f7;
  font-weight: 600;
}

.proj-card.proj-status-wip .proj-tag {
  color: #ffb74d;
}

.proj-status-badge {
  font-size: 0.7em;
  padding: 0.2em 0.6em;
  border-radius: 20px;
  background: rgba(79, 195, 247, 0.15);
  color: #4fc3f7;
  font-weight: 600;
  letter-spacing: 0.03em;
}

.proj-badge-wip {
  background: rgba(255, 183, 77, 0.15);
  color: #ffb74d;
}

.proj-title {
  font-size: 1.1em;
  font-weight: 700;
  margin: 0;
  line-height: 1.3;
}

.proj-desc {
  font-size: 0.88em;
  line-height: 1.6;
  margin: 0;
  flex-grow: 1;
}

.proj-meta {
  font-size: 0.75em;
  color: var(--global-font-color, #888);
  opacity: 0.7;
  font-family: monospace;
}

.proj-links {
  display: flex;
  flex-wrap: wrap;
  gap: 1.2rem;
  margin-top: 0.4rem;
}

.proj-cta {
  display: inline-block;
  margin-top: 0.4rem;
  font-size: 0.85em;
  font-weight: 600;
  color: #4fc3f7;
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: border-color 0.15s;
  align-self: flex-start;
}

.proj-links .proj-cta {
  margin-top: 0;
}

.proj-cta:hover {
  border-bottom-color: #4fc3f7;
  text-decoration: none;
}

.proj-cta-disabled {
  color: var(--global-font-color, #888);
  opacity: 0.5;
  cursor: default;
  pointer-events: none;
}
</style>
