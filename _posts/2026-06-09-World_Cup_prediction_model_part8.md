---
title: "Building a World Cup Prediction Model — Part 8: Why It Still Doesn't Make Sense"
---

[Part 7](/World_Cup_prediction_model_part7/) ended on a cliffhanger. I'd stopped hand-tuning the model's weights and let a backtest pick them, using Brier score on the 2014, 2018, and 2022 World Cups. The grid search returned its answer, I baked it in, and ran the final prediction on the official 2026 draw.

Here's what the backtest-validated model produced:

| Rank | Team | Win % |
|------|------|-------|
| 1 | **Japan** | **12.9%** |
| 2 | Morocco | 7.6% |
| 3 | Argentina | 7.5% |
| 4 | Spain | 7.1% |
| 5 | Portugal | 5.2% |
| 6 | Ecuador | 4.8% |
| 7 | Brazil | 4.7% |
| 8 | France | 4.4% |
| 9 | Algeria | 4.1% |
| 10 | Switzerland | 3.7% |
| 21 | England | 1.8% |

To be blunt: **this still doesn't make sense.** The most useful thing I can do is say exactly why, because the reasons point straight at what to build next.

---

## Reality check

You don't need to be a statistician to see the problem. You just need to follow football.

| | Model says | Football reality |
|---|---|---|
| **Favourite** | Japan (12.9%) | A strong side, but a clear favourite over Argentina, France, Spain, Brazil? No serious forecast has Japan first. |
| **Brazil** | 7th, 4.7% | Perennial top-3 contender. 4.7% and behind Ecuador is indefensible. |
| **France** | 8th, 4.4% | 2022 finalists with arguably the deepest squad in the world. |
| **England** | 21st, 1.8% | Euro 2020 *and* 2024 finalists. 21st is absurd. |
| **Algeria** | 9th, 4.1% | A good African side — ahead of Germany, Netherlands, and England? |
| **Ecuador** | 6th, 4.8% | A solid team rated above Brazil and France. |

The backtest didn't fix the Japan problem. It made it worse. In Part 7, match-importance weighting had been holding Japan down while lifting Morocco and Argentina. The backtest found that importance weighting **hurts** predictive accuracy and turned it off, which let Japan climb back to the top, higher than before.

That's the key clue. When the most rigorous, data-driven version of your model backs the least plausible answer, the problem isn't the tuning. **The problem is the model.**

---

## Why the model believes this

### Dixon-Coles only sees goals

The model reduces each team to two numbers, an attack rating and a defense rating, fit purely from goals scored and conceded. It knows nothing about a controlled 1-0 win, a hard-earned draw away at a giant, a depleted squad, or a dead rubber. A team that runs up the score looks strong. A team that wins efficiently looks ordinary.

- **Japan** scores freely and concedes little, including some great results (they beat Germany and Spain at the 2022 World Cup). Beyond a crude confederation multiplier, the model can't discount the inflation from a schedule full of AFC opponents.
- **England** grinds out cautious 1-0 wins. A goals-hungry model consistently underrates low-scoring winners, hence 21st.
- **Brazil** gets dragged down by CONMEBOL's brutal 10-team round-robin qualifier, where even the best teams draw and lose regularly. Those results count at full weight, and the model reads a 0-0 in La Paz as weakness instead of a normal night in South American qualifying.

### One strength axis can't capture who you beat

Confederation weighting was my attempt at a strength-of-schedule correction. It helped, but only at the coarsest level. Within a confederation, the model still treats thrashing the weakest team the same as beating the strongest. There's no opponent-by-opponent adjustment, because a two-parameter model has nowhere to put that information.

### The metric I optimized barely sees what I care about

This one is subtle. I tuned for **Brier score on individual match outcomes** and improved it by 2.3%. But match-level Brier is dominated by the many lopsided group games where almost any reasonable model does well. Who wins the tournament is a tiny, high-variance signal buried in that average.

A configuration can post the best Brier score and still rank the wrong team first. Optimizing match calibration doesn't optimize the champion ranking. I was quietly hoping it would, and it was never going to. A better evaluation would score the model's tournament-level output against actual World Cup results, not just per-match outcomes.

### Reweighting a bad axis is still a bad axis

Everything in Parts 6 and 7 (importance weighting, confederation weighting, backtest tuning) changed *which matches* inform the fit. None of it changed *what the model measures*. I kept polishing one goals-based number. You can weight the inputs perfectly and still get a poor answer if the underlying feature is too thin to express team strength.

---

## What to build

The diagnosis writes the prescription. I need a strength signal that adjusts for opponents by design, and a model that combines many features instead of one. The project already has both designed.

### Elo: opponent-adjusted by design

Elo doesn't care how many goals you score. It cares who you beat. Every result moves points between teams in proportion to how surprising it was, weighted by match importance. Strength of schedule comes for free: beating a 1900-rated side earns far more than thrashing a 1300-rated one, no confederation table needed.

Elo would rate Brazil, France, and England much more sensibly than a goals-based model. And it's already built, tested, and sitting unused in the prediction path.

### XGBoost: many features, learned weights

The [feature pipeline from Part 2](/World_Cup_prediction_model_part2/) was built for this. Instead of a single attack/defense number, an XGBoost classifier can learn from:

- `elo_diff` — the opponent-adjusted strength gap
- `form_home` / `form_away` — recent results, exponentially weighted
- `rest_days` — fixture congestion
- `h2h_home_winrate` — historical matchups
- `tournament_weight`, `is_neutral` — context

A gradient-boosted model learns how to weight these from data instead of me guessing multipliers. Most importantly, it can learn that Elo difference matters far more than raw goal totals, the exact correction Dixon-Coles can't make.

### A better way to judge it

When the ensemble is wired in, I should judge it not just on per-match Brier but on its **tournament-level** output: does the champion ranking pass the football-fan smell test, and how does it score against the actual winners of 2014, 2018, and 2022? The [evaluator from Part 3](/World_Cup_prediction_model_part3/) already provides the backtesting harness. It just needs to point at the right target.

---

## Takeaway

I built a pipeline that's fast (Part 5), structurally correct (Part 4), and carefully tuned (Part 7). The engineering is sound. And it still confidently says Japan will win the World Cup ahead of Brazil, France, and England.

That's not a failure. It's the most useful result in the series. It shows clearly that **good engineering and principled tuning can't rescue a model whose core feature is too weak.** No amount of reweighting goals will teach a model that England's cautious 1-0 wins are worth more than Japan's flattering goal difference. That takes a different signal.

So I'm done tuning. Next I change the model: the Elo + XGBoost ensemble, and a real test of whether richer features finally produce a favourite you'd actually bet on.
