---
title: "Building a World Cup Prediction Model — Part 1: The Tournament Simulator"
---

I have been interested for a long time in what it actually takes to make a principled prediction about a football tournament. Not the pundit version — vibes, narrative, "they have the squad depth" — but the statistical version: given everything we know about how these teams have performed historically, what are the true odds that Brazil wins the World Cup?

The answer turns out to require more infrastructure than most people expect. This is Part 1 of a series documenting how I am building it.

---

## What the Project Is and Why It Is Hard

The goal is a system that, given a 32-team World Cup bracket, simulates the entire tournament thousands of times and outputs probabilities: how likely is each team to win the championship, reach the final, make the semi-finals, and so on.

The hard part is not the simulation loop itself. The hard part is that simulating a tournament realistically requires predicting individual match outcomes, which requires a credible model of team strength, which requires making principled decisions about how to weight 150 years of football history. Brazil vs. Germany in 1970 is technically in the historical record. How much should that match inform your prediction about 2026?

These are not trivial questions, and the answers have real consequences for prediction quality.

My approach combines two well-established statistical frameworks: **Elo ratings**, which give a simple continuous measure of team strength, and the **Dixon-Coles Poisson model**, which goes further and estimates full scoreline distributions. On top of both sits a **Monte Carlo tournament simulator** that runs the bracket 100,000 times and accumulates win probabilities at every stage.

The data is the [Kaggle International Football Results dataset](https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017) — 49,412 international matches from 1872 to the present.

---

## The Two Prediction Models

### Elo Ratings

Elo is a rating system originally designed for chess. The idea is simple: every team starts with a base rating, and after each match, points transfer from the loser to the winner in proportion to how surprising the result was. If a strong team beats a weak team, little changes. If a weak team beats a strong team, large transfers occur in both directions.

I made three design choices that matter:

**K-factor by match importance.** Not all matches should update ratings equally. A World Cup final should move ratings more than a friendly played six months before a tournament. I weight them the same way FIFA does: K=60 for World Cup matches, down to K=10 for friendlies. This means tournament performance drives the ratings, which is the right behavior.

**Home advantage.** When a match is not at a neutral venue, I add 100 Elo points to the home team's effective rating before computing win probabilities. This is roughly consistent with the empirical home advantage observed across international football.

**Zero-sum updates.** Points gained by the winner are exactly lost by the loser, so the total Elo in the system stays constant over time. This is a deliberate constraint — it means ratings reflect relative strength, not accumulated wins.

### Dixon-Coles Poisson Model

Elo gives you one number per team. Dixon-Coles gives you a full probability distribution over scorelines.

The model treats goals as Poisson random variables. For a match between team *i* and team *j*, the expected goals for each side are:

```
λ = exp(attack_i + defense_j + home_advantage)   # expected home goals
μ = exp(attack_j + defense_i)                     # expected away goals
```

Each team has two learned parameters — attacking strength and defensive weakness — estimated via maximum likelihood across all historical matches. Older matches are down-weighted using exponential time decay, so recent form matters more than results from five years ago.

The one known problem with pure Poisson models in football is that they underestimate low-scoring results. 0-0 and 1-1 draws happen more often than Poisson predicts. The Dixon-Coles correction adjusts the joint probability of those specific scorelines to account for this.

The main output the simulator needs is `predict_knockout(team_a, team_b)`: given two teams in a neutral-venue elimination match, what is the probability each team wins? This is derived by computing the full scoreline matrix — every possible combination of goals from 0 to 10 — and summing the appropriate cells.

---

## The Tournament Simulator

The simulator's job is mechanical but the design decisions are not. Given a bracket, it needs to run 100,000 complete tournaments and count how often each team reaches each stage.

### Performance: Pre-Computing Win Probabilities

The single biggest design decision was **pre-computing all pairwise win probabilities before the simulation loop begins**.

With 32 teams, there are 32×31 = 992 ordered pairs. Each `predict_knockout()` call builds a full scoreline matrix — roughly 100 floating-point computations per call. Doing this inside the simulation loop would mean 992 matrix builds × 100,000 simulations = nearly 100 million scoreline computations. That is very slow.

Instead, `_build_win_prob_cache()` runs once upfront and stores all 992 probabilities in a dictionary. Every match resolution during the simulation is then a single random draw against a cached float — essentially free. The entire 100,000-simulation run completes in seconds rather than hours.

### Group Stage

Each group runs a full round-robin (6 matches for 4 teams). For each match, the simulator draws against the pre-cached win probability. A 25% bucket is reserved for draws, so results can be win/draw/loss rather than binary. Teams get the standard 3/1/0 points. Tiebreakers use an approximated goal difference plus a random noise term for exact ties.

Top two teams from each group advance.

### Knockout Rounds

Standard World Cup seeding: group winners face runners-up from the adjacent group. Four knockout rounds run sequentially — Round of 16, Quarter-finals, Semi-finals, Final — all using `predict_knockout()` probabilities at a neutral venue with no draws.

One bug caught during development: an early version skipped the semi-final round entirely, jumping directly from quarter-final winners to a two-team final. The symptom was subtle — all teams from Groups G and H showed 0% championship probability, because the bracket wiring for those groups fed into a round that was never played. Fixed by explicitly adding the semi-final stage.

### Mid-Tournament Updates

The simulator supports a `simulate_from_current()` method that accepts a DataFrame of already-played matches. When simulating a group, any match found in that DataFrame uses the real scoreline instead of a random draw. This allows the model to be updated live as results come in — which is the eventual goal.

---

## Validation

Before trusting any probabilities, I need to verify the simulator is internally consistent. The sanity checks I ran:

| Check | Expected | Result |
|-------|----------|--------|
| Championship probabilities sum | 1.0 | ✅ 1.0 |
| Final probabilities sum | 2.0 | ✅ 2.0 |
| Semi-final probabilities sum | 4.0 | ✅ 4.0 |
| Quarter-final probabilities sum | 8.0 | ✅ 8.0 |
| Round of 16 probabilities sum | 16.0 | ✅ 16.0 |
| Group exit probabilities sum | 16.0 | ✅ 16.0 |

Every stage sum is exact — no teams are double-counted or dropped at any round. No team shows 0% or 100% probability, which confirms the simulator is exploring the full space rather than deterministically routing any team through the bracket.

These checks were run on synthetic data — all 32 tournament teams playing each other with Poisson-distributed goals — to avoid waiting on the full maximum likelihood fit over 49,000 rows while doing structural debugging. Running on real data is the next step.

---

## What's Next

The simulator is the foundation, but the prediction pipeline has two more layers to build:

**Feature engineering.** Right now the only inputs to the model are historical match results. The next module adds richer context for each match: Elo differential, recent form over the last 5 and 10 matches, rest days since last match, home vs. away vs. neutral, and head-to-head record. These features will feed into an XGBoost prediction layer alongside the Poisson model.

**Backtesting and evaluation.** A model that cannot be evaluated against reality is not useful. The evaluation module will run the full pipeline against the 2014, 2018, and 2022 World Cups — tournaments for which we know the results — and measure calibration using Brier score and log-loss. The question is not just whether the eventual winner had a high predicted probability, but whether the entire probability distribution was well-calibrated across all 64 matches.

I will write those up as Part 2 and Part 3.
