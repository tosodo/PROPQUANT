# PROPQUANT — Data Provenance (Gate 0)

Exported 2026-07-28 by `Src/mt5/PQ_ExportBars.mq5` (v1.00), run headless against the live
Wine MT5 terminal. Raw CopyRates → CSV, no post-processing. Checksums in the `.sha256`
sidecars next to each file. Files are gitignored (not committed); this record is.

| Field | Value |
|---|---|
| broker / server | **FundingPips-SIM1** (MetaTrader 5) — the challenge environment |
| account | **20184574** (same funded account as Phoenix, per operator) |
| MT5 build | 6063 |
| export method | `PQ_ExportBars.mq5` v1.00 — `CopyRates(sym, tf, 0, Bars(sym,tf))` → tab-CSV |
| export timestamp | 2026-07-28 ~18:58 (terminal/server clock) |
| terminal connected | YES (auto-connected to FundingPips-SIM1 at launch) |
| server↔UTC offset + DST | **UNKNOWN — operator to confirm.** Not inferred. The challenge's 4% daily reset is stated as 00:00 UTC+3; the FundingPips server clock is typically UTC+2/+3 with DST, but this must be confirmed before any daily-boundary logic is trusted. |
| column layout | `<DATE> <TIME> <OPEN> <HIGH> <LOW> <CLOSE> <TICKVOL> <VOL> <SPREAD>` (tab-sep) |

## Files

| File | Symbol | TF | Rows | First | Last | SHA256 (short) |
|---|---|---|---|---|---|---|
| PQ_EURUSD_H1.csv | EURUSD | H1 | 84,289 | 2012-12-27 | 2026-07-28 | 99648069… |
| PQ_EURUSD_H4.csv | EURUSD | H4 | 21,638 | 2012-12-27 | 2026-07-28 | 34e3e0e4… |
| PQ_XAUUSD_H1.csv | XAUUSD | H1 | 40,943 | 2019-08-21 | 2026-07-28 | 91c1e9e1… |
| PQ_XAUUSD_H4.csv | XAUUSD | H4 | 10,992 | 2019-08-21 | 2026-07-28 | 6e50d7c9… |

## Known limitations / still-open (feed into the Gate-0 validator)
- Timezone/DST offset UNKNOWN (above) — blocks trusting any 00:00-boundary daily logic.
- Bar-interval regularity not yet formally checked (expect weekend/holiday gaps; must confirm
  no *unexpected* intra-week gaps). To be validated, not assumed.
- OHLC sanity (high≥max(open,close)≥min≥low, no zero/negative prices) not yet machine-checked.
- Spread column present (points); recent EURUSD spreads show 1 (0.1 pip) — plausible but the
  real cost model uses commission + spread; confirm against the FundingPips cost sheet.
- GBPJPY and NDX100 (NAS100) NOT exported here — only ~2.5 yr on disk; deferred per scope decision.

## Next
Run a Gate-0 integrity validator (adapt `PHOENIX/Research/gate0/gate0_validate.py`, pure stdlib)
over these four files; record pass/fail per check. Only then does Gate 1 (signal edge) begin.
