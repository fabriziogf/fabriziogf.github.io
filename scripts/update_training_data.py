#!/usr/bin/env python3
"""
Update _data/training_data.yml with rolling 7-day window, 12-month trends,
CTL trend, personal records (bike + run), and enhanced workout fields.

Run daily via Cowork:
  cd /Users/fabriziogiovanninifilho/Documents/fabriziogf_page
  /Users/fabriziogiovanninifilho/ai-projects/trainingpeaks-mcp/.venv/bin/python3 scripts/update_training_data.py
"""

import asyncio
import sys
import os
from collections import defaultdict
from datetime import date, timedelta, datetime as _dt, time as _time
from pathlib import Path

# Add TrainingPeaks MCP to path (fitness + TSS + bike PRs)
TP_MCP = Path("/Users/fabriziogiovanninifilho/ai-projects/trainingpeaks-mcp")
sys.path.insert(0, str(TP_MCP / "src"))

from tp_mcp.tools.fitness import tp_get_fitness
from tp_mcp.tools.peaks import tp_get_peaks
from tp_mcp.client import TPClient

# Add this scripts/ dir to path (Strava client + run PRs)
sys.path.insert(0, str(Path(__file__).parent))
from strava_client import StravaClient, classify as strava_classify
from strava_prs import load_cache, save_cache, process_run, build_run_prs


def _epoch(d: date) -> int:
    """Local-midnight epoch seconds for a date (Strava after/before filter)."""
    return int(_dt.combine(d, _time.min).timestamp())


def match_tp_tss(tp_sessions: list, wdate: str, sport: str, moving_s: float) -> float:
    """Attach a TrainingPeaks TSS to a Strava activity by date+sport, nearest
    duration. Each TP session is consumed once so two activities don't share one."""
    best, best_diff = None, None
    for s in tp_sessions:
        if s["used"] or s["date"] != wdate or s["sport"] != sport:
            continue
        diff = abs(s["dur_s"] - moving_s)
        if best_diff is None or diff < best_diff:
            best, best_diff = s, diff
    if best is not None:
        best["used"] = True
        return round(best["tss"], 1)
    return 0.0

REPO     = Path(__file__).parent.parent
OUT      = REPO / "_data" / "training_data.yml"
SWIM_PRS = REPO / "_data" / "swim_prs.yml"

# ── Sport classifier ─────────────────────────────────────────────────────────
TYPE_ID_TO_SPORT: dict[int, str] = {
    1:   'swim',
    2:   'bike',
    3:   'run',
    4:   'bike',
    5:   'other',
    6:   'other',
    7:   'other',
    8:   'bike',
    9:   'strength',
    10:  'other',
    11:  'other',
    12:  'other',
    13:  'run',
    100: 'other',
}

def classify(type_id) -> str:
    return TYPE_ID_TO_SPORT.get(type_id, 'other')


# ── YAML helpers ─────────────────────────────────────────────────────────────
def q(s):
    return f'"{str(s)}"'

def yn(v):
    """Null-safe YAML value — emits null for None."""
    if v is None:
        return "null"
    return str(v)


# ── Bike PR fetcher (TrainingPeaks — Strava has no power-curve API) ───────────
async def fetch_bike_prs(year_days: int) -> dict:
    """Fetch bike peak-power PRs — all-time and this year — from TrainingPeaks.
    Run PRs come from Strava best-efforts (see strava_prs.py)."""
    bike_types = ['power5sec', 'power1min', 'power5min', 'power10min', 'power20min', 'power60min']
    bike: dict = {}
    for pr_type in bike_types:
        at = await tp_get_peaks(sport='Bike', pr_type=pr_type, days=3650)
        ty = await tp_get_peaks(sport='Bike', pr_type=pr_type, days=year_days)
        at_top = at.get('records', [{}])[0] if at.get('records') else {}
        ty_top = ty.get('records', [{}])[0] if ty.get('records') else {}
        bike[pr_type] = {
            'all_time':          at_top.get('value'),
            'all_time_date':     at_top.get('date', ''),
            'all_time_workout':  at_top.get('workout_title', ''),
            'this_year':         ty_top.get('value'),
            'this_year_date':    ty_top.get('date', ''),
            'this_year_workout': ty_top.get('workout_title', ''),
        }
    return bike


