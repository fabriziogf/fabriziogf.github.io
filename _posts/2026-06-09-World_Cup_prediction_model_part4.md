---
title: "Building a World Cup Prediction Model — Part 4: Testing the Models"
---

Over the first three parts of this series I built the full predictive pipeline: the [Monte Carlo tournament simulator](/2026/06/06/World_Cup_prediction_model_part1/), the [feature engineering pipeline](/2026/06/07/World_Cup_prediction_model_part2/), and the [backtesting and calibration framework](/2026/06/08/World_Cup_prediction_model_part3/).

Every one of those modules came with an ad-hoc smoke test — a one-off script to confirm it runs and the numbers look sane. That's fine for initial development. But it doesn't protect against regressions. The moment someone tweaks a K-factor or refactors the bracket seeding, those smoke tests are gone and nothing catches the break.

Part 4 turns those informal checks into a permanent, automated safety net: a pytest suite that runs in seconds and verifies the mathematical guarantees each model is supposed to uphold.

---

## Testing philosophy for statistical models

Testing probabilistic models is different from testing ordinary application code. You usually can't assert exact output values — a Monte Carlo simulation gives slightly different numbers every run, and a fitted model's parameters depend on optimisation details.

Instead, you test **invariants** — properties that must hold no matter what:

- **Structural invariants**: probabilities sum to 1, score matrices normalise, every team appears exactly once
- **Directional invariants**: a stronger team must have a higher win probability than a weaker one; a higher-stakes match must move ratings more than a friendly
- **Conservation laws**: Elo is zero-sum, so total points in the system never change
- **Boundary behaviour**: edge cases like the Dixon-Coles tau correction return exact, known values

These hold regardless of the random seed or the exact fitted parameters, which makes them reliable test targets.

---

## The suite at a glance

```
tests/
├── test_elo.py        # 8 tests — rating dynamics
├── test_poisson.py    # 9 tests — scoreline model
└── test_simulate.py   # 8 tests — bracket simulator
```

25 tests total, all passing in ~87 seconds.

```
======================== 25 passed in 86.73s (0:01:26) =========================
```

---

## `test_elo.py` — Rating dynamics

The Elo system is deterministic, so these tests can assert precise behaviour.

| Test | What it verifies |
|------|------------------|
| `test_teams_initialise_at_base_rating` | Unseen teams start at 1500 |
| `test_single_match_first_appearance_starts_from_base` | Pre-match ratings of a debut match are both 1500 |
| `test_winner_gains_loser_loses` | A decisive result moves the winner up, loser down |
| `test_draw_between_equal_teams_no_change` | Equal teams drawing at a neutral venue stay put |
| `test_total_elo_is_constant` | Zero-sum: total system Elo equals `n_teams × 1500` |
| `test_higher_k_produces_larger_swing` | A World Cup match (K=60) moves ratings more than a friendly (K=10) |
| `test_predict_probabilities_sum_to_one` | `predict()` home/draw/away probabilities sum to 1 |
| `test_stronger_team_higher_win_prob` | A team with several wins is favoured over its victims |

The zero-sum test is the most important — it's the mathematical heart of Elo. If a refactor ever broke the symmetry of the rating update, this catches it immediately:

```python
def test_total_elo_is_constant(simple_matches):
    elo = EloSystem()
    elo.compute_ratings(simple_matches)
    total = sum(elo.ratings.values())
    n_teams = len(elo.ratings)
    assert total == pytest.approx(n_teams * BASE_RATING)
```

---

## `test_poisson.py` — The scoreline model

The Dixon-Coles model is fitted via maximum likelihood, which is the slow part of the suite. To keep things fast, the fitted model is built **once** as a module-scoped fixture and shared across all nine tests:

```python
@pytest.fixture(scope="module")
def fitted_model():
    # 4 teams, engineered strengths, ~180 synthetic matches
    ...
    model = DixonColes(time_decay=0)
    model.fit(df)
    return model
```

The synthetic data is generated with known latent strengths (Brazil > Germany > France > Chile), which lets us assert the model *recovers* that ordering.

| Test | What it verifies |
|------|------------------|
| `test_fit_runs_and_sets_params` | Fitting populates attack, defense, home_adv, rho |
| `test_score_matrix_sums_to_one` | The scoreline matrix normalises to ~1.0 |
| `test_score_matrix_is_nonnegative` | No negative probabilities |
| `test_predict_outcome_probabilities_sum_to_one` | Home/draw/away sum to ~1 |
| `test_predict_knockout_sums_to_one` | Draw mass split so two win probs sum to ~1 |
| `test_stronger_team_higher_win_probability` | Brazil beats Chile more often than the reverse |
| `test_strength_ordering_recovered` | Fitted net strengths preserve Brazil > Chile |
| `test_tau_edge_cases` | The Dixon-Coles correction returns exact values |
| `test_predict_unfitted_raises` | Predicting before fitting raises a clear error |

