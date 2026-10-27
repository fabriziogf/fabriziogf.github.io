---
title: "Building a World Cup Prediction Model — Part 3: Evaluation & Calibration"
---

In [Part 1](/World_Cup_prediction_model_part1/) I built the Monte Carlo tournament simulator. In [Part 2](/World_Cup_prediction_model_part2/) I built the feature pipeline that adds Elo ratings, form, rest days, and head-to-head history to each match.

Both produce predictions. But you can't trust a model you can't measure. Part 3 closes that loop with a backtesting and calibration framework that shows how well the models would have done on past World Cups.

---

## Why evaluation matters

It's tempting to look at a model's output, see plausible numbers, and call it done. Brazil has a 15% chance to win? Sounds about right. But "sounds about right" isn't a measurement.

Real evaluation asks two questions:

1. **Are the probabilities accurate?** If the model predicts a 70% home win across 100 matches, about 70 of them should end in a home win. If only 50 do, the model is overconfident.
2. **Does it beat a naive baseline?** Predicting 33%/33%/33% for every match gives a Brier score of 0.222. If a sophisticated model can't beat that, something's wrong.

---

## The `ModelEvaluator` class

```python
from src.evaluate import ModelEvaluator

df = pd.read_csv("data/results.csv")
evaluator = ModelEvaluator(df)

# Evaluate on a single tournament
metrics = evaluator.evaluate_tournament(year=2022)

# Compare both models across all three target years
comparison = evaluator.compare_models(years=[2014, 2018, 2022])
```

### Train/eval split

For each target year, the evaluator uses a strict time split:

- **Training set**: every match with `date.year < tournament_year`
- **Evaluation set**: FIFA World Cup matches in `tournament_year` (qualifiers excluded)

Elo and Dixon-Coles are both fit fresh on the training set, then predict each tournament match without seeing any tournament results. That mirrors real conditions: you only know what happened before the tournament started.

I caught one bug here. In 2022, the dataset includes World Cup *qualification* matches alongside the tournament itself. A naive `str.contains("World Cup")` filter pulls in 100 qualifiers on top of the 64 real games, mixing two different prediction tasks. The fix was to exclude any tournament name containing `"qualif"`:

```python
is_wc   = t_lower.str.contains("fifa world cup", na=False)
is_qual = t_lower.str.contains("qualif", na=False)
eval_df = year_df[is_wc & ~is_qual]
```

After the fix: 64 matches each for 2014, 2018, and 2022, the correct count for a 32-team tournament.

---

## Metrics

### Brier score (primary)

The Brier score is the mean squared error of probabilistic predictions. For a three-outcome match (home win / draw / away win):

```
BS = (1/3) × [(p_home - o_home)² + (p_draw - o_draw)² + (p_away - o_away)²]
```

where `o_i` is 1 if outcome `i` happened and 0 otherwise. Lower is better. The uniform 33%/33%/33% baseline scores 0.222. That's the number to beat.

### Log-loss

Log-loss punishes confident wrong predictions harder than Brier. If the model says 95% home win and the away team scores in the 90th minute, log-loss hits that much harder. It's a useful second metric for how the model handles uncertainty at the extremes.

```
LL = -Σ o_i × log(max(p_i, ε))
```

### Accuracy

The simplest check: does the most likely predicted outcome match what happened? Accuracy ignores the size of the probability. A 34% pick that beats two 33%s counts as correct if it happens. It's less informative than Brier for a probabilistic model, but a good sanity check.

---

## Calibration curves

Metrics give one number per model. Calibration curves show *where* the model is wrong.

Group all predictions into deciles by predicted probability, then plot mean predicted probability (x-axis) against actual win rate (y-axis). A perfectly calibrated model sits on the diagonal.

```python
evaluator.plot_calibration(year=2022, model="dc", outcome="home")
```

Three common failure patterns:

- **Overconfident**: the curve sags below the diagonal. The model says 80% but teams win 60% of the time
- **Underconfident**: the curve bows above the diagonal. The model says 40% but teams win 55%
- **Systematic bias**: the whole curve is shifted, meaning base rates are off

`plot_calibration_grid()` produces a full comparison grid, one row per year, Elo and Dixon-Coles side by side:

```python
fig = evaluator.plot_calibration_grid(years=[2014, 2018, 2022])
fig.savefig("calibration_grid.png")
```

---

## How it fits together

All four components are now in place:

```
data/results.csv
      │
      ▼
EloSystem.compute_ratings()      ← team strength over time
      │
      ├──► FeatureBuilder.transform()  ← match-level features for XGBoost
      │
      └──► DixonColes.fit()            ← attack/defense parameters
                 │
                 ├──► TournamentSimulator.simulate()   ← championship probabilities
                 │
                 └──► ModelEvaluator.compare_models()  ← how good is it really?
```

**The evaluator is the quality gate at the end of the pipeline.** Before trusting any tournament simulation, run `compare_models()` to check that Dixon-Coles and Elo are well calibrated on past tournaments. If they aren't, tune (time decay, K-factors, feature weights) and re-evaluate.

---

## What's next

The last piece is the **test suite**: pytest coverage for Elo, Dixon-Coles, and the simulator. With all four modules built and tested, the project is ready for the XGBoost layer, a classifier trained on `FeatureBuilder` output that produces match probabilities on top of the Poisson base.
