---
title: "Building a World Cup Prediction Model — Part 6: First Predictions (And Why They're Wrong)"
---

Five parts in, the pipeline is complete and, after the [Part 5](/World_Cup_prediction_model_part5/) performance fix, it actually runs. So I ran it.

The results are interesting, but not in the way you'd want from a finished model. Japan comes out as the tournament favourite. Germany gets tipped for a group-stage exit. That's what the model produces, and it's clearly off. This post shows the first predictions, explains why they don't make sense, and lays out the fixes in progress.

The setup:

- **Model**: Dixon-Coles, fit on all ~11,900 international matches since 2014, with exponential time decay so recent form counts more
- **Bracket**: a 32-team, 8-group tournament
- **Simulation**: 100,000 Monte Carlo runs of the full bracket, from the group stage to the final

```bash
python notebooks/predict_winner.py
```

---

## Group stage

Each group plays a round-robin and the top two advance to the Round of 16. The `p_r16` column is each team's chance of getting out of its group. Within each group these sum to ~200% (two qualifiers per group).

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

A few things stand out:

**Group E is brutal.** Germany, a four-time world champion, is the model's pick to go out in the group at 51%, behind Japan and Spain. That's the model's confederation bias showing (more below).

**Group A has no clear favourite.** Three teams sit between 59% and 69%. Qatar is basically out on arrival at 7%.

**Argentina (77%) and Brazil (78%)** are the safest group-stage qualifiers in the field.

---

## Knockout rounds

As teams advance, the probabilities concentrate. The top contenders at each stage:

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

### Champion

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

The order shifts between rounds. Brazil is the most likely semi-finalist (30%) but only the third most likely champion (7.5%). Why? The bracket. Brazil's path through the later rounds is tougher than Japan's, so even though Brazil reaches the semis more often, it turns those runs into titles less often. **That's the kind of draw-dependent result a simulator captures and a simple power ranking can't.**

---

## What this gets wrong

A model is only as honest as its caveats. Japan as favourite and Germany out in the group should make any football fan squint. It isn't a simulator bug. It's a limitation of the Dixon-Coles model underneath, and it's worth being precise about why.

**Every match counts the same.** Dixon-Coles fits attack and defense parameters from goals scored and conceded, but treats all fixtures equally. A World Cup quarter-final and a meaningless September friendly carry the same weight. Teams that pad their record with easy wins look stronger than they are when it counts.

**No adjustment for confederation strength.** This is the big one. The model doesn't know that Europe's qualifying pool is far deeper than Asia's. Japan racks up lopsided wins against weaker AFC teams, which inflates its attack parameter. Germany plays a gauntlet of strong European sides, so its goal difference looks modest, and the model reads that as weakness. It's really strength of schedule, and the model can't see it.

**No squad information.** Injuries, form, manager changes, an aging core, a golden generation: none of it enters the model. It only sees historical scores.

**Monte Carlo noise.** At 100,000 runs the top probabilities are stable to a few tenths of a percent, but the long tail is noisier. Don't read much into 0.06% vs. 0.04%.

---

## What I'm fixing

The project already has the tools for the biggest flaws, and both fixes are in progress.

**Match-importance weighting in the fit.** The `MATCH_WEIGHTS` table in the Elo system and the `tournament_weight` feature from [Part 2](/World_Cup_prediction_model_part2/) already encode that a World Cup match matters more than a friendly. Feeding those weights into `fit_fast()` will down-weight the friendly-padded records that distort the ratings. It's the most direct fix for the confederation bias.

**The XGBoost layer.** The whole point of the feature pipeline was to combine Elo (which does weight by match importance and captures strength of schedule through its zero-sum updates), recent form, rest, and head-to-head history in a learned classifier. That ensemble should offset Dixon-Coles' confederation blind spot with Elo's relative-strength signal.

Neither fix is guesswork. The [Part 3 evaluator](/World_Cup_prediction_model_part3/) can backtest any new model against the 2014, 2018, and 2022 World Cups and compare Brier scores directly. The fixes either improve the numbers or they don't, and I'll know which.

---

## Takeaway

The pipeline works end to end. It takes in a century of results, fits a probabilistic scoreline model in seconds, and simulates a full tournament 100,000 times to give every team stage-by-stage probabilities.

But Japan as favourite and Germany out in the group are a good reminder not to stop at the first plausible-looking output. **The simulator is doing its job. It's faithfully passing along a strength estimate with a known, explainable bias.** The next post will show whether the fixes move the numbers the right way.
