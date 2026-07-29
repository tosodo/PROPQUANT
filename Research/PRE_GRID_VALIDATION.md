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

## Outcome — RUN 2026-07-29 (early, at T. Osodo's instruction)

Run ahead of the Monday slot. Legitimate: the probe computes **no outcome statistic of any kind**
(spreads, flag counts, timestamp ordering only), so it cannot bias discovery. Running early is
purely de-risking.

- **Slice tested:** XAUUSD, FundingPips-SIM1, 2026.02.11 09:00:00–09:59:59 (Wednesday, normal session)
- **Tick count:** 20,003 (~5.6 ticks/sec)
- **Check 1 (bid/ask sane):** ✅ **PASS** — 0 malformed (0.00%). Spread avg **$0.46**, min $0.20,
  max $1.09. digits=2, point=0.01.
- **Check 2 (buyer/seller classification):** ❌ **FAIL** — decisive.
  - `LAST=0`, `VOLUME=0` → **no trade prints at all.** This is a pure quote feed.
  - `BUY=20003`, `SELL=20003` of 20,003 → **both flags set on 100% of ticks.**
  - Directional separation: `buy_only=0`, `sell_only=0`, `both=20003`, `neither=0`
    → **classifiable = 0.00%** (need ≥50%).
  - Distinct raw flag values: `230` (94.63%), `226` (2.64%), `100` (2.63%), `96` (0.10%).
    Every value has bits 32 (BUY) **and** 64 (SELL) set.
- **Check 3 (parses cleanly):** ✅ **PASS** — 0 backward steps, 0 duplicate `time_msc`, 0 zero `time_msc`.
  Millisecond granularity present and monotonic. Data quality is excellent.

### VERDICT: ❌ GATE FAILED — declared mechanism is UNTESTABLE on this feed

The predicted risk materialised exactly as written above: FundingPips gold is a CFD, the feed
streams **quote updates, not trades**, and `TICK_FLAG_BUY`/`TICK_FLAG_SELL` are set on every tick
as a "both sides tradeable" marker rather than a trade-direction classification. A flag always set
in both directions carries **zero information**.

**Order-flow imbalance continuation cannot be tested on this data.** No parameter grid, and no
amount of tuning, fixes a missing input.

**Per the decision rule above, work stops here.** The tick rule (classify by uptick/downtick) and
bid-vs-ask-update inference are *proxies* — they are a **different mechanism**, and §7.6.1 fixes the
mechanism at declaration. Substituting one silently would convert a failed test into a fake pass.
The choice between (i) re-declare with a pre-registered proxy (clock resets) and (ii) Section 10
failure path is **T. Osodo's, taken explicitly.**

### Process note — probe error found and fixed

The first run **wrongly reported PASS**. The original criterion was `f_buy > 0 || f_sell > 0`,
which a degenerate both-always-set feed satisfies trivially. Corrected to require ≥50%
**directional separation** (`buy XOR sell`) and to dump the distinct raw flag histogram, then
re-run. Recorded here because a gate that can pass on a degenerate input is worse than no gate.

### Descriptive facts banked (permitted under §7.6.7, no outcome statistics)

- **Tick density:** ~20k ticks/hour in an active session — ample for microstructure work.
- **Round-trip cost floor:** spread ≈ $0.46 + commission ($5/lot ÷ 100oz = $0.05 in price) +
  1-tick slippage each side ($0.02) ≈ **$0.53 per round trip**. Any tick strategy must predict a
  move larger than this to be viable. Worth knowing before choosing any successor mechanism.
