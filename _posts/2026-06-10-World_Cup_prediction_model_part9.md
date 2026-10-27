---
title: "Building a World Cup Prediction Model — Part 9: The Ensemble"
---

[Part 8](/World_Cup_prediction_model_part8/) ended with a diagnosis, not a fix. Even after vectorizing the fit, adding match-importance and confederation weights, and tuning them by backtest, Dixon-Coles still made Japan the favourite over Brazil, France, and England. The problem was structural. A model that reduces each team to a goals-based attack/defense pair is too thin to capture football strength, and reweighting can't fix a feature that weak.

The prescription was an **Elo + gradient-boosted trees ensemble**: replace the goals signal with opponent-adjusted Elo ratings, and let a learned classifier combine many features instead of two. This part builds it and checks whether the diagnosis was right.

---

## Design

The new model, `EloXGBoostModel`, has two layers.

### Layer 1: Elo

I built the Elo system early in the project, and it's sat unused in the prediction path ever since. It does exactly what Dixon-Coles can't: it ignores how many goals you score and only cares who you beat and how surprising that was. Thrashing a weak side earns almost nothing. Beating a strong one earns a lot. Strength of schedule is built in, with no hand-set confederation table.

### Layer 2: Boosted trees

On top of Elo, a gradient-boosted trees classifier predicts a three-way outcome (home win / draw / away win) from the [Part 2](/World_Cup_prediction_model_part2/) features:

- `elo_diff`, `elo_home`, `elo_away` — opponent-adjusted strength
- `form_home`, `form_away` — exponentially weighted recent points-per-game
- `rest_days_home`, `rest_days_away` — fixture congestion
- `is_neutral`, `tournament_weight` — match context
- `h2h_home_winrate` — historical matchups

The model *learns* how much to trust each feature. It can learn that `elo_diff` matters far more than any raw goal total, which is the correction Dixon-Coles structurally can't make.

### Three engineering details

**Leak-free features, fast.** `FeatureBuilder` from Part 2 is correct but O(n²): it re-scans history for every row. On 49,000 matches that's too slow. So the ensemble builds features in one chronological pass, tracking each team's form and rest as it goes, and computing each row's features *before* adding that match's result. The full feature build takes seconds.

**Neutral-venue symmetry.** A World Cup knockout has no home team, but the model is trained with home/away framing. For knockouts I predict both orientations (A at home, B at home) and average them, which cancels any leftover home bias before splitting the draw probability.

**A pluggable booster, and an OpenMP problem.** The plan was XGBoost. XGBoost had other plans: on this machine its native library wouldn't load because of a missing OpenMP symbol. The fix was `conda install -c conda-forge llvm-openmp` to update the bundled OpenMP runtime. To keep the code robust either way, the booster is pluggable. It uses real XGBoost when the library loads and falls back to scikit-learn's `HistGradientBoostingClassifier` (functionally equivalent, no native dependency) when it doesn't. Same `fit`/`predict_proba` API either way.

The fitted model exposes `predict()`, `predict_knockout()`, `teams_`, and `is_fitted_`, so it drops into the existing `TournamentSimulator` with no changes.

---

## The result

Fit on the full match history (49,411 games, ~5 seconds) and simulated through the official 2026 bracket, here's the new top of the table next to the old Dixon-Coles ranking:

| Rank | Ensemble | Win % | Dixon-Coles had |
|------|----------|-------|-----------------|
| 1 | **Argentina** | 17.2% | 3rd (7.5%) |
| 2 | Spain | 12.8% | 4th |
| 3 | France | 8.9% | 8th (4.4%) |
| 4 | Brazil | 6.8% | 7th (4.7%) |
| 5 | Portugal | 4.7% | 5th |
| 6 | England | 4.7% | **21st (1.8%)** |
| 7 | Germany | 3.4% | 11th |
| 8 | Japan | 3.3% | **1st (12.9%)** |

This passes the smell test. The reigning champions are favourites. The traditional powers (Spain, France, Brazil, England, Germany) fill the top. Japan fell from 1st to 8th, and England rose from 21st to 6th. Every glaring problem from Part 8 is gone, for the right reason: Elo knows Japan's record is padded against weaker AFC teams, and England's cautious 1-0 wins came against serious opponents.

---

## Is it actually better?

A ranking that looks right isn't proof. So I backtested both models the same way: train on everything before a tournament, predict its matches, score them. Three World Cups, 64 matches each.

| Tournament | Brier (DC → Ensemble) | Accuracy (DC → Ensemble) |
|------------|----------------------|--------------------------|
| 2014 | 0.186 → 0.198 | 56% → 56% |
| 2018 | 0.208 → 0.205 | 47% → 53% |
| 2022 | 0.232 → **0.201** | 38% → **58%** |
| **Overall** | **0.2084 → 0.2012** | **46.9% → 55.7%** |

The ensemble wins on every overall metric: Brier improves 3.5%, log-loss goes from 1.051 to 1.021, and accuracy jumps almost nine points to 55.7%. It now picks the right outcome more than half the time, against a model that was barely better than a random three-way guess.

### Caveats

- **The ensemble lost in 2014.** On the oldest tournament, Dixon-Coles had the better Brier (0.186 vs 0.198). The ensemble's edge is in recent tournaments, where Elo and form rest on denser, more reliable data, which is also where time decay points it.
- **64 matches is a small sample.** Per-tournament differences carry real variance. The overall average is the better signal.
- **The +3.5% understates the real gain.** Match-level Brier is dominated by lopsided group games, so it barely moves when the champion ranking goes from absurd to sensible. The metric and the eye agree on direction, but the metric badly under-reports the size of the change.

---

## Why it worked

The fix wasn't smarter tuning. It was a better signal. Two things did the heavy lifting:

**Elo encodes opponent quality.** Beating up a weak confederation no longer inflates a rating. Japan's flattering goal difference stops mattering once the model sees who those goals came against.

**A learned classifier can prefer `elo_diff` over goals.** Dixon-Coles has to explain results through scoring rates. The boosted trees are free to learn that the Elo gap predicts outcomes better than any goal total, and weight it that way.

Parts 6 and 7 reweighted which matches fed a thin feature. Part 9 changed what the model measures. **That's the difference between polishing a flawed answer and fixing it.**

---

## What's still imperfect

The ensemble is better, not perfect.

- It still uses a 25% draw approximation in the group stage. That's a simulator simplification, not the model's fault.
- It was validated on per-match Brier, which I've now argued three times is the wrong yardstick for a tournament model. The right test scores *tournament-level* output: log-loss against actual champions and finalists across many simulated runs. Building that metric is the next step.
- The 2014 loss and the small sample mean the +3.5% deserves humility, not a victory lap.

But the question from Part 8, whether richer features can finally produce a favourite you'd bet on, now has an answer. Argentina, Spain, France, Brazil. Yes.

Next: a tournament-level evaluation that scores the champion ranking directly, so the metric finally measures what my eyes have been measuring all along.
