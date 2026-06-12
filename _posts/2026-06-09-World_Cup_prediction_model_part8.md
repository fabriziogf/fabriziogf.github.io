---
title: "Building a World Cup Prediction Model — Part 8: Why It Still Doesn't Make Sense"
---

[Part 7](/World_Cup_prediction_model_part7/) ended on a cliffhanger. We'd stopped hand-tuning the model's weights and handed the decision to a backtest, letting Brier score on the 2014/2018/2022 World Cups pick the best configuration. The grid search returned its verdict, we baked it in, and ran the final prediction against the official 2026 draw.

Here's what the principled, backtest-validated model produced:

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

Time to be blunt: **this still doesn't make sense.** And the most important thing to do is say exactly why — because the reasons point directly at what to build next.

---

## The reality check

You don't need to be a statistician to see the problem. You just need to follow football.

| | Model says | Football reality |
|---|---|---|
| **Favourite** | Japan (12.9%) | A strong side, but a clear favourite over Argentina, France, Spain, Brazil? No serious forecast has Japan first. |
| **Brazil** | 7th, 4.7% | Perennial top-3 contender. 4.7% and behind Ecuador is indefensible. |
| **France** | 8th, 4.4% | 2022 finalists with arguably the deepest squad in the world. |
| **England** | 21st, 1.8% | Euro 2020 *and* 2024 finalists. 21st is absurd. |
| **Algeria** | 9th, 4.1% | A good African side — ahead of Germany, Netherlands, and England? |
| **Ecuador** | 6th, 4.8% | A solid team rated above Brazil and France. |

The backtest didn't fix the Japan problem — it made it worse. Recall from Part 7 that match-importance weighting had been suppressing Japan while lifting Morocco and Argentina. The backtest found that importance weighting **hurts** predictive accuracy and switched it off — which let Japan climb back to the top, higher than before.

That's the crucial clue. When the most rigorous, data-driven version of your model endorses the least plausible answer, the problem isn't the tuning. **The problem is the model.**

---

## Why the model believes this

### Dixon-Coles only sees goals

The entire model reduces each team to two numbers — an attack rating and a defense rating — fitted purely from goals scored and conceded. It has no concept of a possession-dominant 1-0 win, a heroic goalless draw away to a giant, a depleted squad, or a dead-rubber. A team that runs up the score looks strong; a team that wins efficiently looks ordinary.

- **Japan** scores freely and concedes little, including genuinely great results (they beat Germany and Spain at the 2022 World Cup). The model has no way to discount the inflation from a schedule full of AFC opponents beyond a crude confederation multiplier.
- **England** grind out cautious 1-0 wins. A goals-hungry model systematically underrates low-scoring winners — hence 21st.
- **Brazil** get dragged down by CONMEBOL's brutal 10-team round-robin qualifier, where even the best teams draw and lose regularly. Those results count at full weight, and the model reads a 0-0 in La Paz as evidence of weakness rather than a normal night in South American qualifying.

### A single strength axis can't capture "who you beat"

Confederation weighting was our attempt at a strength-of-schedule correction, and it helped — but only at the coarsest possible granularity. Within a confederation, the model still treats thrashing the weakest team identically to beating the strongest. There's no opponent-by-opponent adjustment, because a two-parameter generative model has nowhere to put that information.

### The metric we optimised is nearly blind to the thing we care about

This is the subtle one. We tuned for **Brier score on individual match outcomes** and improved it by 2.3%. But match-outcome Brier is dominated by the many lopsided group games where almost any reasonable model scores well. The identity of the eventual champion is a tiny, high-variance signal buried in that average.

A configuration can post the best Brier score while still ranking the wrong team first. Optimising match calibration doesn't optimise the champion ranking — and we were quietly hoping it would. It didn't, and it was never going to. A better evaluation would score the model on its tournament-level output against actual World Cup finishes, not just per-match outcomes.

### Reweighting a bad axis is still a bad axis

Everything in Parts 6 and 7 — importance weighting, confederation weighting, backtest tuning — reweighted *which matches* inform the fit. None of it changed *what the model measures*. We kept polishing a single goals-based number. You can weight the inputs perfectly and still get a poor answer if the underlying feature is too thin to express team strength.

---

## What this tells us to build

The diagnosis writes the prescription. We need a strength signal that's opponent-adjusted by construction, and a model that can combine many features instead of one. The project already has both designed.

### Elo — opponent-adjusted by construction

The Elo system doesn't care how many goals you score. It cares who you beat. Every result transfers rating points between teams in proportion to how surprising the outcome was, weighted by match importance. Strength of schedule is baked in automatically: beating a 1900-rated side earns far more than thrashing a 1300-rated one, with no hand-set confederation table required.

Elo would rate Brazil, France, and England far more sensibly than a goals-based model. And it's already built, tested, and sitting unused in the prediction path.

### XGBoost — many features, learned weights

The [feature pipeline from Part 2](/World_Cup_prediction_model_part2/) was built for exactly this moment. Instead of a single attack/defense number, an XGBoost classifier can learn from:

- `elo_diff` — the opponent-adjusted strength gap
- `form_home` / `form_away` — recent results, exponentially weighted
- `rest_days` — fixture congestion
- `h2h_home_winrate` — historical matchups
- `tournament_weight`, `is_neutral` — context

A gradient-boosted model learns how to weight these from data, rather than us guessing multipliers. Crucially, it can discover that Elo difference matters far more than raw goal totals — the exact correction Dixon-Coles can't make.

### A better way to judge it

When we wire in the ensemble, we should evaluate it not only on per-match Brier but on its **tournament-level** output: does the champion ranking pass the football-fan smell test, and how does it score against the actual winners of 2014/2018/2022? The [evaluator from Part 3](/World_Cup_prediction_model_part3/) gives us the backtesting harness. We just need to point it at the right target.

---

## The honest takeaway

We built a pipeline that is fast (Part 5), correct in structure (Part 4), and rigorously tuned (Part 7). Every piece of engineering is sound. And it still confidently tells us Japan will win the World Cup ahead of Brazil, France, and England.

That's not a failure — it's the most valuable result in the whole series. It demonstrates cleanly that **good engineering and principled tuning can't rescue a model whose core feature is too weak.** No amount of reweighting goals will teach a model that England's cautious 1-0 wins are worth more than Japan's flattering goal difference. For that, you need a different signal entirely.

So we stop tuning, and we change the model. Next: the Elo + XGBoost ensemble — and a real test of whether a richer feature set finally produces a favourite you'd actually put money on.
