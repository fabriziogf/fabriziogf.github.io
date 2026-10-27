---
title: "On the Clock: Building a Fantasy Football Draft Assistant"
---

A fantasy draft looks like a ranking problem: sort the players, take the best one left. It isn't. By the third round everyone at the table has the same rankings open in a browser tab. What wins a draft is timing: knowing when a position is about to dry up, when you can afford to wait, and when the "best player available" is someone you could still get twenty picks later.

So I built a draft-day assistant around that idea. It generates my own projections, turns them into value, and, while I'm on the clock, tells me the best pick given who's gone and what my roster needs. This post explains how it works.

The whole thing is one pipeline:

```
nflverse stats + ADP → projections → valuation → FastAPI → React draft cockpit
```

Python for the model and API, React for the UI. Everything is precomputed so it works offline during the draft. [Code is on GitHub](https://github.com/fabriziogf/fantasy-football-draft).

---

## My own projections

I wanted my own projections, not a scraped consensus. The base is simple: take each player's recent seasons, score them with my league's PPR rules, and weight recent years more.

Scoring is config-driven arithmetic over the nflverse seasonal stats:

```python
SCORING = {
    "passing_yards": 0.04, "passing_tds": 4.0, "interceptions": -2.0,
    "rushing_yards": 0.1,  "rushing_tds": 6.0,
    "receptions": 1.0,     "receiving_yards": 0.1, "receiving_tds": 6.0,
    "fumbles_lost": -2.0,
}
```

The scoring isn't the interesting part. What goes wrong when you project naively is. My first version worked in points per game, then multiplied by a full season. The top of the board came back with Davis Webb and Joe Milton III as top-five quarterbacks. Each had played a game or two of garbage time, posted decent rate stats in a tiny sample, and the model happily stretched that over sixteen games.

The fix is **sample-size shrinkage**: pull every player's per-game average toward a low, position-specific prior, weighted by how many games they've actually played.

```
shrunk_ppg = (games · raw_ppg + K · prior) / (games + K)
```

A player with fifty games barely moves. A player with two gets pulled almost all the way back to the prior and drops off the top of the board, which is where a two-game backup belongs. One formula, and the projections started passing the smell test.

---

## Players with no history

Historical stats have a blind spot: anyone without history. Rookies have never taken an NFL snap. Kickers and defenses aren't in the offensive stat tables at all. They all get drafted, so they all need to be on the board.

For these, I defer to the market. [Fantasy Football Calculator](https://fantasyfootballcalculator.com) publishes a free ADP (average draft position) endpoint, which I set to my exact league: PPR, twelve teams, this season. It's real drafts, aggregated. Wiring it up was mostly the unglamorous work of reconciling two vocabularies. The ADP source calls kickers `PK` and the Rams `LAR`; nflverse says `K` and `LA`. Names need the same treatment, down to a hand-checked alias so *Kenny* Gainwell matches *Kenneth* Gainwell instead of being mistaken for a rookie.

Rookies get placed by fitting a curve from ADP to projected points within their position. A rookie running back inherits the points of the slot where the market drafts him. Kickers and defenses get a rough baseline.

That's the guiding rule: **the model leads where it has signal and defers to the market where it doesn't.** It's also where the main limitation sits. My data source only goes through 2024, so a few veterans the market has quietly moved on from still rank high on stale history. The board shows each player's ADP next to my value, so those disagreements are visible, not hidden. A projection you can't sanity-check is worse than useless.

---

## Points, value, timing

Projected points don't tell you who to draft. A quarterback outscores every running back on raw points, but that doesn't make him the pick. *Every* quarterback scores a lot, so good ones aren't actually scarce.

The standard fix is **value over replacement (VOR)**: measure a player not by his points but by how far he sits above the last starter the league will roster at his position. In a twelve-team league that starts one quarterback, "replacement" is roughly the twelfth-best quarterback. For running backs, where everyone starts two or more, it's much deeper. VOR is what lets you compare a quarterback to a running back fairly.

But VOR is static. It's the same in round one and round ten. What makes the assistant draft-aware is **value over next available (VONA)**: for each player, how much better is he than the best player at his position who'll likely still be there at my *next* pick?

That's the timing question, made concrete. If a comparable player will survive the trip back to me, there's no rush: VONA is near zero, so wait. If the position is about to fall off a cliff, VONA is large, so take him now. I estimate who survives with ADP: anyone the market drafts before my next pick is probably gone.

This also fixed two things pure VOR gets wrong. Elite quarterbacks stop looking like first-round picks once you see their VONA is near zero, because another good one will be there later. And kickers and defenses, which naive VOR drafts absurdly early, get re-anchored to what the market actually pays, so they slide to the back of the draft where they belong.

---

## The recommendation and the reason

On the clock, every available player gets a score that blends the two:

```
score = (0.5 · VOR + 0.5 · VONA) × strategy_multiplier
```

The multiplier encodes my strategy: build a core of strong running backs and receivers first, only take an elite tight end or quarterback when his value clearly beats the best skill player on the board, and leave kicker and defense for the last rounds unless one is a clear outlier.

Every recommendation explains itself, with a sentence instead of a bare number:

> **WR2 · Tier 2 · VOR 88 · cliff: next comparable at pick 22 is ~26 pts worse · builds RB/WR core**

I never wanted a black box telling me who to draft with thirty seconds on the clock. If I can't see why, I can't overrule it when I know something the model doesn't.

On top of value, the assistant shows plain, rule-based flags: a rookie whose number came from ADP rather than tape, a running back in his age-cliff years, a player who's missed a lot of time, or a bye week that clashes with someone I've already drafted. Each is a visible rule, not a mysterious risk score.

![Draft cockpit showing ranked recommendations with reason lines and the roster tracker](/assets/images/ff_draft_cockpit.png)
*On the clock: each recommendation carries its reason line, value stats (VOR, VONA, ADP), and rule-based flags — next to the live roster tracker.*

---

## The cockpit

None of this matters if it's slow to use with a pick clock running. The interface is a single React screen: a ranked list of recommendations with their reasons, a roster tracker showing which starting slots I still need, a search box to mark any pick (mine or an opponent's) in one keystroke, and a tier board that makes positional runs obvious. The snake-draft math shows how many picks until I'm up again. Draft state is saved on the server, so if the browser dies mid-draft, a refresh puts me back where I was.

![Tier board grouping every position into value tiers](/assets/images/ff_tier_board.png)
*The tier board: every position grouped into value tiers, so a run on the board is obvious at a glance.*

Under it all is the part I care about most: it's tunable and testable. Every knob (scoring, shrinkage strength, value weights, strategy) lives in one config file, and the model logic runs under a test suite with no network and no surprises. The projections will get sharper once this season's data lands. **But the machine that turns numbers into a pick on the clock is done**, and I'll be drafting with it.

*The code, and a longer tour of each phase, is [on GitHub](https://github.com/fabriziogf/fantasy-football-draft).*
