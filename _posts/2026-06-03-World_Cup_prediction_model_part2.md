---
title: "Building a World Cup Prediction Model — Part 2: Feature Engineering"
---

In [Part 1](/World_Cup_prediction_model_part1/) I built the Monte Carlo tournament simulator, the engine that runs thousands of bracket simulations and returns championship probabilities. It uses the Dixon-Coles Poisson model to decide individual matches.

This part makes that prediction layer richer. The feature pipeline describes each match in numbers. Not just "Brazil vs. France," but "Brazil with a 120-point Elo edge, 4 days of rest, 2.1 weighted points per game, at a neutral venue in a World Cup qualifier." Those features feed an XGBoost layer that sits on top of the Poisson base.

---

## The core constraint: no lookahead

The most important rule in any sports prediction pipeline is **no lookahead bias**: the model can never see the future when predicting the past.

It's easy to break by accident. Computing a team's average goals over a season and attaching it to every match in that season leaks future results into the early rows. Rolling windows that ignore match order have the same problem.

The fix is simple but has to be enforced. For the match at row `t`, feature computation only sees `df.iloc[:t]`, the rows strictly before it:

```python
for idx, row in df.iterrows():
    records.append(self._compute_row(row, df.iloc[:idx]))
```

That slice gets passed to every helper as `past_matches`. It makes it structurally impossible for a feature to reference a future match.

---

## The `FeatureBuilder` class

Usage:

```python
from src.elo import EloSystem
from src.features import FeatureBuilder

elo = EloSystem()
df = elo.load_matches("data/results.csv")
elo.compute_ratings()

builder = FeatureBuilder(elo_system=elo)
features = builder.transform(df)
```

`transform(df)` returns a DataFrame with 10 columns, aligned row-for-row with the input:

| Column | Type | Description |
|--------|------|-------------|
| `elo_home` | float | Home team's Elo rating just before this match |
| `elo_away` | float | Away team's Elo rating just before this match |
| `elo_diff` | float | `elo_home - elo_away` |
| `form_home` | float | Exponentially weighted PPG for home team (last 10 matches) |
| `form_away` | float | Same for away team |
| `rest_days_home` | int | Days since home team's last match (-1 if debut) |
| `rest_days_away` | int | Days since away team's last match (-1 if debut) |
| `is_neutral` | int | 1 if played at a neutral venue, 0 otherwise |
| `tournament_weight` | float | Numeric importance of the match type |
| `h2h_home_winrate` | float | Home team's historical win rate in this head-to-head |

---

## Feature design

### Elo at match time

The Elo system keeps a full audit trail. `elo.history` records pre- and post-match ratings for every team in every game. To get the rating at match time, I take the most recent `post_elo` for each team strictly before the match date:

```python
home_rows = hist[(hist["home_team"] == team) & (hist["date"] < date)]
away_rows = hist[(hist["away_team"] == team) & (hist["date"] < date)]
# Take the most recent appearance (either home or away)
return max(candidates, key=lambda x: x[0])[1]
```

This covers teams that appear both home and away, always picking the latest rating.

### Form: exponentially weighted PPG

Recent form matters more than results from three months ago. I compute points per game (Win=3, Draw=1, Loss=0) over the last 10 matches, weighted so the most recent match counts most:

```python
weights = np.array([np.exp((i - n + 1) / ewm_span) for i in range(n)])
weights /= weights.sum()
form = np.dot(weights, points)
```

With `ewm_span=5`, a match 5 games ago carries about 37% of the weight of the latest one. Teams with no history get a neutral **1.0**, the middle of a typical PPG range in international football.

### Rest days

Fixture congestion is real. Teams on 3 days' rest do measurably worse than teams with a full week off. `rest_days` is the number of days since the team's last match. On a debut it returns **-1** as a sentinel, which downstream models can handle with imputation or a separate flag.

### Tournament weight

A World Cup final matters far more than a January friendly, and the model should know that. `tournament_weight` maps the `tournament` column to the same K-factor scale `EloSystem` uses:

| Tournament type | Weight |
|----------------|--------|
| Friendly | 10 |
| Qualification | 25 |
| Confederation | 35 |
| Confederation final | 40 |
| World Cup | 60 |

That gives XGBoost one numeric signal for match importance instead of one-hot encoding hundreds of tournament names.

### Head-to-head win rate

Past meetings between two specific teams can capture things Elo and form miss: rivalries, psychological edges, stylistic matchups. I look at their last 10 meetings regardless of venue and compute the home team's win rate:

```python
wins / total  # draws count as 0 wins for both sides
```

Pairs that have never met get **0.5**, a neutral prior.

---

## Sample output

`transform()` on 20 matches from 2018 onward:

```
   elo_home  elo_away  elo_diff  form_home  form_away  rest_days_home  rest_days_away  is_neutral  tournament_weight  h2h_home_winrate
   1689.43   1574.77    114.65       1.00       1.00              -1              -1           0               20.0              0.50
   1588.27   1697.22   -108.95       1.00       1.00              -1              -1           1               20.0              0.50
   1604.77   1668.70    -63.93       1.00       1.00              -1              -1           0               20.0              0.50
   ...
```

Three checks passed:

- **Zero nulls** in all 10 columns. Every feature has a fallback for teams with no history
- **Elo diff range** of -166 to +168 on the 2018+ slice, consistent with realistic rating spreads
- **No exceptions** on any match in the dataset

---

## What's next

With features in place, three pieces remain:

**Backtesting and evaluation.** The evaluation module runs the full pipeline against the 2014, 2018, and 2022 World Cups and measures Brier score, log-loss, accuracy, and calibration curves. The question isn't just whether the eventual winner got a high probability. It's whether the whole distribution was well calibrated across all 64 matches.

**XGBoost layer.** A gradient-boosted classifier trained on the `FeatureBuilder` output to predict outcomes. It sits on top of Dixon-Coles: the Poisson model handles scorelines, XGBoost handles richer match context.

**Test suite.** pytest coverage for Elo, Dixon-Coles, and the simulator end to end.

More in Part 3.