The tau correction test is a good example of testing exact boundary behaviour. The Dixon-Coles low-score adjustment has a precise closed form for each of the four corrected scorelines:

```python
def test_tau_edge_cases():
    lam, mu, rho = 1.5, 1.2, -0.1
    assert DixonColes._tau(lam, mu, 0, 0, rho) == pytest.approx(1 - lam * mu * rho)
    assert DixonColes._tau(lam, mu, 1, 0, rho) == pytest.approx(1 + mu * rho)
    assert DixonColes._tau(lam, mu, 0, 1, rho) == pytest.approx(1 + lam * rho)
    assert DixonColes._tau(lam, mu, 1, 1, rho) == pytest.approx(1 - rho)
    assert DixonColes._tau(lam, mu, 2, 3, rho) == 1.0   # no correction
```

---

## `test_simulate.py` — The bracket simulator

Testing the simulator had a performance problem: it needs a fitted Dixon-Coles model covering all 32 teams, and fitting that via MLE on a full round-robin would take minutes — too slow for a test suite.

The solution was to **bypass the fit entirely and inject hand-crafted parameters**. The simulator only ever reads `params_`, `teams_`, and `is_fitted_`, so you can construct a model with engineered attack/defense values directly:

```python
def _engineered_model() -> DixonColes:
    model = DixonColes()
    # All teams neutral, except a dominant favourite and a weak outsider
    attack[FAVOURITE]  = 1.2;  defense[FAVOURITE]  = -1.2
    attack[OUTSIDER]   = -1.2; defense[OUTSIDER]   = 1.2
    model.teams_ = sorted(ALL_TEAMS)
    model.params_ = {"attack": attack, "defense": defense, "home_adv": 0.1, "rho": -0.1}
    model.is_fitted_ = True
    return model
```

This makes the simulator tests fast and deterministic (via a fixed seed), while still exercising the full bracket logic.

| Test | What it verifies |
|------|------------------|
| `test_win_probabilities_sum_to_one` | Exactly one champion per sim → p_win sums to 1 |
| `test_stage_sums_are_consistent` | Stage sums are 2 / 4 / 8 / 16 / 16 (final/semi/QF/R16/group exit) |
| `test_all_teams_present` | Every bracket team appears exactly once |
| `test_probabilities_in_valid_range` | All probabilities within [0, 1] |
| `test_favourite_wins_more_than_outsider` | The strong team wins more than the weak one |
| `test_favourite_is_top_ranked` | The favourite is the single most likely champion |
| `test_mid_tournament_update_changes_probabilities` | A team that loses all group games collapses to 0% |
| `test_known_result_respected_in_group` | A team handed 9 points reliably advances (>90%) |

The mid-tournament test is the most valuable. It validates the `simulate_from_current()` feature from Part 1 — the one that lets the model update live as results come in. By feeding in three group-stage losses for the favourite, we confirm its championship probability drops to exactly zero:

```python
def test_mid_tournament_update_changes_probabilities():
    baseline = sim.simulate(GROUPS)
    # Brazil loses all three group matches 0-3
    updated = sim.simulate_from_current(GROUPS, results_so_far)
    assert p_fav_updated < p_fav_baseline
    assert p_fav_updated == pytest.approx(0.0, abs=1e-9)
```

---

## Lessons from writing these tests

**Inject, don't fit.** When the expensive part of a system isn't what you're testing, construct the object's state directly. The simulator tests run in seconds because they never touch the optimiser.

**Test invariants, not values.** You can't assert "Brazil wins 18.3% of the time" — that's seed-dependent. But you can assert "Brazil wins more than Tonga" and "all probabilities sum to 1." Those hold forever.

**Seed everything random.** Every simulator test passes a fixed seed, so a failure is reproducible rather than a flaky once-in-ten event.

**Share expensive fixtures.** The module-scoped `fitted_model` fixture fits Dixon-Coles once and reuses it across nine tests, instead of paying the fit cost nine times.

---

## The project, complete

With the test suite in place, all four modules are built, verified, and on `main`:

```
✅ src/elo.py         — Elo ratings
✅ src/poisson.py     — Dixon-Coles model
✅ src/simulate.py    — tournament simulator
✅ src/features.py    — feature pipeline
✅ src/evaluate.py    — backtesting & calibration
✅ tests/             — 25 passing tests
```

The foundation is solid enough to build on. The natural next step is the **XGBoost prediction layer** that consumes the `FeatureBuilder` output — and when that lands, it'll come with its own tests validated against the same Brier-score backtests from Part 3.
