# PROPQUANT — Data Inventory (Gate 0, part 1)

Scan date: 2026-07-28. Machine: Osodo's Mac (MT5 runs under Wine).

## Best source found: `FundingPips-SIM1` server (inside the Wine MT5 install)
This is the challenge environment itself — symbol names, spreads, and contract specs match
what the funded account will trade. All four target instruments are present under the
correct FundingPips names (NAS100 is called **NDX100** here).

Path: `~/Library/Application Support/net.metaquotes.wine.metatrader5/drive_c/Program Files/MetaTrader 5/Bases/FundingPips-SIM1/`

| Instrument | Bar history (years on disk) | Tick data | Assessment |
|---|---|---|---|
| EURUSD | 2014–2026 (~12 yr) | 1 month (202607) | Strong — full funnel possible |
| XAUUSD | 2019–2026 (~7 yr) | Feb–Jul 2026 (184 MB) | Strong — full funnel possible |
| GBPJPY | 2024–2026 (~2.5 yr) | minimal | Thin — first look only |
| NDX100 (NAS100) | 2024–2026 (~2.5 yr) | minimal | Thin — first look only |

Data is in MT5 binary `.hcc` (bars) / `.tkc` (ticks) format — must be exported to CSV before
Python can use it.

## Secondary source: verified EURUSD CSV from Phoenix
`AigentForce/PHOENIX/Data/EURUSD_H1_201801020100_202607211800.csv` — H1, 2018-01-02 → 2026-07-21,
53,160 rows, with `.provenance.md` and `.sha256`. Raw MT5 export header
(`<DATE> <TIME> <OPEN> <HIGH> <LOW> <CLOSE> <TICKVOL> <VOL> <SPREAD>`).
Known limitations recorded in its provenance (460 non-1h intervals; 42.7% zero-spread rows —
attribution open; broker/server/offset UNKNOWN pending operator input). Usable as a
cross-check against a fresh FundingPips-SIM1 export.

## Implication for the funnel
- EURUSD and XAUUSD have the depth to reach Gate 4 with a trustworthy pass-rate number.
- GBPJPY and NDX100 currently cannot — ~2.5 yr covers too few market regimes. Options:
  1. Attempt to extend history from the FundingPips server via the terminal (may be capped).
  2. Proceed on EURUSD + XAUUSD first; treat GBPJPY/NDX100 as candidates pending more data.
- Every exported CSV gets a provenance record (broker, server, MT5 build, export method,
  server↔UTC offset) and a checksum before any research runs on it. UNKNOWN fields stay
  UNKNOWN until the operator supplies them — not inferred.

## Not yet done (next actions, pending Osodo's go-ahead)
- Export clean CSVs for the four instruments (1H + 4H) from FundingPips-SIM1.
- Run a Gate-0 integrity validator (gaps, OHLC sanity, timezone, tick-spec) on each.
- Record the server↔UTC offset (critical: the 4% daily reset is 00:00 UTC+3).
