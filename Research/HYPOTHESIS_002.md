# PROPQUANT — Hypothesis 002: active-hours breakout momentum (gold)

**Pre-registered 2026-07-28, BEFORE running the test.**

## The mechanism (why an edge should exist)
Hypothesis 001 showed FX *reverts* in quiet hours (no directional flow). The mirror image:
during the **active London/NY hours**, large directional institutional and macro flow dominates —
and **gold** in particular moves in catalyst-driven bursts (rates, USD, risk sentiment). When
price breaks out of its recent range *while that flow is live*, the move should have short-term
**follow-through** (momentum). The same breakout during the quiet overnight hours should more
often be a false break that fades.

So the mechanism makes two directional predictions, not one:
- Breakout momentum should be **stronger on gold than on EURUSD** (gold trends; EURUSD reverts).
- Breakout momentum should be **positive in active hours** and **weak/negative in quiet hours**.

## The rule to be tested (pre-committed, not tuned)
On H1:
- Donchian breakout: BUY when close > highest high of the prior 20 bars; SELL when close <
  lowest low of the prior 20 bars.
- Enter at the next bar's open. Exit at the first of: 1.5×ATR(14) adverse stop, 3.0×ATR target
  (asymmetric R≈2 — momentum should let winners run), or a 24-bar time stop. One position at a
  time. Net of conservative cost (EURUSD 1.0 pip, gold $0.35).

## The prediction (falsifiable)
1. Gold breakout is net positive (PF > 1) after costs, concentrated in the active-hours block.
2. Active-hours block clearly beats the quiet-hours block.
3. EURUSD breakout is weaker/negative (it reverts, so breakouts fail) — a built-in control.

If gold breakout is flat/negative everywhere, or works best overnight, the mechanism is wrong
and we reject it. No tuning to rescue.

## RESULT (2026-07-28, `Src/research/gate1c_breakout.py`)

**REJECTED at Gate 1 — weak/no net edge.**
- **Gold, all hours:** win 35.8%, PF **0.99**, total −$226 over 2,116 trades — essentially
  break-even/negative (R≈2 breakeven win is ~33%; 35.8% is marginal). Prediction 1 (net
  positive) fails.
- Best contiguous 6h block IS the active window (hours 11–16, +$667) — a weak directional hint
  for prediction 2 — but it sits among large negative hours and is noisy; trading only that
  block would be the same cherry-pick that failed Gate 2 for Hyp 001. Not pursued.
- **EURUSD control:** breakout loses (PF 0.88) as predicted (it reverts) — prediction 3 holds.
  Our *understanding* is coherent; a *tradeable* gold-breakout edge is not present.

Weaker in-sample than Hyp 001 (which itself died out-of-sample). Not advanced to Gate 2.
Hypothesis 002 closed. No tuning applied.

