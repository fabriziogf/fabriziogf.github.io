---
title: "Building a World Cup Prediction Model — Part 7: Fixing the Favourite"
---

[Part 6](/2026/06/11/World_Cup_prediction_model_part6/) produced the first real prediction — and a suspicious one. The model crowned Japan the favourite at 11.6% and tipped four-time champion Germany for a group-stage exit. The simulator wasn't broken. It was faithfully propagating a strength estimate from a Dixon-Coles model with two known blind spots: it weighted every match equally, and it had no notion of strength of schedule.

This part covers the fixes. None of them were cosmetic, and one of them taught a lesson about why you should never tune a model by squinting at its output.

---

## Fix 1: Which competitions count (match-importance weighting)

The first blind spot was easy to name. A friendly is a glorified training session; a World Cup knockout is the opposite. Treating them identically lets a team inflate its rating by racking up comfortable friendly wins.

The fix was to weight each match in the likelihood by its importance, using a tier scheme mapped to the actual tournament labels in the data:

| Tier | Weight | Examples |
|------|--------|----------|
| World Cup finals | 6.0 | FIFA World Cup |
| Continental finals | 3.5 | Euro, Copa América, AFCON, Nations League |
| Qualifiers | 2.5 | World Cup / Euro qualification |
| Other competitive | 2.0 | Minor cups |
| Friendlies | 1.0 | Friendly |

Normalised to mean 1 so the overall likelihood scale stays put, then folded into the existing time-decay weights inside `fit_fast()`.

Teams that show up in big tournaments rose. Friendly-merchants fell.

| Team | Before | After importance weighting |
|------|--------|---------------------------|
| Argentina | 9.2% | 11.9% ↑ |
| Morocco | 6.9% | 11.1% ↑ |
| England | 3.0% | 5.5% ↑ |
| Japan | 11.6% | 12.5% |

Helpful — but Japan didn't fall. Importance weighting fixes *which matches* count, not *who you played in them*. The deeper bias survived.

---

## Fix 2: Which opponents count (strength of schedule)

This was the real culprit behind Japan. The model had no idea that the European or South American qualifying pools are far deeper than the Asian one. Japan piles up goals against weaker AFC opposition; Germany grinds through a gauntlet of strong UEFA sides. The model read Germany's more modest goal difference as weakness.

The fix: a confederation-strength multiplier. Each team is mapped to its FIFA confederation, and every match is weighted by the average strength of the two confederations involved.

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

Japan dropped and lost the favourite tag — the intended effect. But Brazil collapsed to 9th, behind Switzerland and England. Why would a strength-of-schedule fix hurt a CONMEBOL team that gets full weight?

Because CONMEBOL only has 10 members, who play each other constantly in a brutal round-robin qualifier. Confederation weighting keeps those punishing South American results at full strength while discounting Brazil's easy friendly wins — so Brazil's draws and losses in tough qualifying now dominate its rating. The correction over-penalised the very region it was meant to favour.

---

## The meta-lesson: stop eyeballing, start backtesting

Here's the trap. Every time we nudged the weights, the favourite changed:

- No weighting → **Japan**
- + importance → **Japan** (stronger)
- + confederation → **Morocco**, with Brazil suspiciously low

We were playing whack-a-mole. Each hand-tuned weight fixed one implausible result and created another. The numbers `UEFA = 1.0`, `AFC = 0.5`, `importance = 6.0` were all guesses, justified by nothing more than "the output looks more reasonable now."

That's not modelling — it's curve-fitting to our own intuitions about who should win.

The fix was structural: stop picking weights by hand. We added two magnitude knobs (`importance_alpha` and `confederation_alpha`, each in [0, 1]) and built a **backtesting grid search** that scores every weight configuration by its Brier score on the 2014, 2018, and 2022 World Cups. Lower Brier = better-calibrated predictions against tournaments that actually happened.

```python
for imp_alpha, conf_alpha in grid:
    brier = mean_brier_over([2014, 2018, 2022])
# pick the config that predicted the past best
```

Instead of asking "does Brazil look right?", we ask "which weights would have predicted the last three World Cups most accurately?" The data arbitrates, not our gut. That's the point.

This search is running as of writing. Part 8 will report what it chose.

---

## Fix 3: The tournament was the wrong shape

A sharper problem surfaced next: the simulator was built for the old **32-team** format (8 groups → Round of 16 → QF → SF → Final). But the 2026 World Cup is **48 teams**.

That's a different bracket entirely:

- **12 groups of 4** instead of 8
- Top 2 from each group (24) **plus the 8 best third-placed teams** = 32 qualifiers
- A new **Round of 32** before the Round of 16

So `simulate.py` got third-place ranking (by points, then goal difference), a generic single-elimination runner that works for any bracket size, standard seeding for the Round of 32, and a new `p_r32` output column. The simulator now detects the format from the number of groups, so the old 32-team logic and its tests still work unchanged. Stage sums land exactly: 32 → 16 → 8 → 4 → 2 → 1, with 16 teams eliminated in the group stage.

One honest caveat: the official 2026 Round of 32 follows a fixed slotting chart where your path depends on which group you won. We use standard strength-based seeding instead, because the exact chart depends on which third-place groups qualify (a 495-row lookup). For a probability forecast that's a reasonable abstraction. Matching FIFA's exact bracket paths is a possible follow-up.

---

## Fix 4: The teams were wrong too

The bracket in the prediction script was a placeholder — a rough copy of the 2022 groups, with teams in the wrong places and a duplicate. Once the real 2026 draw was available, plugging it in surfaced the unglamorous but essential work of **name normalisation**. The model only knows a team if the spelling matches `results.csv`:

| Draw label | Dataset spelling |
|------------|------------------|
| Korea Republic | South Korea |
| Czechia | Czech Republic |
| Côte d'Ivoire | Ivory Coast |
| Cabo Verde | Cape Verde |
| Türkiye | Turkey |
| USA | United States |

The nastiest trap: Group K listed "Congo", but the qualifying playoff path was *Congo DR / Jamaica / New Caledonia* — so it's **DR Congo** (Kinshasa), a completely different country from the Republic of the Congo (Brazzaville). Both exist as separate teams in the data. Picking the wrong one would silently feed the model a different nation's entire history. We mapped it to DR Congo and added a check that all 48 teams resolve to a real team in the data and a known confederation, so a future typo fails loudly instead of quietly degrading the prediction.

---

## Where this leaves us

Going into the final run, the model is a different animal than it was in Part 6:

- ✅ Matches weighted by **competition importance**
- ✅ Matches weighted by **strength of schedule** (confederation)
- ✅ Those weights about to be **chosen by backtesting**, not by hand
- ✅ The correct **48-team / Round of 32** tournament structure
- ✅ The **official 2026 draw**, with names and confederations validated

Whether all this produces a sensible favourite — or just a differently surprising one — is still an open question. We won't know until the backtest picks the weights and we run it against the real groups.

If the result holds up, Part 8 is the payoff. If it doesn't, that's a finding too: a well-built pipeline that still can't tame the bias would tell us the fix lies in the model itself (the planned Elo + XGBoost ensemble), not its weights. Either way, the difference from Part 6 is that we'll be able to say *why* we trust the number — measured against three real World Cups — rather than just hoping it looks right.
