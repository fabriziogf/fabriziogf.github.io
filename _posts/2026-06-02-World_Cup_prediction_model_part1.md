---
title: "Building a World Cup Prediction Model — Part 1: The Tournament Simulator"
---

I've wanted to know what it takes to make a principled prediction about a football tournament. Not the pundit version, with vibes, narrative, and "they have the squad depth," but the statistical one: given how these teams have performed historically, what are the actual odds that Brazil wins the World Cup?

It takes more infrastructure than most people expect. This is Part 1 of a series on how I'm building it.

---

## The project and why it's hard

The goal is a system that takes a 32-team World Cup bracket, simulates the whole tournament thousands of times, and outputs probabilities: how likely each team is to win, reach the final, make the semis, and so on.

The simulation loop isn't the hard part. Simulating a tournament realistically means predicting individual matches. That needs a credible model of team strength, which in turn needs principled decisions about how to weight 150 years of football history. Brazil vs. Germany in 1970 is technically in the record. How much should it inform a prediction about 2026?

These questions aren't trivial, and the answers directly affect prediction quality.

My approach combines two well-established statistical frameworks: **Elo ratings**, a simple continuous measure of team strength, and the **Dixon-Coles Poisson model**, which estimates full scoreline distributions. On top of both sits a **Monte Carlo tournament simulator** that runs the bracket 100,000 times and tallies probabilities at every stage.

The data is the [Kaggle International Football Results dataset](https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017): 49,412 international matches from 1872 to today.

---

## The two prediction models

### Elo ratings

Elo is a rating system originally built for chess. Every team starts with a base rating. After each match, points move from the loser to the winner in proportion to how surprising the result was. A strong team beating a weak one barely changes anything. A weak team beating a strong one moves things a lot.

Three design choices matter:

**K-factor by match importance.** Not every match should move ratings equally. A World Cup final should count for more than a friendly six months before a tournament. I use FIFA's weights: K=60 for World Cup matches, down to K=10 for friendlies.

**Home advantage.** When a match isn't at a neutral venue, I add 100 Elo points to the home team's effective rating before computing win probabilities. That roughly matches the observed home advantage in international football.

**Zero-sum updates.** The winner gains exactly what the loser drops. Total Elo stays constant, so ratings reflect relative strength, not accumulated wins.

### Dixon-Coles Poisson model

Elo gives one number per team. Dixon-Coles gives a full probability distribution over scorelines.

The model treats goals as Poisson random variables. For a match between team *i* and team *j*, expected goals are:

```
λ = exp(attack_i + defense_j + home_advantage)   # expected home goals
μ = exp(attack_j + defense_i)                     # expected away goals
```

Each team has two learned parameters, attacking strength and defensive weakness, fit by maximum likelihood across all historical matches. Older matches are down-weighted with exponential time decay, so recent form counts more than results from five years ago.

Pure Poisson models have one known problem in football: they underestimate low scores. 0-0 and 1-1 draws happen more often than Poisson predicts. The Dixon-Coles correction adjusts those specific scorelines.

The main output the simulator needs is `predict_knockout(team_a, team_b)`: in a neutral-venue elimination match, what's each team's chance of winning? It comes from building the full scoreline matrix, every combination from 0 to 10 goals, and summing the right cells.

---

## The tournament simulator

The simulator runs 100,000 full tournaments and counts how often each team reaches each stage.

### Pre-computing win probabilities

The biggest design decision was to **pre-compute every pairwise win probability before the simulation loop starts**.

32 teams make 32×31 = 992 ordered pairs. Each `predict_knockout()` call builds a full scoreline matrix. Doing that inside the loop would mean 992 matrix builds × 100,000 simulations, nearly 100 million scoreline computations. Far too slow.

Instead, `_build_win_prob_cache()` runs once and stores all 992 probabilities in a dictionary. Every match during simulation is then one random draw against a cached float. The full 100,000-run simulation finishes in seconds.

### Group stage

Each group plays a full round-robin (6 matches for 4 teams). For each match, the simulator draws against the cached win probability. A 25% bucket is reserved for draws, so results can be win, draw, or loss. Teams get the standard 3/1/0 points. Tiebreakers use an approximate goal difference plus a random noise term for exact ties.

The top two in each group advance.

### Knockout rounds

Standard World Cup seeding: group winners face runners-up from the neighboring group. Four rounds run in order (Round of 16, quarter-finals, semi-finals, final), all using `predict_knockout()` at a neutral venue with no draws.

I caught one bug during development. An early version skipped the semi-finals entirely and jumped from quarter-final winners straight to a two-team final. The symptom was subtle: every team in Groups G and H showed a 0% chance of winning, because their side of the bracket fed into a round that was never played. Adding the semi-final stage explicitly fixed it.

### Mid-tournament updates

The simulator has a `simulate_from_current()` method that takes a DataFrame of matches already played. When simulating a group, any match in that DataFrame uses the real score instead of a random draw. That lets the model update live as results come in, which is the end goal.

---

## Validation

Before trusting any probabilities, I checked that the simulator was internally consistent:

| Check | Expected | Result |
|-------|----------|--------|
| Championship probabilities sum | 1.0 | ✅ 1.0 |
| Final probabilities sum | 2.0 | ✅ 2.0 |
| Semi-final probabilities sum | 4.0 | ✅ 4.0 |
| Quarter-final probabilities sum | 8.0 | ✅ 8.0 |
| Round of 16 probabilities sum | 16.0 | ✅ 16.0 |
| Group exit probabilities sum | 16.0 | ✅ 16.0 |

Every stage sums exactly. No team is double-counted or dropped in any round. No team sits at 0% or 100%, so the simulator is exploring the full space.

I ran these checks on synthetic data (all 32 teams playing each other with Poisson-distributed goals) so I didn't have to wait on the full maximum likelihood fit over 49,000 rows while debugging structure. Running on real data is next.

---

## What's next

The simulator is the foundation. The pipeline needs two more layers:

**Feature engineering.** Right now the only inputs are historical results. The next module adds context: Elo differential, form over the last 5 and 10 matches, rest days, home vs. away vs. neutral, and head-to-head record. These features feed an XGBoost layer that sits next to the Poisson model.

**Backtesting and evaluation.** A model you can't check against reality isn't useful. The evaluation module runs the full pipeline against the 2014, 2018, and 2022 World Cups and measures calibration with Brier score and log-loss. **The question isn't just whether the eventual winner got a high probability. It's whether the whole distribution was well calibrated across all 64 matches.**

Those are Parts 2 and 3.
