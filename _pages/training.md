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

<!-- ══ TAB NAV ═══════════════════════════════════════════════════════════════ -->
<div class="td-tabs" role="tablist">
  <button class="td-tab td-tab-active" onclick="tdShowTab('week',this)"  role="tab">This Week</button>
  <button class="td-tab"               onclick="tdShowTab('trends',this)" role="tab">12-Month Trends</button>
  <button class="td-tab"               onclick="tdShowTab('prs',this)"    role="tab">Personal Records</button>
</div>

<!-- ══════════════════════════════════════════════════════════════════════════
     TAB 1 — THIS WEEK
     ══════════════════════════════════════════════════════════════════════ -->
<div id="tab-week" class="td-panel">

  <h2 style="margin-top:1.5rem">Fitness (PMC)</h2>

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

  <h2>7-Day Summary</h2>

  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
    <div class="td-sport-card" style="border-top: 3px solid #4fc3f7;">
      <div class="td-sport-title">🏊 Swim</div>
      <div class="td-sport-row"><span>Sessions</span><strong>{{ td.totals.swim.sessions }}</strong></div>
      <div class="td-sport-row"><span>Hours</span><strong>{{ td.totals.swim.hours }}h</strong></div>
      <div class="td-sport-row"><span>Distance</span><strong>{{ td.totals.swim.distance_km }} km</strong></div>
      <div class="td-sport-row"><span>TSS</span><strong>{{ td.totals.swim.tss }}</strong></div>
    </div>
    <div class="td-sport-card" style="border-top: 3px solid #81c784;">
      <div class="td-sport-title">🚴 Bike</div>
      <div class="td-sport-row"><span>Sessions</span><strong>{{ td.totals.bike.sessions }}</strong></div>
      <div class="td-sport-row"><span>Hours</span><strong>{{ td.totals.bike.hours }}h</strong></div>
      <div class="td-sport-row"><span>Distance</span><strong>{{ td.totals.bike.distance_km }} km</strong></div>
      <div class="td-sport-row"><span>TSS</span><strong>{{ td.totals.bike.tss }}</strong></div>
    </div>
    <div class="td-sport-card" style="border-top: 3px solid #ffb74d;">
      <div class="td-sport-title">🏃 Run</div>
      <div class="td-sport-row"><span>Sessions</span><strong>{{ td.totals.run.sessions }}</strong></div>
      <div class="td-sport-row"><span>Hours</span><strong>{{ td.totals.run.hours }}h</strong></div>
      <div class="td-sport-row"><span>Distance</span><strong>{{ td.totals.run.distance_km }} km</strong></div>
      <div class="td-sport-row"><span>TSS</span><strong>{{ td.totals.run.tss }}</strong></div>
    </div>
    <div class="td-sport-card" style="border-top: 3px solid #ce93d8;">
      <div class="td-sport-title">🏋️ Strength</div>
      <div class="td-sport-row"><span>Sessions</span><strong>{{ td.totals.strength.sessions }}</strong></div>
      <div class="td-sport-row"><span>Hours</span><strong>{{ td.totals.strength.hours }}h</strong></div>
      <div class="td-sport-row"><span>TSS</span><strong>{{ td.totals.strength.tss }}</strong></div>
    </div>
  </div>

  **Total TSS:** {{ td.totals.swim.tss | plus: td.totals.bike.tss | plus: td.totals.run.tss | plus: td.totals.strength.tss }}
  &nbsp;·&nbsp;
  **Total Hours:** {{ td.totals.swim.hours | plus: td.totals.bike.hours | plus: td.totals.run.hours | plus: td.totals.strength.hours }}h

  ---

  <h2>Daily TSS by Sport</h2>
  <canvas id="chartDailyTSS" height="90"></canvas>

  ---

  <h2>Daily Hours by Sport</h2>
  <canvas id="chartDailyHours" height="90"></canvas>

  ---

  <h2>TSS Distribution</h2>
  <div style="max-width: 340px; margin: 0 auto 2rem;">
    <canvas id="chartTSSDonut"></canvas>
  </div>

  ---

  <h2>Sessions This Week</h2>

  <table id="sessions-table" style="width:100%; border-collapse: collapse; font-size: 0.9em;">
    <thead>
      <tr>
        <th style="text-align:left;  padding:.4rem .6rem; border-bottom:2px solid rgba(128,128,128,.3);">Date</th>
        <th style="text-align:left;  padding:.4rem .6rem; border-bottom:2px solid rgba(128,128,128,.3);">Sport</th>
        <th style="text-align:left;  padding:.4rem .6rem; border-bottom:2px solid rgba(128,128,128,.3);">Session</th>
        <th style="text-align:right; padding:.4rem .6rem; border-bottom:2px solid rgba(128,128,128,.3);">Hours</th>
        <th style="text-align:right; padding:.4rem .6rem; border-bottom:2px solid rgba(128,128,128,.3);">Distance</th>
        <th style="text-align:right; padding:.4rem .6rem; border-bottom:2px solid rgba(128,128,128,.3);">TSS</th>
        <th style="text-align:right; padding:.4rem .6rem; border-bottom:2px solid rgba(128,128,128,.3);">Avg HR</th>
        <th style="text-align:right; padding:.4rem .6rem; border-bottom:2px solid rgba(128,128,128,.3);">Avg Power</th>
      </tr>
    </thead>
    <tbody>
      {% for w in td.workouts %}
      {% if w.sport == "swim"     %}{% assign sport_icon = "🏊" %}{% assign sport_color = "#4fc3f7" %}{% endif %}
      {% if w.sport == "bike"     %}{% assign sport_icon = "🚴" %}{% assign sport_color = "#81c784" %}{% endif %}
      {% if w.sport == "run"      %}{% assign sport_icon = "🏃" %}{% assign sport_color = "#ffb74d" %}{% endif %}
      {% if w.sport == "strength" %}{% assign sport_icon = "🏋️" %}{% assign sport_color = "#ce93d8" %}{% endif %}
      {% if w.sport == "other"    %}{% assign sport_icon = "⚡" %}{% assign sport_color = "#90a4ae" %}{% endif %}
      <tr class="session-row" style="border-bottom:1px solid rgba(128,128,128,.15); cursor:pointer;"
          onclick="tdToggleRow(this)">
        <td style="padding:.4rem .6rem;">{{ w.date }}</td>
        <td style="padding:.4rem .6rem;"><span style="color:{{ sport_color }};font-weight:600;">{{ sport_icon }} {{ w.sport | capitalize }}</span></td>
        <td style="padding:.4rem .6rem;">{{ w.title }}</td>
        <td style="padding:.4rem .6rem;text-align:right;">{{ w.hours }}h</td>
        <td style="padding:.4rem .6rem;text-align:right;">{% if w.distance_km > 0 %}{{ w.distance_km }} km{% else %}—{% endif %}</td>
        <td style="padding:.4rem .6rem;text-align:right;">{{ w.tss }}</td>
        <td style="padding:.4rem .6rem;text-align:right;">{% if w.hr_avg %}{{ w.hr_avg }} bpm{% else %}—{% endif %}</td>
        <td style="padding:.4rem .6rem;text-align:right;">{% if w.power_avg %}{{ w.power_avg }} W{% else %}—{% endif %}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

