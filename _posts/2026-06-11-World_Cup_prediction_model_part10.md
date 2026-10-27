---
title: "Building a World Cup Prediction Model — Part 10: The Final Prediction, and Measuring What Matters"
---

After nine parts of building, breaking, and rebuilding, here's the model's final forecast for the 2026 World Cup. It's the Elo + gradient-boosted trees ensemble from [Part 9](/World_Cup_prediction_model_part9/), fit on 49,411 international matches and run through 100,000 Monte Carlo simulations of the official 48-team draw.

| Rank | Team | Win % | Reach final | Reach semis |
|------|------|-------|-------------|-------------|
| 1 | **Argentina** | 17.1% | 25.1% | 35.7% |
| 2 | Spain | 12.8% | 19.7% | 29.5% |
| 3 | France | 8.9% | 15.4% | 25.2% |
| 4 | Brazil | 6.7% | 12.3% | 21.5% |
| 5 | England | 4.8% | 9.7% | 18.3% |
| 6 | Portugal | 4.8% | 9.6% | 18.1% |
| 7 | Germany | 3.4% | 7.4% | 15.2% |
| 8 | Japan | 3.3% | 7.0% | 14.4% |
| 9 | Uruguay | 3.2% | 6.8% | 13.9% |
| 10 | Netherlands | 3.1% | 6.6% | 14.0% |

The reigning champions, Argentina, are favourites at 17.1%, clear of Spain and France. Brazil, England, Portugal, and Germany round out a top seven any football fan would recognize as the real contenders. The full table runs down to Curaçao at 0.004%.

*(A confession: I'm Brazilian, and after ten parts of careful work my own model has the audacity to put Argentina first and Brazil a distant fourth. I re-ran it. Several times. The seed didn't care about my feelings. Some biases you can't vectorize away.)*

A few things beyond the headline:

- **The field is wide open.** Even the favourite wins only about one time in six. At 17%, Argentina fails to lift the trophy in roughly five of every six simulated tournaments.
- **Group J is Argentina's launchpad.** Argentina has a 91.5% chance of getting out of its group, the highest in the field.
- **Group E is the toughest.** Germany (86.6% to advance) and Ecuador (83.4%) are strong, but Ivory Coast (69.2%) makes it a real fight.
- **Dark horses:** Mexico (2.9%), Colombia (2.9%), Morocco (2.8%), and Croatia (2.6%) all have real semi-final chances.

If you read [Part 6](/World_Cup_prediction_model_part6/), you'll feel the difference right away. That first prediction crowned Japan and buried England in 21st. This one needs no apology. But the more interesting story isn't what the model predicts now. It's how I know it's better, and that turned out to be the hardest problem in the project.

---

## Measuring what matters

Here's the uncomfortable truth under this series: **for most of it, I was measuring the wrong thing, and the measurement said I was doing fine.**

My main metric was Brier score on individual match outcomes. It's a respectable metric. For a *tournament* model, it's almost the wrong one. Look at how it moved:

| Improvement | Per-match Brier change |
|-------------|------------------------|
| Backtest-tuned weights (Part 7) | +2.3% |
| Elo + XGBoost ensemble (Part 9) | +3.5% |

Modest and incremental. Judging on per-match Brier alone, you'd call the ensemble a minor upgrade. You might not even ship it.

Now the same ensemble, measured on what I actually care about: the probability it gave the teams that really went deep in the 2014, 2018, and 2022 World Cups.

| Metric (averaged over three World Cups) | Dixon-Coles | Ensemble |
|------------------------------------------|-------------|----------|
| Probability on the actual champion | 4.9% | **14.6%** |
| Average rank of the actual champion | 7.7th | **3.3rd** |
| Champion log-loss | 3.07 | **2.06** |

Three times the probability on the real winner. The actual champions, Germany in 2014 and Argentina in 2022, went from 8th and 11th in the Dixon-Coles table to 2nd in the ensemble's. That's not a 3.5% improvement. It's a different class of model.

Both tables describe the same two models on the same tournaments. The only thing that changed was the question.

### Why the gap exists

Per-match Brier averages over every match in a tournament. Most are group games, and most group games are lopsided: a contender against a minnow, where any sane model already gives the favourite 80–90%. Get those roughly right and your Brier looks fine, no matter how badly you rank the eventual champion. The handful of matches that decide the trophy are a rounding error in the average.

So a model can nail the easy, plentiful predictions, miss the few hard, important ones, and per-match Brier barely moves. It rewarded Dixon-Coles for confidently beating group-stage minnows while it quietly rated Japan above Brazil.

### The lesson

This is Goodhart's law in miniature: *when a measure becomes the target, it stops being a good measure.* I spent Parts 6 and 7 tuning weight multipliers against per-match Brier and improved it by 2.3%, while the thing I cared about, the champion ranking, stayed broken. The metric was green. The model was wrong. I only caught it because the output was so implausible no metric could hide it.

The first fix wasn't a better model. It was a better **question**. Once I scored the models on champion probability, the ranking and the metric finally agreed, and the ensemble's real margin, 3×, became visible.

The discipline that matters here and well beyond football: **build the evaluation that measures your actual goal, not the one that's convenient to compute.** The per-match metric was easy and misleading. The tournament-level metric took real work (hardcoding historical brackets, simulating each one, scoring against reality), and it was the only one that told the truth.

---

## Caveats on the final number

- **No squad information.** Injuries, slumps, a manager change, a golden generation aging out: none of it is visible. The model only sees results.
- **The backtest is three tournaments deep.** The ensemble's tournament-level win is large and consistent on 2014 and 2022, but it lost the per-match Brier comparison on 2014 and was roughly level on 2018's champion. Three World Cups is a small sample.
- **17% is real uncertainty, not a hedge.** The favourite misses far more often than it wins. Treat the table as a distribution, not a tip.
- **The draw is the final 2026 allocation.** The simulator uses standard strength-based seeding for the Round of 32, an approximation of FIFA's fixed bracket chart.

---

## The arc

Ten parts ago this was an Elo class and a Poisson model. Along the way it became a study in honest engineering: a 10-hour fit cut to 10 seconds by changing the shape of a computation, not the hardware; a favourite that survived every principled tuning attempt until I changed the model itself; and a metric that flattered me until I replaced it with one that didn't.

The model now says Argentina, then Spain, then France. You can believe it or not. It's a model, with all of a model's blind spots. But for the first time in the project, I can stand behind both the number and the method.

And the most lasting lesson has nothing to do with football: **a model is only as trustworthy as the question you use to judge it.** Measure what you care about. If that's hard to measure, the difficulty is the work, not an excuse to measure something easier.
