# PROPQUANT — Pre-Grid Tick Validation (HARD GATE, Monday 3 Aug 2026, first action)

**Purpose:** verify tick flags and bid/ask structure before any discovery tuning happens.
**If this fails, the declared mechanism is untestable and the sprint resets.**

This gate is recorded **before** it is run, so the outcome cannot be reinterpreted afterwards.
It does not alter the signed terms in `PREREG_TICK_SPRINT.md`; it is the operational gate that
§7.6.8 (export requirement) and the Appendix checklist item ("export script tested on small
subset") both depend on.

---

## Why this gate exists

The declared mechanism (§7.6.1) is **short-horizon order-flow imbalance continuation**. It
requires classifying each tick as **buyer-initiated** or **seller-initiated**. That classification
must come from the data. If the feed does not carry it, the mechanism cannot be tested — no amount
of parameter tuning fixes a missing input.

## The known risk, stated in advance

MT5's `MqlTick.flags` field can carry:

| Flag | Meaning | Expected on a gold CFD feed? |
|---|---|---|
| `TICK_FLAG_BID` | bid changed | **Yes** — quote feeds set this |
| `TICK_FLAG_ASK` | ask changed | **Yes** |
| `TICK_FLAG_LAST` | last-trade price changed | Uncertain |
| `TICK_FLAG_VOLUME` | volume changed | Uncertain |
| `TICK_FLAG_BUY` | **buyer-initiated trade** | **Doubtful** |
| `TICK_FLAG_SELL` | **seller-initiated trade** | **Doubtful** |

`TICK_FLAG_BUY` / `TICK_FLAG_SELL` are populated on **exchange-traded instruments with real trade
prints**. FundingPips gold is a **CFD**, and CFD feeds typically stream **quote updates, not
trades** — so there is a material chance these flags are absent or always zero.

**This is a real risk to the sprint, not a formality.** It is written down now so that a failure on
Monday is a recorded prediction, not a surprise.

---

## The test (~15 minutes, first action Monday)

Export a **1-hour slice** of discovery ticks — a few thousand ticks, e.g. 09:00–10:00 on a random
February 2026 trading day — via `Src/mt5/PQ_TickProbe.mq5` (inert: `CopyTicksRange` + Print only;
no CSV of the full window, no orders, no EA attached, no AutoTrading).

Three checks, all must pass:

1. **Bid/ask populated and sensible** — bid < ask on effectively every tick, spread distribution
   consistent with gold microstructure, no zero/negative/absurd spreads beyond a small tail.
2. **Tick flags populated and usable** — specifically, whether `TICK_FLAG_BUY` / `TICK_FLAG_SELL`
   ever appear. The probe prints a **flag histogram** over the slice.
3. **Parses cleanly** — timestamps strictly non-decreasing, `time_msc` present and granular, no
   duplicate-timestamp collapse, no export artifacts.

## Decision rule (fixed in advance)

- **All three pass** → proceed to full discovery export and the §7.6.7 descriptive pass.
- **Check 1 or 3 fails** → data-quality failure. Per §5 caveat 4, this invalidates the window.
  Stop and document.
- **Check 2 fails** (no buy/sell flags) → **the declared mechanism is untestable as written.**
  Stop. Do **not** silently substitute a proxy classification (e.g. the tick rule, or
  bid-vs-ask-update inference). A proxy is a *different mechanism* and §7.6.1 fixes the mechanism
  at declaration. The options are then T. Osodo's call, taken explicitly:
  - **(i)** Re-declare the mechanism with a pre-registered proxy classification, restarting the
    §7.6 declaration — sprint clock resets.
  - **(ii)** Declare the tick angle untestable on this feed and go to the Section 10 failure path.

  Either way the substitution is a **recorded decision**, never a quiet workaround.

---

## Outcome (to be filled Monday 3 Aug, before any tuning)

- Slice tested: _______________________
- Tick count: _______________________
- Check 1 (bid/ask sane): _______________________
- Check 2 (buy/sell flags present): _______________________
- Check 3 (parses cleanly): _______________________
- **Verdict:** _______________________
