# PROPQUANT — Gate 1 Report (signal edge, in-sample)

Run: 2026-07-28 · `Src/research/gate1_signal_edge.py` · full-series in-sample.
Candidate: EMA50/200 trend + MACD + RSI on H1, confirmed by H4 EMA50/200 trend.
Exit: ATR(14) bracket, stop 1.5×ATR, target 1.2× stop (≈1:1.2 R:R). Net of a
conservative round-turn cost (EURUSD 1.0 pip, XAUUSD $0.35).

## Results

| Market | Trades | Win% | Profit factor | Expectancy/trade | Total | Verdict |
|---|---|---|---|---|---|---|
| **EURUSD** | 4,251 | 44.9% | **0.88** | −0.00015 px | −0.64 px | **FAIL — loses** |
| **XAUUSD** | 2,197 | 47.4% | **1.06** | +$0.34 | +$736 | Marginal (longs carry it) |
| XAUUSD longs | 1,407 | 49.0% | 1.08 | +$0.48 | +$676 | Only live thread |
| XAUUSD shorts | 790 | 44.7% | 1.01 | +$0.08 | +$60 | Effectively flat |

## Verdict: the inherited candidate signal has **no reliable edge**.

- **EURUSD: dead.** Negative expectancy, profit factor 0.88 — and this is *in-sample*, the
  most favourable possible case. Break-even win rate for a 1:1.2 payoff is 45.5%; the signal
  wins 44.9%. It loses by construction.
- **XAUUSD: marginal and untrustworthy.** Profit factor 1.06 in-sample is barely above
  break-even. A signal this thin almost never survives out-of-sample (Gate 2) or a fuller
  cost model. The only part with any life is XAUUSD **longs** during gold's long bull trend —
  which may be nothing more than "gold went up for 7 years."

## What this means (and why it's a good outcome)
This is the funnel doing its job: it killed a weak strategy **for free**, on paper, instead
of on a $50,000 challenge. It also confirms the earlier audit — the seeding brief *claimed*
"68% win rate, PF 1.5–2.2, >90% pass rate." Measured on real data: **45–47% win rate,
PF 0.88–1.06.** Those claims were fabricated, as flagged from the start.

## Honesty note
No parameters were tuned to improve these numbers. Per the project's honesty contract, we do
not tune a known-weak signal until it looks nice — that manufactures false confidence. The
result stands as measured.

## Recommended next step
Do **not** proceed to build an EA on this signal. Two legitimate paths (see chat): (a) cheaply
confirm the one marginal thread — XAUUSD longs — dies out-of-sample via a Gate-2 walk-forward,
so the rejection is evidence-based; and/or (b) return to mechanism design and form a genuine,
economically-motivated edge hypothesis before any further testing.
