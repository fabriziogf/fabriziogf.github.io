---
title: "Building a World Cup Prediction Model — Part 6: The Prediction"
---

Five parts in, the pipeline is complete and — after the [Part 5](/2026/06/10/World_Cup_prediction_model_part5/) performance fix — actually runnable. Time to point it at a real tournament and see what it predicts.

The setup:

- **Model**: Dixon-Coles, fitted on all ~11,900 international matches since 2014 with exponential time decay so recent form counts more
- **Bracket**: a 32-team, 8-group tournament
- **Simulation**: 100,000 Monte Carlo runs of the full bracket — group stage, Round of 16, quarter-finals, semi-finals, final

```bash
python notebooks/predict_winner.py
```

---

## Group stage: who advances?

Each group plays a round-robin; the top two advance to the Round of 16. The `p_r16` column is each team's probability of surviving its group. Within every group these sum to ~200% (two qualifiers per group).

| Group | Favourite (advance %) | Runner-up (advance %) | Eliminated |
|-------|----------------------|----------------------|------------|
| **A** | Ecuador (69%) | Netherlands (65%) | Senegal (59%), Qatar (7%) |
| **B** | Iran (70%) | England (65%) | USA (43%), Wales (22%) |
| **C** | Argentina (77%) | Mexico (71%) | Saudi Arabia (27%), Poland (25%) |
| **D** | France (65%) | Denmark (58%) | Australia (47%), Tunisia (30%) |
| **E** | Japan (73%) | Spain (67%) | Germany (51%), Costa Rica (9%) |
| **F** | Switzerland (75%) | Morocco (65%) | Belgium (57%), Croatia (36%) |
| **G** | Brazil (78%) | Switzerland (75%) | Cameroon (38%), Serbia (9%) |
| **H** | Portugal (76%) | Uruguay (50%) | South Korea (48%), Ghana (27%) |

A few things jump out:

**Group E is brutal.** Germany — a four-time world champion — is the model's pick to exit in the group stage at 51%, behind both Japan and Spain. That's the model's confederation bias showing through (more on that below).

**Group A has no dominant side.** Three teams between 59% and 69%. Qatar is essentially eliminated on arrival at 7%.

**Argentina (77%) and Brazil (78%)** are the most secure group-stage qualifiers in the field.

---

## The knockout rounds

As teams progress, the probabilities concentrate. Here are the top contenders at each stage.

### Quarter-finals

| Team | % |
|------|---|
| Brazil | 51% |
| Argentina | 49% |
| Switzerland | 47% |
| Japan | 46% |
| Portugal | 44% |
| Ecuador | 43% |

### Semi-finals

| Team | % |
|------|---|
| Brazil | 30% |
| Argentina | 29% |
| Japan | 28% |
| Switzerland | 26% |
| Portugal | 26% |

### Final

| Team | % |
|------|---|
| Japan | 18% |
| Argentina | 18% |
| Brazil | 14% |
| Ecuador | 13% |
| Portugal | 12% |
| Spain | 12% |

### Winning it all

| Rank | Team | Win % |
|------|------|-------|
| 1 | **Japan** | **11.6%** |
| 2 | Argentina | 9.2% |
| 3 | Brazil | 7.5% |
| 4 | Spain | 7.0% |
| 5 | Morocco | 6.9% |
| 6 | Portugal | 6.7% |
| 7 | Ecuador | 6.4% |
| 8 | Switzerland | 6.2% |
| 9 | Mexico | 5.7% |
| 10 | France | 4.9% |

Notice how the ordering shifts between rounds. Brazil is the most likely semi-finalist (30%) but only the third most likely champion (7.5%). Why? The bracket. Brazil's path into the latter rounds runs through tougher opposition than Japan's, so even though Brazil reaches the semis more often, it converts those appearances into trophies less often. That's exactly the kind of draw-dependent insight a simulator captures that a simple power ranking can't.

---

## What this prediction gets wrong

A model is only as honest as its caveats. The headline result — Japan as tournament favourite, Germany tipped for a group-stage exit — should make any football fan squint. It's not a bug in the simulator. It's a limitation of the underlying Dixon-Coles model, and it's worth being precise about why.

**All matches are weighted equally.** Dixon-Coles fits attack and defense parameters from goals scored and conceded, but treats every fixture the same. A World Cup quarter-final and a meaningless September friendly contribute equally to a team's rating. Teams that pad their record with comfortable wins look stronger than they are when it counts.

**No adjustment for confederation strength.** This is the big one. The model has no concept that the European qualifying pool is far deeper than the Asian one. Japan racks up lopsided wins against weaker AFC opponents, inflating its attack parameter. Germany plays a gauntlet of strong European sides, so its goal difference looks more modest — and the model reads that as Germany being weaker. In reality it reflects strength of schedule, which the model is blind to.

**No squad-level information.** Injuries, form, manager changes, an aging core, a golden generation — none of it enters the model. It sees only historical scorelines.

**Monte Carlo noise.** At 100,000 simulations the top probabilities are stable to a few tenths of a percent, but the long tail is noisier. Don't over-read the difference between a 0.06% and a 0.04% team.

---

## How to fix it

The good news: the project already contains the tools to address the biggest flaw.

**Match-importance weighting in the fit.** The `MATCH_WEIGHTS` table used by the Elo system and the `tournament_weight` feature from [Part 2](/2026/06/07/World_Cup_prediction_model_part2/) already encode that a World Cup match matters more than a friendly. Feeding those weights into `fit_fast()` would down-weight the friendly-padded records that currently distort the ratings.

**The XGBoost layer.** The whole point of the feature pipeline was to blend Elo (which does update by match importance and captures strength of schedule through its zero-sum dynamics), recent form, rest, and head-to-head history into a learned classifier. That ensemble would temper Dixon-Coles' confederation blind spot with Elo's relative-strength signal.

And we don't have to guess whether those changes help. The [Part 3 evaluator](/2026/06/08/World_Cup_prediction_model_part3/) lets us backtest any new model against the 2014, 2018, and 2022 World Cups and compare Brier scores directly.

---

## The takeaway

The pipeline works end-to-end. It ingests a century of results, fits a probabilistic scoreline model in seconds, and simulates a full tournament 100,000 times to produce stage-by-stage probabilities for every team.

But the headline number — Japan, 11.6% — is also a good illustration of why you don't ship a model on its first plausible-looking output. The simulator is doing its job correctly; it's faithfully propagating a strength estimate that has a known, explainable bias. Recognising that, quantifying it with backtesting, and correcting it with match weighting and the XGBoost ensemble is the next chapter of the project — and the difference between a model that produces numbers and one you'd actually trust.
