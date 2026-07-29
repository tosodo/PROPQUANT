# PROPQUANT — Hypothesis 001: intraday mean-reversion in quiet hours

**Pre-registered 2026-07-28, BEFORE running the test.** Written first on purpose: the
prediction below is committed in advance so we can't quietly fit the story to whatever the
data shows. This is the discipline the inherited strategy skipped.

## The question
Trend-following on EURUSD has no edge (Gate 1). Is there a *different*, economically-grounded
behaviour we can exploit instead?

## The mechanism (why an edge should exist)
Foreign-exchange order flow is not spread evenly across the day. During the London and New York
sessions, large directional institutional flow dominates — trends and breakouts can persist.
During the quiet overnight hours (late US afternoon through the Asian session, when European and
US desks are largely offline), there is little directional flow; price action is dominated by
liquidity provision and short-term inventory management. In that regime, prices that overshoot a
short-term mean tend to **revert** rather than continue, because there is no sustained flow to
push them further.

This is a structural, liquidity-based reason — not a pattern we hope repeats. It also fits a
prop challenge well: mean-reversion produces a **high win rate** (good for hitting +10%/+6%
steadily), and the tail-risk it carries is exactly what the hard stop and daily-loss cap exist
to contain.

## The rule to be tested (pre-committed, not tuned)
On H1 EURUSD:
- Deviation `z = (close − SMA(close,20)) / ATR(14)`.
- When `z ≥ +1.0` → **SELL** (fade the overshoot); when `z ≤ −1.0` → **BUY**.
- Enter at the next bar's open. Exit at the first of: price reverts to SMA20 (take profit),
  a 2.0×ATR adverse stop, or a 12-bar time stop. One position at a time. Net of conservative cost.

## The prediction (this is the falsifiable part)
The mechanism predicts **WHERE** the edge lives, not just that one number is positive:
1. Fade/reversion expectancy is **positive in the quiet overnight block** of hours.
2. Fade/reversion expectancy is **near-zero or negative during the London+NY block** — the same
   rule should *not* work when directional flow dominates.
3. The overnight block should clearly beat the active block.

A single positive total would be weak evidence (could be luck or a bull drift). A coherent
**hour-of-day structure matching the mechanism** is strong evidence, and is hard to produce by
chance. If instead expectancy is flat across all hours, or best during London/NY, the mechanism
is wrong and we reject it — no tuning to rescue it.

(Note: exact session hours depend on the still-unconfirmed server↔UTC offset. We therefore
examine the full expectancy-by-hour profile and check whether a *contiguous overnight block*
carries the effect, rather than pre-labelling hours we can't yet map precisely.)

## RESULT (2026-07-28, `Src/research/gate1b_meanrev.py`)

**EURUSD — hypothesis SUPPORTED (directionally).** The pre-registered prediction holds:
- Overnight block (server hours 0–4): positive expectancy, win 57–63%, PF up to 1.82 (hour 2).
- London/NY block (hours 12–18): negative expectancy, PF 0.75–0.91 — rule fails as predicted.
- Best contiguous 6h block by the scan = hours 0–5 (the overnight/Asian window), matching the
  mechanism. The all-hours rule still loses (PF 0.92) — the edge is *concentrated where predicted*,
  which is the whole point and much stronger than a single positive number.
- Caveat: modest size (~2–4 pips/trade net, ~60 trades/yr in the block) and this is IN-SAMPLE.
  Whether it survives out-of-sample is unknown until Gate 2.

**XAUUSD — hypothesis REJECTED.** No coherent session structure; best 6h block is negative
(−$436). Gold is too trend/news-driven for this effect. Drop mean-reversion for gold.

## Decision
Keep EURUSD quiet-hours reversion as the live candidate. Do NOT expand hour-picking by hand
(overfitting risk). Next gate = **Gate 2 walk-forward**: derive the effect on early data, test it
on later unseen data. If the overnight edge persists out-of-sample, it is real and worth building
a controlled strategy around; if it evaporates, it was in-sample luck and we reject it too.

## GATE 2 OUTCOME (2026-07-28): REJECTED — see `gate2_report.md`.
The edge was real in 2013–2019 (fixed block PF 1.46) but decayed to flat from 2020 (PF 0.98),
and the adaptive walk-forward is negative out-of-sample (PF 0.90). Alpha decay. Hypothesis 001
is closed. Not tradeable going forward.

