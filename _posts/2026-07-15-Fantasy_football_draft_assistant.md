---
title: "On the Clock: Building a Fantasy Football Draft Assistant"
---

A fantasy draft looks like a ranking problem: sort the players, take the best one left. It isn't. By the third round everyone at the table has the same rankings open in a browser tab. What actually wins a draft is timing — knowing when a position is about to dry up, when you can afford to wait, and when the "best player available" is someone you could still get twenty picks later.

So I built a draft-day assistant around that idea. It generates my own projections, turns them into value, and — while I'm on the clock — tells me the best pick right now, given who's already gone and what my roster needs. This post is about how it works.

The whole thing is one pipeline:

```
nflverse stats + ADP → projections → valuation → FastAPI → React draft cockpit
```

Python for the model and API, React for the UI. Everything is precomputed so it works offline during the draft. [Code is on GitHub](https://github.com/fabriziogf/fantasy-football-draft).

---

## Building my own projections

I wanted my own projections, not a scraped consensus. The base is simple: take each player's recent seasons, score them under my league's PPR rules, and weight recent years more heavily.

Scoring is just config-driven arithmetic over the nflverse seasonal stats:

```python
SCORING = {
    "passing_yards": 0.04, "passing_tds": 4.0, "interceptions": -2.0,
    "rushing_yards": 0.1,  "rushing_tds": 6.0,
    "receptions": 1.0,     "receiving_yards": 0.1, "receiving_tds": 6.0,
    "fumbles_lost": -2.0,
}
```

The interesting part isn't the scoring. It's what goes wrong when you project it naively. My first version worked in points per game, then multiplied by a full season. The top of the board came back with Davis Webb and Joe Milton III as top-five quarterbacks. Each had played a game or two of garbage time, put up decent rate stats in a tiny sample, and the model happily stretched that across sixteen games.

The fix is **sample-size shrinkage**: pull every player's per-game average toward a low, position-specific prior, weighted by how many games they've actually played.

```
shrunk_ppg = (games · raw_ppg + K · prior) / (games + K)
```

A player with fifty games barely moves. A player with two gets pulled almost all the way back to the prior and drops off the top of the board, which is where a two-game backup belongs. One formula, and the projections started passing the smell test.

---

## The players with no history

Historical stats have a blind spot: anyone without history. Rookies have never taken an NFL snap. Kickers and defenses aren't in the offensive stat tables at all. They all get drafted, so they all have to be on the board.

For these, I defer to the market. The [Fantasy Football Calculator](https://fantasyfootballcalculator.com) publishes a free ADP (average draft position) endpoint, set to my exact league — PPR, twelve teams, this season. It's real drafts, aggregated. Wiring it up was mostly the unglamorous work of reconciling two vocabularies: the ADP source calls kickers `PK` and the Rams `LAR`; nflverse says `K` and `LA`. Names need the same treatment, down to a hand-checked alias so *Kenny* Gainwell matches *Kenneth* Gainwell instead of getting mistaken for a rookie.

Rookies get placed by fitting a curve from ADP to projected points within their position. A rookie running back inherits the points of the slot where the market drafts him. Kickers and defenses get a rough baseline.

That's the guiding principle: **the model leads where it has signal, and defers to the market where it doesn't.** It's also where the honest limitation lives. The data source I use publishes through 2024, so a few veterans the market has quietly moved on from still rank high on stale history. The board shows each player's ADP right next to my value, so those disagreements are visible instead of hidden. A projection you can't sanity-check is worse than useless.

---

## From points to value to timing

Projected points don't tell you who to draft. A quarterback outscores every running back on raw points, but that doesn't make him the pick. *Every* quarterback scores a lot, so the good ones aren't actually scarce.

The standard fix is **value over replacement (VOR)**: measure a player not by his points but by how far he sits above the last starter the league will roster at his position. In a twelve-team league that starts one quarterback, "replacement" is roughly the twelfth-best quarterback. For running backs, where everyone starts two or more, it's much deeper. VOR is what lets you compare a quarterback to a running back honestly.

But VOR is static. It's the same in round one and round ten. The piece that makes the assistant draft-aware is **value over next available (VONA)**: for each player, how much better is he than the best guy at his position who'll likely still be there at my *next* pick?

That's the timing question, made concrete. If a comparable player will survive the round trip back to me, there's no urgency — VONA is near zero, so wait. If the position is about to fall off a cliff, VONA is large, so take him now. I estimate who survives using ADP: anyone the market drafts before my next pick is probably gone.

This also fixed two things pure VOR gets wrong. Elite quarterbacks stop looking like first-round picks once you see their VONA is near zero, because another good one will be there later. And kickers and defenses, which naive VOR drafts absurdly early, get re-anchored to what the market actually pays, so they slide to the back of the draft where they belong.

---

## The recommendation, and the why

On the clock, every available player gets a score that blends the two:

```
score = (0.5 · VOR + 0.5 · VONA) × strategy_multiplier
```

The multiplier encodes my actual strategy: build a core of strong running backs and receivers first, only reach for an elite tight end or quarterback when his value genuinely beats the best skill player on the board, and leave kicker and defense for the final rounds unless one is a clear outlier.

Every recommendation explains itself. Not a bare number — a sentence:

> **WR2 · Tier 2 · VOR 88 · cliff: next comparable at pick 22 is ~26 pts worse · builds RB/WR core**

I never wanted a black box telling me to draft someone with thirty seconds on the clock. If I can't see why, I can't overrule it when I know something the model doesn't.

On top of value, the assistant surfaces plain, rule-based flags: a rookie whose number came from ADP rather than tape, a running back into his age-cliff years, a player who's missed a lot of time, or a bye week that collides with someone I've already drafted. Each is a transparent rule, not a mysterious risk score.

---

## The cockpit

None of this matters if it's slow to use with a pick clock ticking. The interface is a single React screen: a ranked list of recommendations with their reasons, a roster tracker showing which starting slots I still need, a search box to mark any pick — mine or an opponent's — in one keystroke, and a tier board that makes positional runs visible at a glance. The snake-draft math tells me how many picks until I'm up again. Draft state is saved server-side, so if the browser dies mid-draft, a refresh puts me right back where I was.

Under it all is the part I care about most: it's tunable and testable. Every knob — scoring, the shrinkage strength, the value weights, the strategy — lives in one config file, and the model logic runs under a test suite with no network and no surprises. The projections will only get sharper once this season's data lands. But the machine that turns numbers into a pick on the clock is done, and I'll be drafting with it.

*The code, and a longer tour of each phase, is [on GitHub](https://github.com/fabriziogf/fantasy-football-draft).*
