---
title: "Building a World Cup Prediction Model — Part 3: Evaluation & Calibration"
---

In [Part 1](/World_Cup_prediction_model_part1/) I built the Monte Carlo tournament simulator. In [Part 2](/World_Cup_prediction_model_part2/) I built the feature engineering pipeline that enriches each match with Elo ratings, form, rest days, and head-to-head history.

Both of those produce predictions. But a model you can't measure is a model you can't trust. Part 3 is about closing that loop — building a backtesting and calibration framework that tells you objectively how well the models would have performed on past World Cups.

---

## Why evaluation matters

It's tempting to look at a model's output, see plausible numbers, and call it done. Brazil has a 15% chance to win? Sounds about right. But "sounds about right" isn't a measurement.

Proper evaluation forces two honest questions:

1. **Are the probabilities accurate?** If the model predicts 70% home win across 100 matches, roughly 70 of them should actually end in a home win. If only 50 do, the model is systematically overconfident.
2. **Does it beat a naive baseline?** A model that always predicts 33%/33%/33% for every match achieves a Brier score of 0.222. If a sophisticated model can't beat that, something is wrong.

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

For each target year, the evaluator applies a strict temporal split:

- **Training set**: every match with `date.year < tournament_year`
- **Evaluation set**: FIFA World Cup matches in `tournament_year` (qualification rounds excluded)

Both the Elo system and Dixon-Coles model are fitted fresh on the training set, then used to predict each tournament match without seeing any tournament results. This mirrors real prediction conditions — you only know what happened before the tournament started.

One bug caught during development: in 2022, the dataset includes FIFA World Cup *qualification* matches alongside the actual tournament. A naive `str.contains("World Cup")` filter pulls in 100 qualification matches on top of the 64 actual games, mixing two different prediction tasks. The fix was to explicitly exclude any tournament name containing `"qualif"`:

```python
is_wc   = t_lower.str.contains("fifa world cup", na=False)
is_qual = t_lower.str.contains("qualif", na=False)
eval_df = year_df[is_wc & ~is_qual]
```

After the fix: 64 matches each for 2014, 2018, and 2022 — the correct count for a 32-team knockout tournament.

---

## Metrics

### Brier score (primary)

The Brier score measures the mean squared error of probabilistic predictions. For a three-outcome match (home win / draw / away win):

```
BS = (1/3) × [(p_home - o_home)² + (p_draw - o_draw)² + (p_away - o_away)²]
```

where `o_i` is 1 if outcome `i` occurred, 0 otherwise. Lower is better. The uniform 33%/33%/33% baseline scores 0.222 — that's the number to beat.

### Log-loss

Log-loss penalises confident wrong predictions more severely than Brier score. If the model says 95% home win and the away team scores in the 90th minute, log-loss punishes that much harder. It's a useful companion metric for seeing how well the model handles uncertainty at the extremes.

```
LL = -Σ o_i × log(max(p_i, ε))
```

### Accuracy

The simplest check: does the most probable predicted outcome match what actually happened? Accuracy doesn't care about the size of the probability — a 34% prediction beats a 33%/33% tie and counts as correct if it wins. Less informative than Brier for a probabilistic model, but a good sanity check.

---

## Calibration curves

Metrics give you one number per model. Calibration curves show you *where* the model is wrong.

The idea: group all predictions by their predicted probability (binned into deciles), then plot the mean predicted probability on the x-axis against the actual win rate on the y-axis. A perfectly calibrated model lies on the diagonal.

```python
evaluator.plot_calibration(year=2022, model="dc", outcome="home")
```

Three common failure modes visible in calibration plots:

- **Overconfident**: the curve bows below the diagonal — the model predicts 80% but teams only win 60% of the time
- **Underconfident**: the curve bows above the diagonal — the model predicts 40% but teams actually win 55%
- **Systematic bias**: the whole curve is shifted, suggesting the base rates are off

The `plot_calibration_grid()` method produces a full comparison grid — one row per year, Elo vs. Dixon-Coles side by side:

```python
fig = evaluator.plot_calibration_grid(years=[2014, 2018, 2022])
fig.savefig("calibration_grid.png")
```

---

## How it fits into the project

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

The evaluator sits at the end of the pipeline as the quality gate. Before trusting any tournament simulation, you run `compare_models()` to verify the Dixon-Coles and Elo predictions are well-calibrated on past tournaments. If they're not, you tune — time decay parameters, K-factors, feature weights — and re-evaluate.

---

## What's next

The final piece is the **test suite** — pytest coverage for the Elo system, Dixon-Coles model, and tournament simulator. With all four modules built and tested, the project is ready for the XGBoost prediction layer: a learned classifier trained on the `FeatureBuilder` output that produces match outcome probabilities on top of the probabilistic Poisson base.