</div><!-- /tab-week -->


<!-- ══════════════════════════════════════════════════════════════════════════
     TAB 2 — 12-MONTH TRENDS
     ══════════════════════════════════════════════════════════════════════ -->
<div id="tab-trends" class="td-panel" style="display:none;">

  <h2 style="margin-top:1.5rem">Monthly TSS by Sport</h2>
  <canvas id="chartMonthlyTSS" height="100"></canvas>

  ---

  <h2>Monthly Hours by Sport</h2>
  <canvas id="chartMonthlyHours" height="100"></canvas>

  ---

  <h2>CTL / ATL Trend</h2>
  <p style="font-size:.85em;color:#888;margin-top:-.5em;">End-of-day values, one per calendar day over the past 12 months.</p>
  <canvas id="chartCTL" height="90"></canvas>

  ---

  <h2>Monthly Volume Heatmap</h2>
  <div id="heatmap-container" style="overflow-x:auto;margin-bottom:2rem;"></div>

</div><!-- /tab-trends -->


<!-- ══════════════════════════════════════════════════════════════════════════
     TAB 3 — PERSONAL RECORDS
     ══════════════════════════════════════════════════════════════════════ -->
<div id="tab-prs" class="td-panel" style="display:none;">

  <div style="margin-top:1.5rem;display:flex;gap:.6rem;flex-wrap:wrap;margin-bottom:1.5rem;">
    <button class="td-pr-toggle td-pr-toggle-active" onclick="tdPRToggle('this_year',this)">2026 (This Year)</button>
    <button class="td-pr-toggle" onclick="tdPRToggle('all_time',this)">All-Time</button>
  </div>

  <!-- ── Bike ── -->
  <h3 style="color:#81c784;margin-top:2rem;margin-bottom:.6rem;">🚴 Bike — Peak Power</h3>

  <table class="td-pr-table">
    <thead>
      <tr>
        <th>Duration</th>
        <th class="pr-this-year">2026 Best</th>
        <th class="pr-this-year">Date</th>
        <th class="pr-this-year">Session</th>
        <th class="pr-all-time" style="display:none">All-Time Best</th>
        <th class="pr-all-time" style="display:none">Date</th>
        <th class="pr-all-time" style="display:none">Session</th>
      </tr>
    </thead>
    <tbody>
      {% assign bike_prs = td.prs.bike %}
      <tr>
        <td>{{ bike_prs.power5sec.label }}</td>
        <td class="pr-this-year td-pr-value">{% if bike_prs.power5sec.this_year %}{{ bike_prs.power5sec.this_year }} W{% else %}<span class="td-pr-null">—</span>{% endif %}</td>
        <td class="pr-this-year td-pr-date">{{ bike_prs.power5sec.this_year_date }}</td>
        <td class="pr-this-year td-pr-workout">{{ bike_prs.power5sec.this_year_workout }}</td>
        <td class="pr-all-time td-pr-value" style="display:none">{% if bike_prs.power5sec.all_time %}{{ bike_prs.power5sec.all_time }} W{% else %}<span class="td-pr-null">—</span>{% endif %}</td>
        <td class="pr-all-time td-pr-date" style="display:none">{{ bike_prs.power5sec.all_time_date }}</td>
        <td class="pr-all-time td-pr-workout" style="display:none">{{ bike_prs.power5sec.all_time_workout }}</td>
      </tr>
      <tr>
        <td>{{ bike_prs.power1min.label }}</td>
        <td class="pr-this-year td-pr-value">{% if bike_prs.power1min.this_year %}{{ bike_prs.power1min.this_year }} W{% else %}<span class="td-pr-null">—</span>{% endif %}</td>
        <td class="pr-this-year td-pr-date">{{ bike_prs.power1min.this_year_date }}</td>
        <td class="pr-this-year td-pr-workout">{{ bike_prs.power1min.this_year_workout }}</td>
        <td class="pr-all-time td-pr-value" style="display:none">{% if bike_prs.power1min.all_time %}{{ bike_prs.power1min.all_time }} W{% else %}<span class="td-pr-null">—</span>{% endif %}</td>
        <td class="pr-all-time td-pr-date" style="display:none">{{ bike_prs.power1min.all_time_date }}</td>
        <td class="pr-all-time td-pr-workout" style="display:none">{{ bike_prs.power1min.all_time_workout }}</td>
      </tr>
      <tr>
        <td>{{ bike_prs.power5min.label }}</td>
        <td class="pr-this-year td-pr-value">{% if bike_prs.power5min.this_year %}{{ bike_prs.power5min.this_year }} W{% else %}<span class="td-pr-null">—</span>{% endif %}</td>
        <td class="pr-this-year td-pr-date">{{ bike_prs.power5min.this_year_date }}</td>
        <td class="pr-this-year td-pr-workout">{{ bike_prs.power5min.this_year_workout }}</td>
        <td class="pr-all-time td-pr-value" style="display:none">{% if bike_prs.power5min.all_time %}{{ bike_prs.power5min.all_time }} W{% else %}<span class="td-pr-null">—</span>{% endif %}</td>
        <td class="pr-all-time td-pr-date" style="display:none">{{ bike_prs.power5min.all_time_date }}</td>
        <td class="pr-all-time td-pr-workout" style="display:none">{{ bike_prs.power5min.all_time_workout }}</td>
      </tr>
      <tr>
        <td>{{ bike_prs.power10min.label }}</td>
        <td class="pr-this-year td-pr-value">{% if bike_prs.power10min.this_year %}{{ bike_prs.power10min.this_year }} W{% else %}<span class="td-pr-null">—</span>{% endif %}</td>
        <td class="pr-this-year td-pr-date">{{ bike_prs.power10min.this_year_date }}</td>
        <td class="pr-this-year td-pr-workout">{{ bike_prs.power10min.this_year_workout }}</td>
        <td class="pr-all-time td-pr-value" style="display:none">{% if bike_prs.power10min.all_time %}{{ bike_prs.power10min.all_time }} W{% else %}<span class="td-pr-null">—</span>{% endif %}</td>
        <td class="pr-all-time td-pr-date" style="display:none">{{ bike_prs.power10min.all_time_date }}</td>
        <td class="pr-all-time td-pr-workout" style="display:none">{{ bike_prs.power10min.all_time_workout }}</td>
      </tr>
      <tr>
        <td>{{ bike_prs.power20min.label }}</td>
        <td class="pr-this-year td-pr-value">{% if bike_prs.power20min.this_year %}{{ bike_prs.power20min.this_year }} W{% else %}<span class="td-pr-null">—</span>{% endif %}</td>
        <td class="pr-this-year td-pr-date">{{ bike_prs.power20min.this_year_date }}</td>
        <td class="pr-this-year td-pr-workout">{{ bike_prs.power20min.this_year_workout }}</td>
        <td class="pr-all-time td-pr-value" style="display:none">{% if bike_prs.power20min.all_time %}{{ bike_prs.power20min.all_time }} W{% else %}<span class="td-pr-null">—</span>{% endif %}</td>
        <td class="pr-all-time td-pr-date" style="display:none">{{ bike_prs.power20min.all_time_date }}</td>
        <td class="pr-all-time td-pr-workout" style="display:none">{{ bike_prs.power20min.all_time_workout }}</td>
      </tr>
      <tr>
        <td>{{ bike_prs.power60min.label }}</td>
        <td class="pr-this-year td-pr-value">{% if bike_prs.power60min.this_year %}{{ bike_prs.power60min.this_year }} W{% else %}<span class="td-pr-null">—</span>{% endif %}</td>
        <td class="pr-this-year td-pr-date">{{ bike_prs.power60min.this_year_date }}</td>
        <td class="pr-this-year td-pr-workout">{{ bike_prs.power60min.this_year_workout }}</td>
        <td class="pr-all-time td-pr-value" style="display:none">{% if bike_prs.power60min.all_time %}{{ bike_prs.power60min.all_time }} W{% else %}<span class="td-pr-null">—</span>{% endif %}</td>
        <td class="pr-all-time td-pr-date" style="display:none">{{ bike_prs.power60min.all_time_date }}</td>
        <td class="pr-all-time td-pr-workout" style="display:none">{{ bike_prs.power60min.all_time_workout }}</td>
      </tr>
    </tbody>
  </table>

  <!-- ── Run ── -->
  <h3 style="color:#ffb74d;margin-top:2rem;margin-bottom:.6rem;">🏃 Run — Pace</h3>

  <table class="td-pr-table">
    <thead>
      <tr>
        <th>Distance</th>
        <th class="pr-this-year">2026 Best</th>
        <th class="pr-this-year">Date</th>
        <th class="pr-this-year">Session</th>
        <th class="pr-all-time" style="display:none">All-Time Best</th>
        <th class="pr-all-time" style="display:none">Date</th>
        <th class="pr-all-time" style="display:none">Session</th>
      </tr>
    </thead>
    <tbody>
      {% assign run_prs = td.prs.run %}
      <tr>
        <td>{{ run_prs.speed1K.label }}</td>
        <td class="pr-this-year td-pr-value">{% if run_prs.speed1K.this_year %}{{ run_prs.speed1K.this_year }}/km{% else %}<span class="td-pr-null">—</span>{% endif %}</td>
        <td class="pr-this-year td-pr-date">{{ run_prs.speed1K.this_year_date }}</td>
        <td class="pr-this-year td-pr-workout">{{ run_prs.speed1K.this_year_workout }}</td>
        <td class="pr-all-time td-pr-value" style="display:none">{% if run_prs.speed1K.all_time %}{{ run_prs.speed1K.all_time }}/km{% else %}<span class="td-pr-null">—</span>{% endif %}</td>
        <td class="pr-all-time td-pr-date" style="display:none">{{ run_prs.speed1K.all_time_date }}</td>
        <td class="pr-all-time td-pr-workout" style="display:none">{{ run_prs.speed1K.all_time_workout }}</td>
      </tr>
      <tr>
        <td>{{ run_prs.speed5K.label }}</td>
        <td class="pr-this-year td-pr-value">{% if run_prs.speed5K.this_year %}{{ run_prs.speed5K.this_year }}/km{% else %}<span class="td-pr-null">—</span>{% endif %}</td>
        <td class="pr-this-year td-pr-date">{{ run_prs.speed5K.this_year_date }}</td>
        <td class="pr-this-year td-pr-workout">{{ run_prs.speed5K.this_year_workout }}</td>
        <td class="pr-all-time td-pr-value" style="display:none">{% if run_prs.speed5K.all_time %}{{ run_prs.speed5K.all_time }}/km{% else %}<span class="td-pr-null">—</span>{% endif %}</td>
        <td class="pr-all-time td-pr-date" style="display:none">{{ run_prs.speed5K.all_time_date }}</td>
        <td class="pr-all-time td-pr-workout" style="display:none">{{ run_prs.speed5K.all_time_workout }}</td>
      </tr>
      <tr>
        <td>{{ run_prs.speed10K.label }}</td>
        <td class="pr-this-year td-pr-value">{% if run_prs.speed10K.this_year %}{{ run_prs.speed10K.this_year }}/km{% else %}<span class="td-pr-null">—</span>{% endif %}</td>
        <td class="pr-this-year td-pr-date">{{ run_prs.speed10K.this_year_date }}</td>
        <td class="pr-this-year td-pr-workout">{{ run_prs.speed10K.this_year_workout }}</td>
        <td class="pr-all-time td-pr-value" style="display:none">{% if run_prs.speed10K.all_time %}{{ run_prs.speed10K.all_time }}/km{% else %}<span class="td-pr-null">—</span>{% endif %}</td>
        <td class="pr-all-time td-pr-date" style="display:none">{{ run_prs.speed10K.all_time_date }}</td>
        <td class="pr-all-time td-pr-workout" style="display:none">{{ run_prs.speed10K.all_time_workout }}</td>
      </tr>
      <tr>
        <td>{{ run_prs.speedHalfMarathon.label }}</td>
        <td class="pr-this-year td-pr-value">{% if run_prs.speedHalfMarathon.this_year %}{{ run_prs.speedHalfMarathon.this_year }}/km{% else %}<span class="td-pr-null">—</span>{% endif %}</td>
        <td class="pr-this-year td-pr-date">{{ run_prs.speedHalfMarathon.this_year_date }}</td>
        <td class="pr-this-year td-pr-workout">{{ run_prs.speedHalfMarathon.this_year_workout }}</td>
        <td class="pr-all-time td-pr-value" style="display:none">{% if run_prs.speedHalfMarathon.all_time %}{{ run_prs.speedHalfMarathon.all_time }}/km{% else %}<span class="td-pr-null">—</span>{% endif %}</td>
        <td class="pr-all-time td-pr-date" style="display:none">{{ run_prs.speedHalfMarathon.all_time_date }}</td>
        <td class="pr-all-time td-pr-workout" style="display:none">{{ run_prs.speedHalfMarathon.all_time_workout }}</td>
      </tr>
      <tr>
        <td>{{ run_prs.speedMarathon.label }}</td>
        <td class="pr-this-year td-pr-value">{% if run_prs.speedMarathon.this_year %}{{ run_prs.speedMarathon.this_year }}/km{% else %}<span class="td-pr-null">—</span>{% endif %}</td>
        <td class="pr-this-year td-pr-date">{{ run_prs.speedMarathon.this_year_date }}</td>
        <td class="pr-this-year td-pr-workout">{{ run_prs.speedMarathon.this_year_workout }}</td>
        <td class="pr-all-time td-pr-value" style="display:none">{% if run_prs.speedMarathon.all_time %}{{ run_prs.speedMarathon.all_time }}/km{% else %}<span class="td-pr-null">—</span>{% endif %}</td>
        <td class="pr-all-time td-pr-date" style="display:none">{{ run_prs.speedMarathon.all_time_date }}</td>
        <td class="pr-all-time td-pr-workout" style="display:none">{{ run_prs.speedMarathon.all_time_workout }}</td>
      </tr>
    </tbody>
  </table>

