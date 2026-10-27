---
title: "Building a World Cup Prediction Model — Part 7: Fixing the Favourite"
---

[Part 6](/World_Cup_prediction_model_part6/) produced the first real prediction, and a suspicious one. The model made Japan the favourite at 11.6% and sent four-time champion Germany home in the group stage. The simulator wasn't broken. It was faithfully passing along a strength estimate from a Dixon-Coles model with two known blind spots: it weighted every match equally, and it had no sense of strength of schedule.

This part covers the fixes. None were cosmetic, and one taught me never to tune a model by squinting at its output.

---

## Fix 1: Which competitions count

The first blind spot was easy to name. A friendly is basically a training session. A World Cup knockout is the opposite. Treating them the same lets a team inflate its rating with easy friendly wins.

The fix was to weight each match in the likelihood by importance, using tiers mapped to the actual tournament labels in the data:

| Tier | Weight | Examples |
|------|--------|----------|
| World Cup finals | 6.0 | FIFA World Cup |
| Continental finals | 3.5 | Euro, Copa América, AFCON, Nations League |
| Qualifiers | 2.5 | World Cup / Euro qualification |
| Other competitive | 2.0 | Minor cups |
| Friendlies | 1.0 | Friendly |

The weights are normalized to a mean of 1 so the overall likelihood scale doesn't move, then combined with the existing time-decay weights inside `fit_fast()`.

Teams that show up in big tournaments rose. Friendly specialists fell.

| Team | Before | After importance weighting |
|------|--------|---------------------------|
| Argentina | 9.2% | 11.9% ↑ |
| Morocco | 6.9% | 11.1% ↑ |
| England | 3.0% | 5.5% ↑ |
| Japan | 11.6% | 12.5% |

That helped, but Japan didn't fall. Importance weighting fixes *which matches* count, not *who you played*. The deeper bias survived.

---

## Fix 2: Which opponents count

This was the real reason for Japan. The model had no idea that the European and South American qualifying pools are far deeper than Asia's. Japan piles up goals against weaker AFC teams; Germany grinds through strong UEFA opposition. The model read Germany's smaller goal difference as weakness.

The fix is a confederation-strength multiplier. Each team maps to its FIFA confederation, and each match is weighted by the average strength of the two confederations involved.

| Confederation | Strength |
|---------------|----------|
| UEFA (Europe) | 1.00 |
| CONMEBOL (South America) | 1.00 |
| CAF (Africa) | 0.65 |
| CONCACAF (N./C. America) | 0.60 |
| AFC (Asia) | 0.50 |
| OFC (Oceania) | 0.35 |

A result against a soft confederation now counts for less. You can't climb the ratings by beating up a weak region.

| Team | + Importance | + Confederation |
|------|--------------|-----------------|
| Japan | 12.5% (1st) | 11.1% (lost top spot) |
| Morocco | 11.1% | 14.7% (now 1st) |
| Argentina | 11.9% | 10.8% |
| **Brazil** | 6.2% | **4.8%** ⚠️ |

Japan dropped and lost the favourite tag, as intended. But Brazil fell to 9th, behind Switzerland and England. Why would a strength-of-schedule fix hurt a CONMEBOL team that gets full weight?

Because CONMEBOL has only 10 members, and they play each other constantly in a brutal round-robin qualifier. Confederation weighting keeps those tough South American results at full strength while discounting Brazil's easy friendly wins. So Brazil's draws and losses in qualifying now dominate its rating. The correction over-penalized the region it was supposed to favour.

---

## Stop eyeballing, start backtesting

Here's the trap. Every time I nudged the weights, the favourite changed:

- No weighting → **Japan**
- + importance → **Japan** (stronger)
- + confederation → **Morocco**, with Brazil suspiciously low

It was whack-a-mole. Each hand-tuned weight fixed one implausible result and created another. `UEFA = 1.0`, `AFC = 0.5`, `importance = 6.0` were all guesses, justified only by "the output looks more reasonable now."

That's not modelling. It's curve-fitting to my own intuition about who should win.

The fix was structural: stop picking weights by hand. I added two magnitude knobs (`importance_alpha` and `confederation_alpha`, each in [0, 1]) and built a **backtesting grid search** that scores each configuration by its Brier score on the 2014, 2018, and 2022 World Cups. Lower Brier means better-calibrated predictions on tournaments that actually happened.

```python
for imp_alpha, conf_alpha in grid:
    brier = mean_brier_over([2014, 2018, 2022])
# pick the config that predicted the past best
```

Instead of asking "does Brazil look right?", I ask "which weights would have best predicted the last three World Cups?" **The data decides, not my gut.**

The search is running as I write this. Part 8 will report what it picked.

---

## Fix 3: The wrong tournament shape

A sharper problem came up next. The simulator was built for the old **32-team** format (8 groups → Round of 16 → QF → SF → Final). The 2026 World Cup has **48 teams**.

That's a different bracket:

- **12 groups of 4** instead of 8
- Top 2 from each group (24) **plus the 8 best third-placed teams** = 32 qualifiers
- A new **Round of 32** before the Round of 16

So `simulate.py` got third-place ranking (points, then goal difference), a generic single-elimination runner for any bracket size, standard seeding for the Round of 32, and a new `p_r32` column. The simulator detects the format from the number of groups, so the old 32-team logic and its tests still work unchanged. Stage sums come out exact: 32 → 16 → 8 → 4 → 2 → 1, with 16 teams out in the group stage.

One caveat. The official 2026 Round of 32 uses a fixed slotting chart where your path depends on which group you won. I use standard strength-based seeding instead, because the exact chart depends on which third-place groups qualify (a 495-row lookup). For a probability forecast that's a reasonable simplification. Matching FIFA's exact paths could be a follow-up.

---

## Fix 4: The wrong teams

The bracket in the prediction script was a placeholder, a rough copy of the 2022 groups with teams in the wrong places and one duplicate. Once the real 2026 draw was out, plugging it in surfaced the unglamorous but essential work of **name normalization**. The model only knows a team if the spelling matches `results.csv`:

| Draw label | Dataset spelling |
|------------|------------------|
| Korea Republic | South Korea |
| Czechia | Czech Republic |
| Côte d'Ivoire | Ivory Coast |
| Cabo Verde | Cape Verde |
| Türkiye | Turkey |
| USA | United States |

The nastiest trap: Group K listed "Congo," but the playoff path was *Congo DR / Jamaica / New Caledonia*. So it's **DR Congo** (Kinshasa), a different country from the Republic of the Congo (Brazzaville). Both exist as separate teams in the data. Picking the wrong one would quietly feed the model another nation's entire history. I mapped it to DR Congo and added a check that all 48 teams resolve to a real team in the data and a known confederation, so a future typo fails loudly instead of quietly degrading the prediction.

---

## Where this leaves things

Going into the final run, the model is very different from Part 6:

- ✅ Matches weighted by **competition importance**
- ✅ Matches weighted by **strength of schedule** (confederation)
- ✅ Those weights about to be **chosen by backtesting**, not by hand
- ✅ The correct **48-team / Round of 32** structure
- ✅ The **official 2026 draw**, with names and confederations validated

Whether this produces a sensible favourite, or just a differently surprising one, is still open. I won't know until the backtest picks the weights and I run it on the real groups.

If the result holds up, Part 8 is the payoff. If it doesn't, that's a finding too. A well-built pipeline that still can't tame the bias would mean the fix lies in the model itself (the planned Elo + XGBoost ensemble), not its weights. Either way, unlike Part 6, I'll be able to say *why* I trust the number, because it's measured against three real World Cups, not just because it looks right.
