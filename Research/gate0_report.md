# PROPQUANT — Gate 0 Report (data integrity)

Run: 2026-07-28 · `Src/research/gate0_validate.py` (pure stdlib) over `Research/data/PQ_*.csv`.

## Verdict: **PASS** (all four series)

| Series | Rows | Span | Price range | OHLC viol. | Dupes | Out-of-order | Unexpected gaps |
|---|---|---|---|---|---|---|---|
| EURUSD H1 | 84,289 | 2012-12-27 → 2026-07-28 | 0.9536 – 1.3993 | 0 | 0 | 0 | 15 (all holidays) |
| EURUSD H4 | 21,638 | 2012-12-27 → 2026-07-28 | 0.9536 – 1.3993 | 0 | 0 | 0 | 15 (all holidays) |
| XAUUSD H1 | 40,943 | 2019-08-21 → 2026-07-28 | 1445.6 – 5597.2 | 0 | 0 | 0 | 15 (breaks/holidays) |
| XAUUSD H4 | 10,992 | 2019-08-21 → 2026-07-28 | 1445.6 – 5597.2 | 0 | 0 | 0 | 12 (holidays) |

## What the "unexpected gaps" actually are (all benign)
- **Holiday closures** — 28–80h gaps clustered on Dec 24/25 and Dec 31–Jan 4 every year. Real market closures, not missing data.
- **Gold daily break** — XAUUSD shows 2h gaps at 00:00→02:00 in the 2019 stretch: the daily CME maintenance break. Expected for metals.
- None indicate corruption; the strictly-increasing-timestamp and OHLC-sanity checks are clean.

## Observations carried forward (not Gate 0 failures)
- **Zero-spread rows:** EURUSD ~30% (25,067/84,289), XAUUSD ~7%. Older-history export artifact.
  → The cost model must NOT rely on the stored spread column for those rows; use commission
    ($5/lot fx & metals) + a realistic modelled spread. Flagged for Gate 4 cost modelling.
- **Timezone/UTC offset still UNKNOWN.** Does not block signal research (Gate 1), but blocks any
  00:00-daily-boundary logic (the 4% daily-loss reset). Confirm with operator before Gate 4.
- **zero-tickvol rows = 0** across all files — good; every bar has tick activity.

## Gate 0 → cleared for EURUSD + XAUUSD. Proceed to Gate 1 (signal edge, in-sample).