# 3:00/km in m/s — anything faster is a GPS artifact, excluded from run PRs
MAX_VALID_RUN_SPEED_MS = 1000 / 180


def _mps_to_pace(speed_ms) -> str | None:
    """m/s → 'M:SS' per km, or None."""
    if not speed_ms or speed_ms <= 0:
        return None
    sec = 1000 / speed_ms
    return f"{int(sec // 60)}:{int(sec % 60):02d}"


async def fetch_run_prs_tp(year_days: int) -> dict:
    """Run pace PRs from TrainingPeaks — used as the full-history baseline that
    Strava best-efforts are merged on top of (see merge_run_prs)."""
    run_types = ['speed1K', 'speed5K', 'speed10K', 'speedHalfMarathon', 'speedMarathon']
    run: dict = {}
    for pr_type in run_types:
        at = await tp_get_peaks(sport='Run', pr_type=pr_type, days=3650)
        ty = await tp_get_peaks(sport='Run', pr_type=pr_type, days=year_days)
        at_recs = [r for r in at.get('records', []) if (r.get('value') or 0) <= MAX_VALID_RUN_SPEED_MS]
        ty_recs = [r for r in ty.get('records', []) if (r.get('value') or 0) <= MAX_VALID_RUN_SPEED_MS]
        at_top = at_recs[0] if at_recs else {}
        ty_top = ty_recs[0] if ty_recs else {}
        run[pr_type] = {
            'all_time':          _mps_to_pace(at_top.get('value')),
            'all_time_date':     at_top.get('date', ''),
            'all_time_workout':  at_top.get('workout_title', ''),
            'this_year':         _mps_to_pace(ty_top.get('value')),
            'this_year_date':    ty_top.get('date', ''),
            'this_year_workout': ty_top.get('workout_title', ''),
        }
    return run


def _pace_sec(p) -> float:
    """'M:SS' → seconds, inf if missing/unparseable (so it never wins a min())."""
    try:
        m, s = str(p).split(':')
        return int(m) * 60 + int(s)
    except (ValueError, AttributeError):
        return float('inf')


def merge_run_prs(strava_run: dict, tp_run: dict) -> dict:
    """Per distance, keep whichever source has the faster pace for all_time and
    this_year independently. Strava wins ties (preferred source going forward)."""
    out: dict = {}
    for key in set(strava_run) | set(tp_run):
        sv = strava_run.get(key, {})
        tv = tp_run.get(key, {})
        merged = {}
        for span in ('all_time', 'this_year'):
            s_pace, t_pace = sv.get(span), tv.get(span)
            use_strava = s_pace is not None and _pace_sec(s_pace) <= _pace_sec(t_pace)
            src = sv if use_strava else tv
            merged[span]               = src.get(span)
            merged[f'{span}_date']     = src.get(f'{span}_date', '')
            merged[f'{span}_workout']  = src.get(f'{span}_workout', '')
        out[key] = merged
    return out


