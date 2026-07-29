# PROPQUANT — Gate 2 Report (walk-forward, out-of-sample)

Run: 2026-07-28 · `Src/research/gate2_walkforward.py` · EURUSD quiet-hours mean-reversion.

## Verdict: **FAIL — reject Hypothesis 001 as a tradeable strategy.**

The in-sample edge (Gate 1b) does NOT survive out-of-sample. It was a genuine feature of
2013–2019 markets that has decayed to nothing since ~2020.

### (A) Fixed overnight block (server hours 0–5), time-stability
| Window | Trades | Win% | Profit factor | Total |
|---|---|---|---|---|
| Early (<2020) | 381 | 60.1% | **1.46** | +0.188 px |
| Late (≥2020) | 430 | 57.0% | **0.98** | −0.007 px |

Year by year, every strong year is 2013–2017 (PF 1.1–2.4). From 2020: PF 0.73, 0.74, then
choppy — no consistency, net flat/negative. The mechanism was real but has been arbitraged away.

### (B) Adaptive rolling walk-forward (train 4y → select profitable hours → test next year)
| Out-of-sample | Trades | Win% | Profit factor | Total |
|---|---|---|---|---|
| Selected hours | 2,294 | 52.6% | **0.90** | −0.232 px |
| All hours (baseline) | 7,691 | 52.7% | 0.92 | −0.664 px |

Selection barely differs from trading blindly, and both lose. The hour-selection does not
generalise; nearly every OOS fold is negative.

## What this means
Gate 2 did its job: it caught a decayed edge before a cent was risked. Two strategies have now
been honestly falsified — the inherited trend combo (Gate 1) and this mean-reversion (Gate 2).
That is normal quant research: most hypotheses fail, and finding a *current, robust* edge in
daily-bar retail FX/metal data is genuinely hard.

## Honesty note
No parameters were re-tuned to rescue the result. A decayed edge stays rejected.

## Status
- Infrastructure (data, validators, backtest funnel, MT5 export/compile tooling) is solid and
  reusable — that investment carries forward to any future hypothesis.
- No validated edge yet. Decision on direction pending (see chat): bounded further hypotheses,
  build the deterministic risk-compliance engine in parallel, or reassess scope honestly.
