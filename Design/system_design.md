# PROPQUANT — System Design

This is the honest, buildable version of the architecture. It inherits the **rules and
risk structure** from the seeding brief and discards the unproven strategy claims and the
non-compiling code that came with it.

The system has two independent halves that must never be confused:

- **The compliance layer** — deterministic rule enforcement. This is knowable and correct
  in advance; it does not need "validation", it needs to be *right*. Bugs here fail the
  challenge instantly.
- **The strategy layer** — the thing that decides when to buy/sell. This is *not* known to
  work. It is a hypothesis until `Research/` proves an edge on real data.

---

## 1. Compliance layer (must be exactly correct)

| Rule | Enforcement | Trigger |
|---|---|---|
| Max loss 12% | Track equity incl. floating P&L each tick; hard floor | equity ≤ $44,000 → flat + stop |
| Daily loss 4% | Baseline = max(open balance, open equity) at 00:00 UTC+3 | equity ≤ baseline × 0.96 → flat + stop for the day |
| Per-trade-idea $1,000 (Master) | Group by instrument + direction + 10-min re-entry rule; sum realized + floating | idea loss ≥ $1,000 → close that idea |
| Inactivity 30 days | Timestamp of last fully-closed trade | force a small closed trade by day 25 |
| News window (Master) | Forex Factory high-impact (red) calendar; block open/close in window | in-window → suppress orders |
| Weekend hold (Master) | Flatten before Friday close | Friday session end → close all |
| Profit concentration | Track each idea's contribution to phase profit | single idea > 60% target → warn / diversify |

**Design stance:** the compliance layer is written and unit-tested *first*, against the
FundingPips rules, independent of any strategy. It is the safety cage. A strategy plugs
into it; it never bypasses it.

## 2. Strategy layer (hypothesis — to be proven)

Starting hypothesis inherited from the brief (this is a *candidate*, not a decision):
- Trend filter: EMA 50/200 alignment on 1H confirmed by 4H.
- Momentum gate: RSI and MACD in agreement.
- Optional mean-reversion sleeve for ranging regimes.

Every element above must earn its place in the funnel (`Research/VALIDATION_PLAN.md`).
Elements that don't improve out-of-sample results get cut. If nothing survives, we report
that honestly rather than shipping a losing EA.

Instruments in scope (validated individually, then combined): **EURUSD, GBPJPY, XAUUSD, NAS100.**

## 3. Position sizing
- Risk per trade a tunable fraction of the account (candidate 0.5–1.0%), converted to lots
  from the stop distance and the instrument's true tick value — **not** a hard-coded pip
  value. (The seeding code hard-coded $10/pip for everything; that is wrong for XAUUSD and
  NAS100 and would missize every non-EURUSD trade.)
- Every sizing calc is checked against: 20-lot cap, the per-trade-idea $1,000 limit, and
  the remaining daily-loss headroom before the order is allowed.

## 4. Execution target
- Backtesting/research: Python on real historical data (see validation plan).
- Live: an **MQL5 EA for MetaTrader 5**, written from scratch in correct MQL5 (the seeding
  file was MQL4 and will not compile). Compiled and copied by Claude; **attached by Osodo**.

## 5. What is explicitly deferred
- The **PPO / reinforcement-learning** layer. It is only worth building on top of a
  rule-based edge that already works. Until the rule-based core is validated, RL is noise.
