---
permalink: /training/
title: "Training Dashboard"
layout: single
author_profile: true
classes: wide
---

{% assign td = site.data.training_data %}

<p style="color: var(--global-font-color, #888); font-size: 0.85em; margin-top: -0.5em;">
  Rolling 7-day window: <strong>{{ td.window_start }}</strong> → <strong>{{ td.window_end }}</strong> &nbsp;·&nbsp; Updated: {{ td.generated_at }}
</p>

---

## Fitness (PMC)

<div style="display: flex; gap: 1.5rem; flex-wrap: wrap; margin-bottom: 2rem;">
  <div class="td-stat-card td-card-ctl">
    <div class="td-stat-label">Fitness (CTL)</div>
    <div class="td-stat-value">{{ td.fitness.ctl }}</div>
  </div>
  <div class="td-stat-card td-card-atl">
    <div class="td-stat-label">Fatigue (ATL)</div>
    <div class="td-stat-value">{{ td.fitness.atl }}</div>
  </div>
  <div class="td-stat-card {% if td.fitness.tsb >= 0 %}td-card-tsb-pos{% else %}td-card-tsb-neg{% endif %}">
    <div class="td-stat-label">Form (TSB)</div>
    <div class="td-stat-value">{{ td.fitness.tsb }}</div>
  </div>
</div>

---

## 7-Day Summary

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
{% for sport in "swim,bike,run,strength" | split: "," %}
  {% assign s = td.totals[sport] %}
  {% if sport == "swim"     %} {% assign icon = "🏊" %} {% assign color = "#4fc3f7" %} {% endif %}
  {% if sport == "bike"     %} {% assign icon = "🚴" %} {% assign color = "#81c784" %} {% endif %}
  {% if sport == "run"      %} {% assign icon = "🏃" %} {% assign color = "#ffb74d" %} {% endif %}
  {% if sport == "strength" %} {% assign icon = "🏋️" %} {% assign color = "#ce93d8" %} {% endif %}
  <div class="td-sport-card" style="border-top: 3px solid {{ color }};">
    <div class="td-sport-title">{{ icon }} {{ sport | capitalize }}</div>
    <div class="td-sport-row"><span>Sessions</span><strong>{{ s.sessions }}</strong></div>
    <div class="td-sport-row"><span>Hours</span><strong>{{ s.hours }}h</strong></div>
    {% if sport != "strength" %}
    <div class="td-sport-row"><span>Distance</span><strong>{{ s.distance_km }} km</strong></div>
    {% endif %}
    <div class="td-sport-row"><span>TSS</span><strong>{{ s.tss }}</strong></div>
  </div>
{% endfor %}
</div>

**Total TSS:** {{ td.totals.swim.tss | plus: td.totals.bike.tss | plus: td.totals.run.tss | plus: td.totals.strength.tss }}
&nbsp;·&nbsp;
**Total Hours:** {{ td.totals.swim.hours | plus: td.totals.bike.hours | plus: td.totals.run.hours | plus: td.totals.strength.hours }}h

---

## Daily TSS by Sport

<canvas id="chartDailyTSS" height="90"></canvas>

---

## Daily Hours by Sport

<canvas id="chartDailyHours" height="90"></canvas>

---

## TSS Distribution

<div style="max-width: 340px; margin: 0 auto 2rem;">
  <canvas id="chartTSSDonut"></canvas>
</div>

---

## Sessions This Week

| Date | Sport | Session | Hours | Distance | TSS |
|------|-------|---------|------:|----------:|----:|
{% for w in td.workouts %}
{% if w.sport == "swim"     %} {% assign sport_icon = "🏊" %} {% endif %}
{% if w.sport == "bike"     %} {% assign sport_icon = "🚴" %} {% endif %}
{% if w.sport == "run"      %} {% assign sport_icon = "🏃" %} {% endif %}
{% if w.sport == "strength" %} {% assign sport_icon = "🏋️" %} {% endif %}
{% if w.sport == "other"    %} {% assign sport_icon = "⚡" %} {% endif %}
| {{ w.date }} | {{ sport_icon }} {{ w.sport | capitalize }} | {{ w.title }} | {{ w.hours }}h | {% if w.distance_km > 0 %}{{ w.distance_km }} km{% else %}—{% endif %} | {{ w.tss }} |
{% endfor %}