# ── YAML builder ─────────────────────────────────────────────────────────────
def build_yaml(data: dict) -> str:
    td    = data
    lines = [
        "# Auto-generated by scripts/update_training_data.py",
        "# Do not edit manually — overwritten daily by the Cowork job.",
        "",
        f"generated_at: {q(td['generated_at'])}",
        f"window_start: {q(td['window_start'])}",
        f"window_end:   {q(td['window_end'])}",
        "",
        "fitness:",
        f"  ctl:  {td['fitness']['ctl']}",
        f"  atl:  {td['fitness']['atl']}",
        f"  tsb:  {td['fitness']['tsb']}",
        "",
        "totals:",
    ]
    sports = ['swim', 'bike', 'run', 'strength', 'other']
    for s in sports:
        t = td['totals'][s]
        lines += [
            f"  {s}:",
            f"    sessions:    {t['sessions']}",
            f"    hours:       {t['hours']}",
            f"    distance_km: {t['distance_km']}",
            f"    tss:         {t['tss']}",
        ]

    # ── Daily (7-day window) ──────────────────────────────────────────────────
    lines += ["", "daily:"]
    for d in td['daily']:
        lines.append(f"  - date: {q(d['date'])}")
        for s in sports:
            v = d[s]
            lines.append(
                f"    {s:<8}: "
                f"{{ hours: {v['hours']:<5}, distance_km: {v['distance_km']:<6}, "
                f"tss: {v['tss']:<6}, sessions: {v['sessions']} }}"
            )

    # ── Workouts (with hr_avg + power_avg) ───────────────────────────────────
    lines += ["", "workouts:"]
    for w in td['workouts']:
        lines.append(
            f"  - date: {q(w['date'])}\n"
            f"    sport: {w['sport']}\n"
            f"    title: {q(w['title'])}\n"
            f"    hours: {w['hours']}\n"
            f"    distance_km: {w['distance_km']}\n"
            f"    tss: {w['tss']}\n"
            f"    hr_avg: {yn(w['hr_avg'])}\n"
            f"    power_avg: {yn(w['power_avg'])}\n"
            f"    strava_id: {yn(w.get('strava_id'))}"
        )

    # ── Monthly trends (12 months) ────────────────────────────────────────────
    lines += ["", "monthly:"]
    for m in td['monthly']:
        lines.append(f"  - month: {q(m['month'])}")
        for s in sports:
            v = m[s]
            lines.append(
                f"    {s:<8}: "
                f"{{ sessions: {v['sessions']}, hours: {v['hours']:<6}, "
                f"distance_km: {v['distance_km']:<7}, tss: {v['tss']} }}"
            )

    # ── CTL trend (end-of-month snapshots) ───────────────────────────────────
    lines += ["", "ctl_trend:"]
    for c in td['ctl_trend']:
        lines.append(f"  - {{ month: {q(c['month'])}, ctl: {c['ctl']}, atl: {c['atl']}, tsb: {c['tsb']} }}")

    # ── Personal Records — Bike ───────────────────────────────────────────────
    lines += ["", "prs:", "  bike:"]
    bike_labels = {
        'power5sec':   '5 sec',
        'power1min':   '1 min',
        'power5min':   '5 min',
        'power10min':  '10 min',
        'power20min':  '20 min',
        'power60min':  '60 min',
    }
    for k, label in bike_labels.items():
        pr = td['prs']['bike'].get(k, {})
        lines.append(f"    {k}:")
        lines.append(f"      label:            {q(label)}")
        lines.append(f"      unit:             {q('W')}")
        lines.append(f"      all_time:         {yn(pr.get('all_time'))}")
        lines.append(f"      all_time_date:    {q(pr.get('all_time_date',''))}")
        lines.append(f"      all_time_workout: {q(pr.get('all_time_workout',''))}")
        lines.append(f"      this_year:        {yn(pr.get('this_year'))}")
        lines.append(f"      this_year_date:   {q(pr.get('this_year_date',''))}")
        lines.append(f"      this_year_workout: {q(pr.get('this_year_workout',''))}")

    # ── Personal Records — Run ────────────────────────────────────────────────
    lines += ["  run:"]
    run_labels = {
        'speed1K':           '1 km',
        'speed5K':           '5 km',
        'speed10K':          '10 km',
        'speedHalfMarathon': 'Half Marathon',
        'speedMarathon':     'Marathon',
    }
    for k, label in run_labels.items():
        pr = td['prs']['run'].get(k, {})
        lines.append(f"    {k}:")
        lines.append(f"      label:            {q(label)}")
        lines.append(f"      unit:             {q('min/km')}")
        lines.append(f"      all_time:         {q(pr['all_time']) if pr.get('all_time') else 'null'}")
        lines.append(f"      all_time_date:    {q(pr.get('all_time_date',''))}")
        lines.append(f"      all_time_workout: {q(pr.get('all_time_workout',''))}")
        lines.append(f"      this_year:        {q(pr['this_year']) if pr.get('this_year') else 'null'}")
        lines.append(f"      this_year_date:   {q(pr.get('this_year_date',''))}")
        lines.append(f"      this_year_workout: {q(pr.get('this_year_workout',''))}")

    lines.append("")
    return "\n".join(lines)


