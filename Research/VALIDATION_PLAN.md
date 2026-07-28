# PROPQUANT — Validation Plan (the funnel)

The strategy layer must pass through this funnel before any live EA is justified. Each
gate can kill the project — that's the point. We would rather learn "no edge" here, for
free, than on a $50,000 challenge.

## Gate 0 — Data integrity (blocks everything)
- Obtain real historical price data for **EURUSD, GBPJPY, XAUUSD, NAS100**.
- Verify: no gaps beyond weekends/holidays, sane OHLC, correct timezone, correct
  contract/tick specs per instrument. Bad data → stop; no research runs on it.
- **Open dependency:** we need to confirm what data we actually have. (Repo note: the gold
  work used tick data from ~2026-02-05 onward — likely too short for a trend system. This
  must be resolved before Gate 1.)

## Gate 1 — Signal core has an edge (in-sample)
- Implement the candidate signal cleanly on 1H/4H.
- Measure on in-sample data per instrument: expectancy, profit factor, trade count,
  distribution of returns. Require a *positive, statistically non-trivial* edge before
  proceeding. A handful of lucky trades is not an edge.

## Gate 2 — Walk-forward (out-of-sample)
- Walk-forward: optimise on a window, test on the next unseen window, roll forward.
- Require the edge to survive out-of-sample with acceptable Sharpe and drawdown. Most
  retail signals die here. If it dies, that's the finding.

## Gate 3 — Robustness / stress
- Bootstrap the trade sequence and perturb parameters ±. If the result depends on an exact
  parameter or a specific trade order, it's overfit, not real.
- Regime split: does it survive both trending and ranging periods, or only one?

## Gate 4 — Challenge simulation (the real test)
- Run the *validated* signal inside the full compliance layer over many simulated
  challenge attempts, with realistic spread, commission ($5/lot fx/metals), and slippage.
- Report the honest **pass rate** for Phase 1 and Phase 2, the breach rate and *which*
  breach, and the distribution of days-to-pass. This — not any single backtest — is the
  number that matters.

## Only after Gate 4 passes
- Write the MQL5 EA, compile clean (0 errors / 0 warnings), reconcile its backtest against
  the Python result, copy into MT5. Osodo attaches it.

---

### Honesty contract
Any table of "results" in this repo names the script that produced it, the instrument, the
data source, and the date range. No result is written before its script has run. If a gate
fails, we say so plainly and stop — we do not tune until the picture looks nice.
