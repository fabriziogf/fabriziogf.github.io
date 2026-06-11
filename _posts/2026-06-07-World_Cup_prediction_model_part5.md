---
title: "Building a World Cup Prediction Model — Part 5: Making It Actually Run"
---

By the end of [Part 4](/2026/06/09/World_Cup_prediction_model_part4/) every module was built and tested: Elo ratings, the Dixon-Coles scoreline model, the Monte Carlo simulator, the feature pipeline, the evaluator, and 25 passing tests. The pipeline was correct.

Then I tried to use it for real — fit Dixon-Coles on ~12,000 historical matches and simulate a tournament — and the job ran for **over 10 hours before being killed**.

Correct, but unusable. This part is about diagnosing that problem and fixing it properly. The short version: it was never a hardware problem. It was a `for` loop.

---

## Diagnosing the bottleneck

The slow path lives in `DixonColes.fit()`. The model is fitted by maximum likelihood — an optimiser (L-BFGS-B) searches parameter space to minimise the negative log-likelihood. The objective function looked like this:

```python
def neg_log_likelihood(x):
    ...
    ll = 0.0
    for _, row in df.iterrows():          # Python loop over every match
        ...
        lam = np.exp(attack[i] + defense[j] + home)
        mu  = np.exp(attack[j] + defense[i])
        tau = self._tau(lam, mu, hg, ag, rho)
        ll += w * (np.log(tau + 1e-10)
                   + poisson.logpmf(hg, lam)   # scalar scipy call per row
                   + poisson.logpmf(ag, mu))
    return -ll
```

Two compounding problems:

1. **`df.iterrows()`** is the slowest way to traverse a DataFrame — it builds a `Series` object for every single row.
2. **`scipy.stats.poisson.logpmf`** called on scalars has heavy per-call overhead. It's designed to be called once on a whole array, not 24,000 times in a loop.

Now multiply it out. The optimiser doesn't call this function once — it calls it thousands of times. With ~65 teams there are ~130 parameters, and L-BFGS estimates the gradient by finite differences, so each iteration needs ~130 evaluations. Across hundreds of iterations:

```
~130 params × ~hundreds of iterations × 12,000 rows × 2 scipy calls
≈ on the order of 10⁹ Python-level operations
```

That's the 10-hour figure. No faster CPU fixes an algorithm shaped like this — you'd shave a constant factor off something that's fundamentally the wrong shape.

---

## The fix: vectorisation

The key insight: the likelihood is the same arithmetic applied to every match independently. That's exactly what NumPy does in compiled C — if you express it as array operations instead of a Python loop.

The fix lives in a new module, `src/fast_poisson.py`, whose `fit_fast()` produces the identical `params_` dictionary as the original — a drop-in replacement.

### Step 1: Encode everything as arrays once

```python
home_idx = df["home_team"].map(idx).to_numpy()
away_idx = df["away_team"].map(idx).to_numpy()
hg = df["home_score"].astype(int).to_numpy()
ag = df["away_score"].astype(int).to_numpy()
```

### Step 2: Evaluate the whole dataset in one shot

Instead of looping, every match is computed simultaneously by indexing the parameter arrays with the team-index arrays:

```python
lam = np.exp(attack[home_idx] + defense[away_idx] + home)   # whole vector
mu  = np.exp(attack[away_idx] + defense[home_idx])
```

### Step 3: Replace scipy's scalar call with the explicit formula

The Poisson log-pmf has a simple closed form: `k·log(λ) − λ − log(k!)`. The `log(k!)` term doesn't change between optimiser iterations, so it's precomputed once:

```python
log_hg_fact = gammaln(hg + 1.0)   # precomputed, constant

# inside the objective:
ll_home = hg * np.log(lam) - lam - log_hg_fact   # vectorised
```

### Step 4: Vectorise the Dixon-Coles correction with masks

The four low-score corrections become boolean-masked array assignments instead of per-row branching:

```python
tau = np.ones_like(lam)
tau[m00] = 1.0 - lam[m00] * mu[m00] * rho
tau[m10] = 1.0 + mu[m10] * rho
tau[m01] = 1.0 + lam[m01] * rho
tau[m11] = 1.0 - rho
```

---

## Verifying it's the same model

A fast wrong answer is worthless. First check: correctness, not speed. Fitting both versions on the same small dataset:

```
slow fit: 2.05s   fast fit: 0.01s

Attack params (team: slow vs fast):
  Brazil   +0.4040  +0.4040  diff=1.87e-07
  Germany  +0.2614  +0.2614  diff=1.07e-07
  France   -0.0192  -0.0192  diff=1.22e-07
  Chile    -0.6461  -0.6461  diff=1.72e-07
home_adv: slow=0.1620 fast=0.1620
rho:      slow=0.1710 fast=0.1710
```

The parameters agree to ~1e-7 — pure floating-point optimiser noise. Same model, computed differently.

---

## Numerical hardening

Moving to the full dataset surfaced a second problem. With 300 teams — many minor national sides with only a handful of matches — the optimiser occasionally probes extreme parameter values, and two things blow up:

1. **`exp()` overflow** — a large linear predictor sends expected goals to infinity.
2. **`log(tau)` of a non-positive number** — the Dixon-Coles τ can go negative when `rho` is large, and `log` of that is undefined (NaN).

Both existed in the original code too, just silenced rather than handled. The fix keeps the objective finite everywhere so the optimiser gets a usable value and steers back toward the valid region:

```python
# Overflow guard: clip the linear predictor before exp()
eta_home = np.clip(attack[home_idx] + defense[away_idx] + home, -10.0, 10.0)
lam = np.exp(eta_home)

# Floor tau so log() is always defined
tau = np.clip(tau, 1e-10, None)
ll = np.sum(w * (np.log(tau) + ll_home + ll_away))
```

Validated under `numpy.seterr(all="raise")` — which turns any numerical warning into a hard error — the full fit now completes with zero warnings.

---

## Caching: fit once, reuse forever

Even at ~10 seconds, there's no reason to refit on every run. `fast_poisson` adds simple pickle-based caching:

```python
save_model(model, "data/dc_model.pkl")   # after fitting
model = load_model("data/dc_model.pkl")  # instant on later runs
```

The prediction script checks for the cache first and only fits if it's missing. Day-to-day use is effectively instant.

---

## The result

| | Original `fit()` | `fit_fast()` |
|---|---|---|
| 12k-match fit | 10+ hours (killed) | **~9.4 seconds** |
| Numerical stability | silent NaNs | clean under strict checking |
| Parameters | — | identical to ~1e-7 |
| Re-runs | full refit | instant (cached) |

A roughly **3,000× speedup** from changing the shape of the computation, not the machine it runs on.

The lesson: when something is catastrophically slow, profile the algorithm before reaching for more compute. A pure-Python `iterrows()` loop inside an optimiser's inner objective is a structural problem. Pushing the work down into vectorised NumPy turned an overnight job into a 10-second one.

In Part 6, we finally use this to generate an actual World Cup prediction — and look honestly at what the numbers do and don't tell us.