</div><!-- /tab-prs -->


<!-- ══ SCRIPTS ════════════════════════════════════════════════════════════════ -->
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
  const sports = ['swim', 'bike', 'run', 'strength'];

  // ── 7-day data ───────────────────────────────────────────────────────────
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

  // ── 12-month data ────────────────────────────────────────────────────────
  const monthly = [
    {% for m in td.monthly %}
    {
      month:    "{{ m.month }}",
      swim:     { tss: {{ m.swim.tss }},     hours: {{ m.swim.hours }}     },
      bike:     { tss: {{ m.bike.tss }},     hours: {{ m.bike.hours }}     },
      run:      { tss: {{ m.run.tss }},      hours: {{ m.run.hours }}      },
      strength: { tss: {{ m.strength.tss }}, hours: {{ m.strength.hours }} },
    },
    {% endfor %}
  ];

  const ctlTrend = [
    {% for c in td.ctl_trend %}
    { month: "{{ c.month }}", ctl: {{ c.ctl }}, atl: {{ c.atl }}, tsb: {{ c.tsb }} },
    {% endfor %}
  ];

  // ── Shared chart options ─────────────────────────────────────────────────
  const stackedBar = {
    responsive: true,
    plugins: { legend: { position: 'bottom' } },
    scales: {
      x: { stacked: true },
      y: { stacked: true, beginAtZero: true },
    },
  };

  function shortMonth(ym) {
    const [y, m] = ym.split('-');
    return new Date(+y, +m - 1).toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
  }

  // ── Chart 1: Daily TSS ───────────────────────────────────────────────────
  const dayLabels = daily.map(d => {
    const dt = new Date(d.date + 'T00:00:00');
    return dt.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  });

  new Chart(document.getElementById('chartDailyTSS'), {
    type: 'bar',
    data: {
      labels: dayLabels,
      datasets: sports.map(s => ({
        label: s.charAt(0).toUpperCase() + s.slice(1),
        data:  daily.map(d => d[s].tss),
        backgroundColor: COLORS[s],
      })),
    },
    options: { ...stackedBar, plugins: { ...stackedBar.plugins,
      title: { display: true, text: 'Daily TSS by Sport' },
      tooltip: {
        callbacks: {
          footer: (items) => {
            const total = items.reduce((a, i) => a + i.raw, 0);
            return `Total TSS: ${total.toFixed(0)}`;
          }
        }
      }
    }},
  });

  // ── Chart 2: Daily Hours ─────────────────────────────────────────────────
  new Chart(document.getElementById('chartDailyHours'), {
    type: 'bar',
    data: {
      labels: dayLabels,
      datasets: sports.map(s => ({
        label: s.charAt(0).toUpperCase() + s.slice(1),
        data:  daily.map(d => d[s].hours),
        backgroundColor: COLORS[s],
      })),
    },
    options: { ...stackedBar, plugins: { ...stackedBar.plugins,
      title: { display: true, text: 'Daily Hours by Sport' },
      tooltip: {
        callbacks: {
          label: (ctx) => ` ${ctx.dataset.label}: ${ctx.raw}h`,
          footer: (items) => {
            const total = items.reduce((a, i) => a + i.raw, 0);
            return `Total: ${total.toFixed(1)}h`;
          }
        }
      }
    },
      scales: { ...stackedBar.scales,
        y: { stacked: true, beginAtZero: true,
             ticks: { callback: v => v + 'h' } } },
    },
  });

  // ── Chart 3: TSS Donut ───────────────────────────────────────────────────
  new Chart(document.getElementById('chartTSSDonut'), {
    type: 'doughnut',
    data: {
      labels: sports.map(s => s.charAt(0).toUpperCase() + s.slice(1)),
      datasets: [{
        data: sports.map(s => totals[s]),
        backgroundColor: sports.map(s => COLORS[s]),
        hoverOffset: 8,
      }],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom' },
        title:  { display: true, text: 'TSS Distribution' },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const total = ctx.dataset.data.reduce((a, v) => a + v, 0);
              const pct   = total > 0 ? ((ctx.raw / total) * 100).toFixed(0) : 0;
              return ` ${ctx.label}: ${ctx.raw} TSS (${pct}%)`;
            }
          }
        }
      },
    },
  });

  // ── Chart 4: Monthly TSS ─────────────────────────────────────────────────
  const monthLabels = monthly.map(m => shortMonth(m.month));

  new Chart(document.getElementById('chartMonthlyTSS'), {
    type: 'bar',
    data: {
      labels: monthLabels,
      datasets: sports.map(s => ({
        label: s.charAt(0).toUpperCase() + s.slice(1),
        data:  monthly.map(m => m[s].tss),
        backgroundColor: COLORS[s],
      })),
    },
    options: { ...stackedBar, plugins: { ...stackedBar.plugins,
      title: { display: true, text: 'Monthly TSS by Sport (12 months)' },
      tooltip: {
        callbacks: {
          footer: (items) => `Total: ${items.reduce((a,i)=>a+i.raw,0).toFixed(0)} TSS`
        }
      }
    }},
  });

  // ── Chart 5: Monthly Hours ────────────────────────────────────────────────
  new Chart(document.getElementById('chartMonthlyHours'), {
    type: 'bar',
    data: {
      labels: monthLabels,
      datasets: sports.map(s => ({
        label: s.charAt(0).toUpperCase() + s.slice(1),
        data:  monthly.map(m => m[s].hours),
        backgroundColor: COLORS[s],
      })),
    },
    options: { ...stackedBar, plugins: { ...stackedBar.plugins,
      title: { display: true, text: 'Monthly Hours by Sport (12 months)' },
      tooltip: {
        callbacks: {
          label: (ctx) => ` ${ctx.dataset.label}: ${ctx.raw}h`,
          footer: (items) => `Total: ${items.reduce((a,i)=>a+i.raw,0).toFixed(1)}h`
        }
      }
    },
      scales: { ...stackedBar.scales,
        y: { stacked: true, beginAtZero: true, ticks: { callback: v => v + 'h' } } },
    },
  });

  // ── Chart 6: CTL / ATL Trend ──────────────────────────────────────────────
  // Sample: one point per week (every 7th day) to keep chart readable
  const ctlSampled = ctlTrend.filter((_, i) => i % 7 === 0 || i === ctlTrend.length - 1);
  new Chart(document.getElementById('chartCTL'), {
    type: 'line',
    data: {
      labels: ctlSampled.map(c => {
        const dt = new Date(c.month + '-01T00:00:00');
        return dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      }),
      datasets: [
        {
          label: 'CTL (Fitness)',
          data: ctlSampled.map(c => c.ctl),
          borderColor: '#4fc3f7',
          backgroundColor: 'rgba(79,195,247,.1)',
          tension: 0.3,
          fill: true,
          pointRadius: 0,
        },
        {
          label: 'ATL (Fatigue)',
          data: ctlSampled.map(c => c.atl),
          borderColor: '#ef9a9a',
          backgroundColor: 'rgba(239,154,154,.05)',
          tension: 0.3,
          fill: false,
          pointRadius: 0,
        },
      ],
    },
    options: {
      responsive: true,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'bottom' },
        title: { display: true, text: 'CTL & ATL — 12-Month Trend' },
        tooltip: {
          callbacks: {
            afterBody: (items) => {
              const ctl = items[0]?.raw ?? 0;
              const atl = items[1]?.raw ?? 0;
              return `TSB (Form): ${(ctl - atl).toFixed(1)}`;
            }
          }
        }
      },
      scales: {
        y: { beginAtZero: false },
      },
    },
  });

  // ── Heatmap ───────────────────────────────────────────────────────────────
  (function buildHeatmap() {
    const container = document.getElementById('heatmap-container');
    if (!container) return;

    const maxTSS = Math.max(...monthly.map(m =>
      sports.reduce((a, s) => a + m[s].tss, 0)
    ));

    let html = '<table style="border-collapse:collapse;font-size:.82em;min-width:520px;">';
    html += '<thead><tr><th style="padding:.3rem .6rem;text-align:left;">Month</th>';
    sports.forEach(s => {
      html += `<th style="padding:.3rem .6rem;color:${COLORS[s]};text-align:right;">${s.charAt(0).toUpperCase()+s.slice(1)}</th>`;
    });
    html += '<th style="padding:.3rem .6rem;text-align:right;">Total TSS</th></tr></thead><tbody>';

    monthly.forEach(m => {
      const totalTSS = sports.reduce((a, s) => a + m[s].tss, 0);
      const intensity = maxTSS > 0 ? totalTSS / maxTSS : 0;
      const bg = `rgba(79,195,247,${(intensity * 0.35).toFixed(2)})`;
      html += `<tr style="border-bottom:1px solid rgba(128,128,128,.12);background:${bg};">`;
      html += `<td style="padding:.3rem .6rem;font-weight:600;">${shortMonth(m.month)}</td>`;
      sports.forEach(s => {
        html += `<td style="padding:.3rem .6rem;text-align:right;color:${COLORS[s]};">${m[s].tss > 0 ? m[s].tss : '—'}</td>`;
      });
      html += `<td style="padding:.3rem .6rem;text-align:right;font-weight:600;">${totalTSS}</td>`;
      html += '</tr>';
    });
    html += '</tbody></table>';
    container.innerHTML = html;
  })();

})();

