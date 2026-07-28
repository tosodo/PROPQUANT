# PROPQUANT — Project Brief

**Source:** Mistral "Vibe" chat (Quant Trading System Design for Prop Firm Challenge),
relayed by Osodo T (project lead) on 2026-07-28. Original chat is private; content
pasted in as text.

**Provenance note:** The Mistral thread produced (a) a rules extraction, (b) a system
design, (c) illustrative Python/MQL5 code, and (d) *claimed* backtest / Monte-Carlo
results. Items (a) and (b) are useful and captured below. Item (d) — the win rates,
pass rates, drawdown figures, and earnings projections — were **not produced by any
real backtest**; no data was loaded or run. They are treated here as hypotheses to be
tested, NOT as evidence. See `Research/` for what actually gets validated.

---

## Objective
Build a rule-compliant quantitative trading system to pass the **FundingPips 2-Step Flex**
prop-firm challenge, optimised for a **$50,000 account**, targeting the **95% reward split**.

Deliverable target: deployment-ready — design → validated strategy → MQL5 EA that compiles
clean and passes real-tick backtests → risk caps wired to the exact challenge limits →
copied into MT5, ready for Osodo to attach at the terminal. (Claude compiles and copies;
Claude never attaches an EA or enables AutoTrading.)

## Account & target
- Account size: **$50,000**
- Reward split: **95%** (needs 3 profitable days ≥ 0.5% = $250/day, per 14-day cycle)

## Challenge rules — 2-Step Flex (to be re-verified against the live FundingPips page)

### Phases
| Phase | Profit target | Min trading days (95% split) | Loss limits |
|---|---|---|---|
| 1 | 10% ($5,000) | 3 profitable days | 4% daily, 12% max |
| 2 | 6% ($3,000) | 3 profitable days | 4% daily, 12% max |

### Hard breaches (immediate closure)
- **Max loss 12%** — static floor: Starting Balance × 0.88 = **$44,000**. Equity (incl. floating P&L) may not touch it.
- **Daily loss 4%** — baseline = max(opening balance, opening equity) at 00:00 UTC+3; floor = baseline × 0.96.
- **Risk per trade idea** — 2% for accounts > $25K = **$1,000** (Master Account only). Combined realized + unrealized on same instrument + same direction, incl. 10-minute rule.
- **Inactivity** — no fully-closed trade in 30 days.

### Soft breaches (restriction, not closure) — Master Account
- **News trading** — no open/close within the high-impact news window (Forex Factory red).
- **Weekend holds** — not allowed on Master (auto-closed).
- **Profit concentration** — single trade idea > 60% of phase target ($3,000 in Phase 1) → 4 profitable days required per reward.

### Trading conditions
- Leverage: Forex 1:100, Metals 1:30, Energies/Indices 1:20/1:10, Crypto 1:2.
- Commission: Forex/Metals $5/lot, Crypto 0.04%.
- Lot cap: 20 lots (1 lot crypto). Dynamic leverage on Master for Metals/Energies/Indices.

## Proposed strategy (from Mistral — to be validated, not assumed)
- Hybrid: trend-following (EMA 50/200 on 1H+4H + MACD>0 + RSI>50) plus mean-reversion (Bollinger).
- Risk per trade: 0.75% ($375). SL 1.5×ATR. TP ~1:1.2.
- Diversify 3–5 uncorrelated instruments (EURUSD, GBPJPY, XAUUSD, NAS100).
- Optional: PPO reinforcement-learning agent as a later optimisation layer.

## Success metrics (targets, to be proven in `Research/`)
Win rate > 65%, profit factor > 1.5, max DD < 4% daily / < 12% total, phase pass > 90%, breach rate < 1%.

## Open items to confirm with Osodo
1. Which FundingPips account variant/number this maps to (Standard vs Swap-Free MT5 — changes leverage & commission).
2. Instrument decision: single instrument first (cleaner to validate) vs multi-instrument from the start.
3. Whether the RL/PPO layer is in scope for v1 or deferred until a rule-based edge is proven.
