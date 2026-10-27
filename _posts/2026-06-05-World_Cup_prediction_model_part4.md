---
title: "Building a World Cup Prediction Model — Part 4: Testing the Models"
---

In the first three parts I built the full pipeline: the [Monte Carlo tournament simulator](/World_Cup_prediction_model_part1/), the [feature pipeline](/World_Cup_prediction_model_part2/), and the [backtesting and calibration framework](/World_Cup_prediction_model_part3/).

Each module came with an ad-hoc smoke test, a one-off script to check that it runs and the numbers look sane. That's fine during early development, but it doesn't catch regressions. Once someone tweaks a K-factor or refactors bracket seeding, those scripts are long gone and nothing flags the break.

Part 4 turns those informal checks into an automated safety net: a pytest suite that verifies the mathematical guarantees each model is supposed to keep.

---

## Testing statistical models

Testing probabilistic models isn't like testing regular application code. You usually can't assert exact outputs. A Monte Carlo simulation gives slightly different numbers each run, and fitted parameters depend on optimizer details.

So you test **invariants**, properties that must hold no matter what:

- **Structural**: probabilities sum to 1, score matrices normalize, every team appears exactly once
- **Directional**: a stronger team has a higher win probability than a weaker one; a high-stakes match moves ratings more than a friendly
- **Conservation**: Elo is zero-sum, so total points in the system never change
- **Boundaries**: edge cases like the Dixon-Coles tau correction return exact, known values

These hold regardless of random seed or fitted parameters, which makes them reliable test targets.

---

## The suite

```
tests/
├── test_elo.py        # 8 tests — rating dynamics
├── test_poisson.py    # 9 tests — scoreline model
└── test_simulate.py   # 8 tests — bracket simulator
```

25 tests, all passing in about 87 seconds.

```
======================== 25 passed in 86.73s (0:01:26) =========================
```

---

## `test_elo.py`: rating dynamics

Elo is deterministic, so these tests can assert exact behavior.

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

The zero-sum test matters most. It's the mathematical core of Elo. If a refactor ever breaks the symmetry of the update, this catches it right away:

```python
def test_total_elo_is_constant(simple_matches):
    elo = EloSystem()
    elo.compute_ratings(simple_matches)
    total = sum(elo.ratings.values())
    n_teams = len(elo.ratings)
    assert total == pytest.approx(n_teams * BASE_RATING)
```

---

## `test_poisson.py`: the scoreline model

Dixon-Coles is fit by maximum likelihood, the slow part of the suite. To keep it fast, the model is fit **once** as a module-scoped fixture and shared by all nine tests:

```python
@pytest.fixture(scope="module")
def fitted_model():
    # 4 teams, engineered strengths, ~180 synthetic matches
    ...
    model = DixonColes(time_decay=0)
    model.fit(df)
    return model
```

The synthetic data uses known strengths (Brazil > Germany > France > Chile), so I can check that the model *recovers* that order.

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

The tau test is a good example of checking exact boundary behavior. The Dixon-Coles low-score adjustment has a closed form for each of the four corrected scorelines:

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

## `test_simulate.py`: the bracket simulator

The simulator tests had a speed problem. They need a fitted Dixon-Coles model covering all 32 teams, and fitting that by MLE on a full round-robin takes minutes. Too slow for a test suite.

The fix was to **skip the fit and inject hand-made parameters**. The simulator only reads `params_`, `teams_`, and `is_fitted_`, so I can build a model with engineered attack and defense values directly:

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

That keeps the simulator tests fast and deterministic (with a fixed seed) while still running the full bracket logic.

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

The mid-tournament test is the most valuable. It checks `simulate_from_current()` from Part 1, the feature that updates the model live as results come in. Feeding in three group-stage losses for the favourite should drop its title chances to exactly zero:

```python
def test_mid_tournament_update_changes_probabilities():
    baseline = sim.simulate(GROUPS)
    # Brazil loses all three group matches 0-3
    updated = sim.simulate_from_current(GROUPS, results_so_far)
    assert p_fav_updated < p_fav_baseline
    assert p_fav_updated == pytest.approx(0.0, abs=1e-9)
```

---

## Lessons

**Inject, don't fit.** When the expensive part of a system isn't what you're testing, build the object's state directly. The simulator tests run in seconds because they never touch the optimizer.

**Test invariants, not values.** You can't assert "Brazil wins 18.3% of the time." That depends on the seed. But you can assert "Brazil wins more than Tonga" and "all probabilities sum to 1." Those always hold.

**Seed everything random.** Every simulator test uses a fixed seed, so a failure is reproducible instead of a flaky one-in-ten event.

**Share expensive fixtures.** The module-scoped `fitted_model` fits Dixon-Coles once and reuses it across nine tests instead of paying for the fit nine times.

---

## Where the project stands

With the tests in place, every module is built, verified, and on `main`:

```
✅ src/elo.py         — Elo ratings
✅ src/poisson.py     — Dixon-Coles model
✅ src/simulate.py    — tournament simulator
✅ src/features.py    — feature pipeline
✅ src/evaluate.py    — backtesting & calibration
✅ tests/             — 25 passing tests
```

The foundation is solid enough to build on. The next step is the **XGBoost layer** that consumes `FeatureBuilder` output. When it lands, it'll come with its own tests, checked against the same Brier-score backtests from Part 3.