// ── Tab switching ─────────────────────────────────────────────────────────
function tdShowTab(name, btn) {
  document.querySelectorAll('.td-panel').forEach(p => p.style.display = 'none');
  document.querySelectorAll('.td-tab').forEach(b => b.classList.remove('td-tab-active'));
  document.getElementById('tab-' + name).style.display = 'block';
  btn.classList.add('td-tab-active');
  // Trigger chart resize so lazy-rendered charts paint correctly
  window.dispatchEvent(new Event('resize'));
}

// ── PR This Year / All-Time toggle ───────────────────────────────────────
function tdPRToggle(mode, btn) {
  document.querySelectorAll('.td-pr-toggle').forEach(b => b.classList.remove('td-pr-toggle-active'));
  btn.classList.add('td-pr-toggle-active');
  const show = mode === 'this_year' ? 'pr-this-year' : 'pr-all-time';
  const hide = mode === 'this_year' ? 'pr-all-time'  : 'pr-this-year';
  document.querySelectorAll('.' + show).forEach(el => el.style.display = '');
  document.querySelectorAll('.' + hide).forEach(el => el.style.display = 'none');
}
</script>


<!-- ══ STYLES ════════════════════════════════════════════════════════════════ -->
<style>
/* ── Stat cards ─────────────────────────────────────────────────────────── */
.td-stat-card {
  flex: 1; min-width: 120px;
  padding: 1rem 1.25rem;
  border-radius: 6px;
  text-align: center;
  background: rgba(128,128,128,0.08);
}
.td-stat-label { font-size:.78em; text-transform:uppercase; letter-spacing:.05em; opacity:.7; }
.td-stat-value { font-size:2em; font-weight:700; margin-top:.1em; }
.td-card-ctl     { border-top:3px solid #4fc3f7; }
.td-card-atl     { border-top:3px solid #ef9a9a; }
.td-card-tsb-pos { border-top:3px solid #81c784; }
.td-card-tsb-neg { border-top:3px solid #ef9a9a; }

/* ── Sport summary cards ────────────────────────────────────────────────── */
.td-sport-card { padding:.85rem 1rem; border-radius:6px; background:rgba(128,128,128,0.08); }
.td-sport-title { font-weight:600; font-size:1em; margin-bottom:.5rem; }
.td-sport-row   { display:flex; justify-content:space-between; font-size:.88em; padding:.15rem 0; }

/* ── Tab nav ────────────────────────────────────────────────────────────── */
.td-tabs {
  display: flex;
  gap: .5rem;
  flex-wrap: wrap;
  margin: 1.2rem 0 0;
  border-bottom: 2px solid rgba(128,128,128,.2);
  padding-bottom: .5rem;
}
.td-tab {
  background: none;
  border: 1px solid rgba(128,128,128,.25);
  border-radius: 4px 4px 0 0;
  color: inherit;
  cursor: pointer;
  font-size: .88em;
  font-weight: 600;
  padding: .45rem 1.1rem;
  opacity: .65;
  transition: opacity .15s, border-color .15s;
}
.td-tab:hover       { opacity: 1; }
.td-tab-active      { opacity: 1; border-bottom-color: #4fc3f7; color: #4fc3f7; border-color: rgba(128,128,128,.4); }

/* ── PR toggle buttons ──────────────────────────────────────────────────── */
.td-pr-toggle {
  background: rgba(128,128,128,.1);
  border: 1px solid rgba(128,128,128,.25);
  border-radius: 20px;
  color: inherit;
  cursor: pointer;
  font-size: .82em;
  font-weight: 600;
  padding: .3rem .9rem;
  opacity: .6;
  transition: opacity .15s, background .15s;
}
.td-pr-toggle:hover        { opacity: 1; }
.td-pr-toggle-active       { opacity: 1; background: rgba(79,195,247,.15); color: #4fc3f7; border-color: #4fc3f7; }

/* ── PR tables ──────────────────────────────────────────────────────────── */
.td-pr-table {
  width: 100%;
  border-collapse: collapse;
  font-size: .9em;
  margin-bottom: 1rem;
}
.td-pr-table th {
  text-align: left;
  padding: .4rem .6rem;
  border-bottom: 2px solid rgba(128,128,128,.3);
  font-size: .8em;
  text-transform: uppercase;
  letter-spacing: .04em;
  opacity: .7;
}
.td-pr-table td {
  padding: .4rem .6rem;
  border-bottom: 1px solid rgba(128,128,128,.12);
}
.td-pr-value   { font-weight: 700; font-size: 1.05em; }
.td-pr-date    { font-size: .82em; opacity: .65; }
.td-pr-workout { font-size: .82em; opacity: .65; font-style: italic; }
.td-pr-null    { opacity: .35; }

/* ── Session row hover ──────────────────────────────────────────────────── */
.session-row:hover { background: rgba(128,128,128,.07); }
</style>