# ── Swim PRs bootstrap (manual — TP API does not expose swim PRs) ─────────────
SWIM_PRS_TEMPLATE = """\
# Swim Personal Records — update manually (TrainingPeaks API does not expose swim PRs).
# pace format: "M:SS" per 100m (e.g. "1:25" = 1 min 25 sec per 100m)
pace50m:
  label: "50 m"
  unit: "min/100m"
  all_time: null
  all_time_date: ""
  this_year: null
  this_year_date: ""

pace100m:
  label: "100 m"
  unit: "min/100m"
  all_time: null
  all_time_date: ""
  this_year: null
  this_year_date: ""

pace200m:
  label: "200 m"
  unit: "min/100m"
  all_time: null
  all_time_date: ""
  this_year: null
  this_year_date: ""

pace400m:
  label: "400 m"
  unit: "min/100m"
  all_time: null
  all_time_date: ""
  this_year: null
  this_year_date: ""

pace1500m:
  label: "1500 m"
  unit: "min/100m"
  all_time: null
  all_time_date: ""
  this_year: null
  this_year_date: ""
"""


# ── Main ─────────────────────────────────────────────────────────────────────
async def main():
    today     = date.today()
    end       = today - timedelta(days=1)
    start     = end - timedelta(days=6)
    trend_start = today - timedelta(days=365)
    year_days   = (today - date(today.year, 1, 1)).days

    print(f"7-day window: {start} → {end}")
    print(f"12-month window: {trend_start} → {end}")

    # ── Fetch workouts ────────────────────────────────────────────────────────
    async with TPClient() as client:
        athlete_id = await client.ensure_athlete_id()

        # 7-day window
        resp7 = await client.get(
            f"/fitness/v6/athletes/{athlete_id}/workouts/{start}/{end}"
        )
        raw_7day = [
            w for w in (resp7.data or [])
            if w.get('totalTime') or w.get('tssActual')
        ]

        # 12-month window for trends
        resp12 = await client.get(
            f"/fitness/v6/athletes/{athlete_id}/workouts/{trend_start}/{end}"
        )
        raw_12mo = [
            w for w in (resp12.data or [])
            if w.get('totalTime') or w.get('tssActual')
        ]

    # ── Fetch fitness (CTL/ATL/TSB) ───────────────────────────────────────────
    fitness_res   = await tp_get_fitness(
        start_date=start.isoformat(), end_date=end.isoformat()
    )
    daily_fitness = {d['date']: d for d in fitness_res.get('daily_data', [])}

    trend_fitness = await tp_get_fitness(
        start_date=trend_start.isoformat(), end_date=end.isoformat()
    )
    trend_daily = trend_fitness.get('daily_data', [])

    sports = ['swim', 'bike', 'run', 'strength', 'other']

    # ── TrainingPeaks TSS aggregations (load stays on TP) ─────────────────────
    tp_tss_total = defaultdict(float)            # sport            -> tss (7-day)
    tp_tss_daily = defaultdict(float)            # (date, sport)    -> tss (7-day)
    tp_tss_month = defaultdict(float)            # (month, sport)   -> tss (12-mo)
    tp_sessions  = []                            # 7-day window, for per-row matching
    win_lo, win_hi = start.isoformat(), end.isoformat()
    for w in raw_7day:
        sport = classify(w.get('workoutTypeValueId'))
        wdate = (w.get('workoutDay') or '')[:10]
        tss   = round(w.get('tssActual') or 0, 1)
        tp_tss_total[sport]         += tss
        tp_tss_daily[(wdate, sport)] += tss
        tp_sessions.append({'date': wdate, 'sport': sport, 'tss': tss,
                            'dur_s': (w.get('totalTime') or 0) * 3600, 'used': False})
    for w in raw_12mo:
        sport = classify(w.get('workoutTypeValueId'))
        month = (w.get('workoutDay') or '')[:7]
        if month:
            tp_tss_month[(month, sport)] += round(w.get('tssActual') or 0, 1)

    # ── PRs: bike + run baseline from TP (Strava overlaid on run below) ───────
    print("Fetching PRs from TrainingPeaks…")
    bike_prs   = await fetch_bike_prs(year_days)
    tp_run_prs = await fetch_run_prs_tp(year_days)

    # ── Strava activities ─────────────────────────────────────────────────────
    print("Fetching activities from Strava…")
    sclient   = StravaClient()
    before    = _epoch(end + timedelta(days=1))
    strava_7day = sclient.activities(after=_epoch(start),       before=before)
    strava_12mo = sclient.activities(after=_epoch(trend_start), before=before)

    pr_cache = load_cache()
    new_runs = 0

    # ── Build 7-day totals + daily breakdown + workout feed (Strava) ──────────
    totals = {s: {'sessions': 0, 'hours': 0.0, 'distance_km': 0.0, 'tss': 0.0}
              for s in sports}
    days = {}
    for i in range(7):
        d = (start + timedelta(days=i)).isoformat()
        days[d] = {s: {'hours': 0.0, 'distance_km': 0.0, 'tss': 0.0, 'sessions': 0}
                   for s in sports}

    workout_list = []
    for a in sorted(strava_7day, key=lambda x: x.get('start_date_local', '')):
        sport   = strava_classify(a)
        wdate   = (a.get('start_date_local') or '')[:10]
        moving  = a.get('moving_time') or 0
        hrs     = round(moving / 3600, 2)
        dist    = round((a.get('distance') or 0) / 1000, 1)
        hr      = a.get('average_heartrate')
        pwr     = a.get('average_watts')
        tss     = match_tp_tss(tp_sessions, wdate, sport, moving)

        totals[sport]['sessions']    += 1
        totals[sport]['hours']       += hrs
        totals[sport]['distance_km'] += dist

        if wdate in days:
            days[wdate][sport]['hours']       += hrs
            days[wdate][sport]['distance_km'] += dist
            days[wdate][sport]['sessions']    += 1

        workout_list.append({
            'date': wdate, 'title': a.get('name', ''), 'sport': sport,
            'hours': hrs, 'distance_km': dist, 'tss': tss,
            'hr_avg': int(hr) if hr else None,
            'power_avg': int(pwr) if pwr else None,
            'strava_id': a.get('id'),
        })

        # Fold new runs into the PR cache (best_efforts live on the detail object)
        if sport == 'run' and a.get('id') not in pr_cache['processed_ids']:
            try:
                if process_run(sclient.activity_detail(a['id']), pr_cache):
                    new_runs += 1
            except Exception as e:  # noqa: BLE001
                print(f"  PR detail fetch failed for {a.get('id')}: {e}")

    # TSS (load) for totals + daily comes from TrainingPeaks
    for s in sports:
        totals[s]['tss'] = tp_tss_total.get(s, 0.0)
    for d in days:
        for s in sports:
            days[d][s]['tss'] = tp_tss_daily.get((d, s), 0.0)

    for s in totals:
        totals[s]['hours']       = round(totals[s]['hours'], 1)
        totals[s]['distance_km'] = round(totals[s]['distance_km'], 1)
        totals[s]['tss']         = int(round(totals[s]['tss'], 0))

    # ── Run PRs (Strava best-efforts cache) ───────────────────────────────────
    if new_runs:
        print(f"  folded {new_runs} new run(s) into PR cache")
    save_cache(pr_cache)
    strava_run_prs = build_run_prs(pr_cache, str(today.year))
    prs = {'bike': bike_prs, 'run': merge_run_prs(strava_run_prs, tp_run_prs)}

    # ── Last fitness values ───────────────────────────────────────────────────
    last_fitness = {'ctl': 0.0, 'atl': 0.0, 'tsb': 0.0}
    if daily_fitness:
        last = sorted(daily_fitness.keys())[-1]
        fd = daily_fitness[last]
        last_fitness = {
            'ctl': fd.get('ctl', 0.0),
            'atl': fd.get('atl', 0.0),
            'tsb': fd.get('tsb', 0.0),
        }

    daily_list = []
    for d in sorted(days.keys()):
        entry = {'date': d}
        for s in sports:
            entry[s] = {k: round(v, 1) for k, v in days[d][s].items()}
        daily_list.append(entry)

    # ── Build monthly aggregates (volume from Strava, TSS from TP) ────────────
    monthly_map = defaultdict(lambda: {
        s: {'sessions': 0, 'hours': 0.0, 'distance_km': 0.0, 'tss': 0.0}
        for s in sports
    })
    for a in strava_12mo:
        sport = strava_classify(a)
        month = (a.get('start_date_local') or '')[:7]
        if not month:
            continue
        monthly_map[month][sport]['sessions']    += 1
        monthly_map[month][sport]['hours']       += (a.get('moving_time') or 0) / 3600
        monthly_map[month][sport]['distance_km'] += (a.get('distance') or 0) / 1000
    for (month, sport), tss in tp_tss_month.items():
        monthly_map[month][sport]['tss'] += tss

    monthly_list = []
    for month in sorted(monthly_map.keys()):
        entry = {'month': month}
        for s in sports:
            v = monthly_map[month][s]
            entry[s] = {
                'sessions':    v['sessions'],
                'hours':       round(v['hours'], 1),
                'distance_km': round(v['distance_km'], 1),
                'tss':         int(round(v['tss'], 0)),
            }
        monthly_list.append(entry)

    # ── CTL trend: last entry per month ──────────────────────────────────────
    ctl_by_month = {}
    for d in trend_daily:
        m = d['date'][:7]
        ctl_by_month[m] = {'ctl': d['ctl'], 'atl': d['atl'], 'tsb': d['tsb']}
    ctl_trend = [
        {'month': m, **v} for m, v in sorted(ctl_by_month.items())
    ]

    # ── Assemble ─────────────────────────────────────────────────────────────
    data = {
        'generated_at': today.isoformat(),
        'window_start': start.isoformat(),
        'window_end':   end.isoformat(),
        'fitness':      last_fitness,
        'totals':       totals,
        'daily':        daily_list,
        'workouts':     workout_list,
        'monthly':      monthly_list,
        'ctl_trend':    ctl_trend,
        'prs':          prs,
    }

    OUT.write_text(build_yaml(data), encoding='utf-8')
    print(f"Written → {OUT}")

    # Bootstrap swim_prs.yml if missing
    if not SWIM_PRS.exists():
        SWIM_PRS.write_text(SWIM_PRS_TEMPLATE, encoding='utf-8')
        print(f"Created swim PRs template → {SWIM_PRS}")

    # ── Commit and push ───────────────────────────────────────────────────────
    if os.environ.get('DASHBOARD_DRY_RUN'):
        print("DRY_RUN set — skipping git commit/push.")
        return
    os.chdir(REPO)
    os.system('git add _data/training_data.yml _data/swim_prs.yml')
    os.system(f'git commit -m "chore: update training dashboard [{today}]"')
    os.system('git push origin main')
    print("Pushed.")


if __name__ == "__main__":
    asyncio.run(main())