---

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
(function () {
  // ── Palette ──────────────────────────────────────────────────────────────
  const COLORS = {
    swim:     '#4fc3f7',
    bike:     '#81c784',
    run:      '#ffb74d',
    strength: '#ce93d8',
    other:    '#90a4ae',
  };

  // ── Data injected from Jekyll / YAML ─────────────────────────────────────
  const daily = [
    {% for d in td.daily %}
    {
      date:     "{{ d.date }}",
      swim:     { tss: {{ d.swim.tss }},     hours: {{ d.swim.hours }}     },
      bike:     { tss: {{ d.bike.tss }},     hours: {{ d.bike.hours }}     },
      run:      { tss: {{ d.run.tss }},      hours: {{ d.run.hours }}      },
      strength: { tss: {{ d.strength.tss }}, hours: {{ d.strength.hours }} },
    },
    {% endfor %}
  ];

  const totals = {
    swim:     {{ td.totals.swim.tss }},
    bike:     {{ td.totals.bike.tss }},
    run:      {{ td.totals.run.tss }},
    strength: {{ td.totals.strength.tss }},
  };

  // ── Shared options ────────────────────────────────────────────────────────
  const labels   = daily.map(d => {
    const dt = new Date(d.date + 'T00:00:00');
    return dt.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  });
  const sports   = ['swim', 'bike', 'run', 'strength'];
  const barOpts  = {
    responsive: true,
    plugins: { legend: { position: 'bottom' } },
    scales: {
      x: { stacked: true },
      y: { stacked: true, beginAtZero: true },
    },
  };

  // ── Chart 1: Daily TSS ────────────────────────────────────────────────────
  new Chart(document.getElementById('chartDailyTSS'), {
    type: 'bar',
    data: {
      labels,
      datasets: sports.map(s => ({
        label:           s.charAt(0).toUpperCase() + s.slice(1),
        data:            daily.map(d => d[s].tss),
        backgroundColor: COLORS[s],
      })),
    },
    options: { ...barOpts, plugins: { ...barOpts.plugins,
      title: { display: true, text: 'Daily TSS by Sport' } } },
  });

  // ── Chart 2: Daily Hours ──────────────────────────────────────────────────
  new Chart(document.getElementById('chartDailyHours'), {
    type: 'bar',
    data: {
      labels,
      datasets: sports.map(s => ({
        label:           s.charAt(0).toUpperCase() + s.slice(1),
        data:            daily.map(d => d[s].hours),
        backgroundColor: COLORS[s],
      })),
    },
    options: { ...barOpts, plugins: { ...barOpts.plugins,
      title: { display: true, text: 'Daily Hours by Sport' } },
      scales: { ...barOpts.scales,
        y: { stacked: true, beginAtZero: true,
             ticks: { callback: v => v + 'h' } } },
    },
  });

  // ── Chart 3: TSS Donut ────────────────────────────────────────────────────
  new Chart(document.getElementById('chartTSSDonut'), {
    type: 'doughnut',
    data: {
      labels: sports.map(s => s.charAt(0).toUpperCase() + s.slice(1)),
      datasets: [{
        data:            sports.map(s => totals[s]),
        backgroundColor: sports.map(s => COLORS[s]),
        hoverOffset:     8,
      }],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom' },
        title:  { display: true, text: 'TSS Distribution' },
      },
    },
  });
})();
</script>

<style>
.td-stat-card {
  flex: 1; min-width: 120px;
  padding: 1rem 1.25rem;
  border-radius: 6px;
  text-align: center;
  background: rgba(128,128,128,0.08);
}
.td-stat-label { font-size: 0.78em; text-transform: uppercase; letter-spacing: .05em; opacity: .7; }
.td-stat-value { font-size: 2em; font-weight: 700; margin-top: .1em; }
.td-card-ctl    { border-top: 3px solid #4fc3f7; }
.td-card-atl    { border-top: 3px solid #ef9a9a; }
.td-card-tsb-pos { border-top: 3px solid #81c784; }
.td-card-tsb-neg { border-top: 3px solid #ef9a9a; }

.td-sport-card {
  padding: .85rem 1rem;
  border-radius: 6px;
  background: rgba(128,128,128,0.08);
}
.td-sport-title { font-weight: 600; font-size: 1em; margin-bottom: .5rem; }
.td-sport-row   { display: flex; justify-content: space-between; font-size: .88em; padding: .15rem 0; }
</style>
