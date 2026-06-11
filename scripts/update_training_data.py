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
from datetime import date, timedelta
from pathlib import Path

# Add TrainingPeaks MCP to path
TP_MCP = Path("/Users/fabriziogiovanninifilho/ai-projects/trainingpeaks-mcp")
sys.path.insert(0, str(TP_MCP / "src"))

from tp_mcp.tools.fitness import tp_get_fitness
from tp_mcp.tools.peaks import tp_get_peaks
from tp_mcp.client import TPClient

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


# ── Pace conversion (m/s → "M:SS /km") ──────────────────────────────────────
def mps_to_pace(speed_ms) -> str | None:
    """Convert m/s to min:sec per km string, e.g. '3:49'."""
    if not speed_ms or speed_ms <= 0:
        return None
    pace_sec = 1000 / speed_ms
    mins = int(pace_sec // 60)
    secs = int(pace_sec % 60)
    return f"{mins}:{secs:02d}"


# ── YAML helpers ─────────────────────────────────────────────────────────────
def q(s):
    return f'"{str(s)}"'

def yn(v):
    """Null-safe YAML value — emits null for None."""
    if v is None:
        return "null"
    return str(v)


# 3:00/km in m/s — anything faster is a GPS artifact, excluded from run PRs
MAX_VALID_RUN_SPEED_MS = 1000 / 180

# Minimum distance (m) to count as a marathon effort (handles Garmin under-recording)
MARATHON_MIN_M = 41_500


def marathon_best_from_workouts(raw_workouts: list, year_days: int) -> tuple[dict, dict]:
    """
    Scan raw workouts for runs >= MARATHON_MIN_M and return the best avg pace,
    split into (all_time_record, this_year_record). Each record is a dict with
    keys: value (pace str), date, workout_title — or {} if none found.
    """
    RUN_TYPES = {3, 13}
    year_start = date.today() - timedelta(days=year_days)

    best_all: tuple | None = None   # (speed_ms, date_str, title)
    best_ty:  tuple | None = None

    for w in raw_workouts:
        if w.get('workoutTypeValueId') not in RUN_TYPES:
            continue
        dist_m = w.get('distance') or 0
        if dist_m < MARATHON_MIN_M:
            continue
        hrs = w.get('totalTime') or 0
        if hrs <= 0:
            continue
        speed_ms = dist_m / (hrs * 3600)
        if speed_ms > MAX_VALID_RUN_SPEED_MS:   # too fast → skip
            continue

        wdate_str = (w.get('workoutDay') or '')[:10]
        title     = w.get('title', '')

        if best_all is None or speed_ms > best_all[0]:
            best_all = (speed_ms, wdate_str, title)

        try:
            if date.fromisoformat(wdate_str) >= year_start:
                if best_ty is None or speed_ms > best_ty[0]:
                    best_ty = (speed_ms, wdate_str, title)
        except (ValueError, TypeError):
            pass

    def to_rec(tup):
        if not tup:
            return {}
        spd, dt, ttl = tup
        return {'value': mps_to_pace(spd), 'date': dt, 'workout_title': ttl}

    return to_rec(best_all), to_rec(best_ty)


def _better_run_record(a: dict, b: dict) -> dict:
    """Return whichever run record has the faster (higher speed) pace, or the non-empty one."""
    if not a:
        return b
    if not b:
        return a
    # pace strings like "3:49" — shorter minutes + shorter seconds = faster
    def pace_to_sec(p):
        try:
            m, s = p.split(':')
            return int(m) * 60 + int(s)
        except Exception:
            return 9999
    return a if pace_to_sec(a['value']) <= pace_to_sec(b['value']) else b


# ── PR fetcher ───────────────────────────────────────────────────────────────
async def fetch_prs(year_days: int, raw_workouts: list) -> dict:
    """Fetch bike and run PRs — all-time and this year.

    raw_workouts is the 12-month window used as a fallback for marathon distance
    (handles Garmin under-recording < 42.195 km but >= 41.5 km).
    """
    bike_types = ['power5sec', 'power1min', 'power5min', 'power10min', 'power20min', 'power60min']
    run_types  = ['speed1K', 'speed5K', 'speed10K', 'speedHalfMarathon', 'speedMarathon']

    prs = {'bike': {}, 'run': {}}

    for pr_type in bike_types:
        at = await tp_get_peaks(sport='Bike', pr_type=pr_type, days=3650)
        ty = await tp_get_peaks(sport='Bike', pr_type=pr_type, days=year_days)
        at_top = at.get('records', [{}])[0] if at.get('records') else {}
        ty_top = ty.get('records', [{}])[0] if ty.get('records') else {}
        prs['bike'][pr_type] = {
            'all_time':          at_top.get('value'),
            'all_time_date':     at_top.get('date', ''),
            'all_time_workout':  at_top.get('workout_title', ''),
            'this_year':         ty_top.get('value'),
            'this_year_date':    ty_top.get('date', ''),
            'this_year_workout': ty_top.get('workout_title', ''),
        }

    # Pre-compute marathon fallback from raw workouts
    mara_at_wkt, mara_ty_wkt = marathon_best_from_workouts(raw_workouts, year_days)

    for pr_type in run_types:
        at = await tp_get_peaks(sport='Run', pr_type=pr_type, days=3650)
        ty = await tp_get_peaks(sport='Run', pr_type=pr_type, days=year_days)

        # Filter out any record faster than 3:00/km (GPS artifact)
        at_records = [r for r in at.get('records', [])
                      if (r.get('value') or 0) <= MAX_VALID_RUN_SPEED_MS]
        ty_records = [r for r in ty.get('records', [])
                      if (r.get('value') or 0) <= MAX_VALID_RUN_SPEED_MS]

        at_top = at_records[0] if at_records else {}
        ty_top = ty_records[0] if ty_records else {}

        at_rec = {
            'value':          mps_to_pace(at_top.get('value')),
            'date':           at_top.get('date', ''),
            'workout_title':  at_top.get('workout_title', ''),
        } if at_top else {}

        ty_rec = {
            'value':          mps_to_pace(ty_top.get('value')),
            'date':           ty_top.get('date', ''),
            'workout_title':  ty_top.get('workout_title', ''),
        } if ty_top else {}

        # For marathon: also consider workout scan (handles Garmin-short recordings)
        if pr_type == 'speedMarathon':
            at_rec = _better_run_record(at_rec, mara_at_wkt)
            ty_rec = _better_run_record(ty_rec, mara_ty_wkt)

        prs['run'][pr_type] = {
            'all_time':          at_rec.get('value'),
            'all_time_date':     at_rec.get('date', ''),
            'all_time_workout':  at_rec.get('workout_title', ''),
            'this_year':         ty_rec.get('value'),
            'this_year_date':    ty_rec.get('date', ''),
            'this_year_workout': ty_rec.get('workout_title', ''),
        }

    return prs


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
            f"    power_avg: {yn(w['power_avg'])}"
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

    # ── Fetch PRs ─────────────────────────────────────────────────────────────
    print("Fetching PRs…")
    prs = await fetch_prs(year_days, raw_12mo)

    # ── Build 7-day totals + daily breakdown ──────────────────────────────────
    sports = ['swim', 'bike', 'run', 'strength', 'other']
    totals = {s: {'sessions': 0, 'hours': 0.0, 'distance_km': 0.0, 'tss': 0.0}
              for s in sports}
    days = {}
    for i in range(7):
        d = (start + timedelta(days=i)).isoformat()
        days[d] = {s: {'hours': 0.0, 'distance_km': 0.0, 'tss': 0.0, 'sessions': 0}
                   for s in sports}

    workout_list = []
    for w in raw_7day:
        sport = classify(w.get('workoutTypeValueId'))
        wdate = (w.get('workoutDay') or '')[:10]
        tss   = round(w.get('tssActual') or 0, 1)
        hrs   = round(w.get('totalTime') or 0, 2)
        dist  = round((w.get('distance') or 0) / 1000, 1)
        hr    = w.get('heartRateAverage')
        pwr   = w.get('powerAverage')

        totals[sport]['sessions']    += 1
        totals[sport]['hours']       += hrs
        totals[sport]['distance_km'] += dist
        totals[sport]['tss']         += tss

        if wdate in days:
            days[wdate][sport]['hours']    += hrs
            days[wdate][sport]['distance_km'] += dist
            days[wdate][sport]['tss']      += tss
            days[wdate][sport]['sessions'] += 1

        workout_list.append({
            'date': wdate, 'title': w.get('title', ''), 'sport': sport,
            'hours': hrs, 'distance_km': dist, 'tss': tss,
            'hr_avg': int(hr) if hr else None,
            'power_avg': int(pwr) if pwr else None,
        })

    for s in totals:
        totals[s]['hours']       = round(totals[s]['hours'], 1)
        totals[s]['distance_km'] = round(totals[s]['distance_km'], 1)
        totals[s]['tss']         = int(round(totals[s]['tss'], 0))

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

    # ── Build monthly aggregates ──────────────────────────────────────────────
    monthly_map = defaultdict(lambda: {
        s: {'sessions': 0, 'hours': 0.0, 'distance_km': 0.0, 'tss': 0.0}
        for s in sports
    })
    for w in raw_12mo:
        sport = classify(w.get('workoutTypeValueId'))
        month = (w.get('workoutDay') or '')[:7]
        if not month:
            continue
        monthly_map[month][sport]['sessions']    += 1
        monthly_map[month][sport]['hours']       += round(w.get('totalTime') or 0, 2)
        monthly_map[month][sport]['distance_km'] += round((w.get('distance') or 0) / 1000, 1)
        monthly_map[month][sport]['tss']         += round(w.get('tssActual') or 0, 1)

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
    os.chdir(REPO)
    os.system('git add _data/training_data.yml _data/swim_prs.yml')
    os.system(f'git commit -m "chore: update training dashboard [{today}]"')
    os.system('git push origin main')
    print("Pushed.")


if __name__ == "__main__":
    asyncio.run(main())
