# PROPQUANT Gold Tick Microstructure Sprint — Pre-Registration

**Project:** PROPQUANT
**Objective:** Discover and validate a profitable gold tick microstructure edge, deployable for FundingPips 2-Step Flex challenge
**Sprint Window:** Monday, August 3, 2026 → Wednesday, August 5, 2026 (EOB UTC+3)
**Account Target:** FundingPips 2-Step Flex, $50,000
**Status:** LOCKED AND SIGNED 2026-07-29. No edits after signature.

---

## Section 1: The Question

Does a real, tradeable, cost-robust microstructure edge exist in gold tick data that can
survive out-of-sample transfer and generate sufficient edge to support a Phase 1 (+10%) and
Phase 2 (+6%) pass under FundingPips' actual drawdown constraints (4% daily loss, 12%
maximum loss)?

---

## Section 2: Data Windows (Locked)

**Discovery Window (tuned once, code frozen by Tuesday EOD):**
- **Broker/Feed:** FundingPips SIM1 (challenge broker)
- **Period:** February 5, 2026 – April 30, 2026 (~2.8 months)
- **Data Type:** Tick-level bid/ask (MT5 `.tkc` format, raw ticks not resampled)
- **Constraint:** All threshold tuning, all hypothesis formation, *only* on this window.
  Validation window untouched until Wednesday.

**Validation Window (evaluated exactly once, Wednesday EOD):**
- **Broker/Feed:** FundingPips SIM1 (same broker, same account, continuous time series)
- **Period:** May 1, 2026 – July 26, 2026 (~2.9 months, exact end date confirmed at export)
- **Constraint:** Evaluation only. No refitting, no post-hoc optimization. Touched exactly
  once, at end of day Wednesday.

**Post-hoc Bonus (non-gating, gratuitous robustness check only):**
- **Broker/Feed:** PUPrime-Live 6 (`XAUUSD.s` symbol, different contract spec from FundingPips)
- **Period:** December 2025 + January 2026 (~2 months)
- **Status:** Run *only* after verdict is locked on FundingPips windows. Cannot rescue or kill
  the result. Used only to calibrate confidence.

---

## Section 3: Primary Success Criteria (Binary, Honest, Non-negotiable)

An edge passes if **all three** of the following hold:

**1. Net Positive Expectancy After Costs (Run A — Baseline)**
- Measure: Cumulative net P&L on the validation window (May 1 – Jul 26, FundingPips)
- Costs included: observed bid/ask spread from tick data (no modeled spread), $5/lot
  round-turn commission, 1-tick adverse slippage on entry and exit (modeled as cost, not luck)
- **Threshold: Net P&L > 0 after all costs**
- If this fails, the edge is dead; the remaining criteria are moot.

**2. Net Positive Expectancy Under Cost Stress (Run B — +50% Spread Widening)**
- Measure: Same validation window, same logic, but bid/ask spread multiplied by 1.5× around mid
- Costs: same commission ($5/lot), same slippage (1 tick adverse)
- **Threshold: Net P&L > 0 under stressed spread**
- Rationale: If the edge disappears when spreads widen by 50%, the edge is living on bid-ask
  bounce, not signal. If it survives, the signal is real.
- Diagnostic: Both Run A passing and Run B failing tells us something true ("edge is
  microstructure bounce"). Both passing is stronger.

**3. Out-of-Sample Transfer (Temporal, Within-Broker)**
- **Discovery:** Feb 5 – Apr 30, 2026 (tuned once, code frozen by Tuesday EOD)
- **Validation:** May 1 – Jul 26, 2026 (evaluation Wednesday, touched exactly once)
- **Test:** Does the *exact same logic, no refitting* applied to May–Jul generate positive
  expectancy?
- **Threshold: Validation P&L > 0** (even if smaller than discovery; degradation is expected;
  zero or negative is failure)
- Rationale: When we trade live, we fit on recent history (Feb–Apr) and bet it holds into near
  future (May–Jul). This OOS test simulates that exact condition.
- Caveat: Both windows are 2026, one macro regime (gold's bull run). This test proves
  structural robustness within a regime, not across regimes. Regime robustness only comes from
  live trading and later PUPrime bonus check.

---

## Section 4: Secondary Success Criteria (Magnitude, Interpretation, Deployment Feasibility)

If all three primary criteria pass, evaluate magnitude:

**4. Phase 1 Pass Probability (Monte Carlo)**
- Method: Take the per-trade P&L distribution from the validation window. Bootstrap paths,
  each of which runs trades until one of three outcomes: **(a) reaches +10% profit, (b)
  encounters a single day with ≥4% loss, or (c) encounters cumulative loss ≥12%**. Include a
  generous cap at 2,000 trades (sufficient to cover ~12–15 weeks of realistic trading, well
  beyond a Phase 1 phase). Run 10,000 such paths.
- Risk constraint: Size each trade so worst-day intraday floating loss in the validation
  backtest ≤ 2.5% (leaving 1.5% cushion before the 4% daily breach).
- Measure: **Fraction of paths reaching +10% before breaching (4% daily or 12% max)**. Also
  report **median number of trades and calendar days to pass Phase 1 across all passing paths**.
- **Threshold: P(Phase 1 pass) ≥ 60%**
- Rationale: 60% pass rate means the edge is solid, not a one-shot outlier. Below 60%, even if
  primary criteria pass, we're relying on luck to pass Phase 1. Median trades/days tells us the
  realistic time frame.

**5. Phase 2 Pass Probability (Conditional Monte Carlo)**
- Method: From paths that passed Phase 1 (in criterion 4), continue the simulation for another
  2,000 trade cap, applying the same per-trade distribution and sizing.
- Measure: **Fraction of Phase-1-passing paths that also reach +6% in Phase 2 without exceeding
  drawdown limits**. Also report **median trades/days to pass Phase 2 conditional on Phase 1 pass**.
- **Threshold: P(Phase 2 | Phase 1 passed) ≥ 70%**
- Rationale: Phase 2's lower target (6% vs 10%) should be easier. 70% conditional pass rate is
  conservative and realistic.

**6. Median Monthly Net Return (Scalability Sanity Check)**
- Method: Compute rolling 30-day windows on the validation period; report the median.
- Costs: Same as primary (actual spread, $5/lot, 1-tick slippage).
- **Threshold: Median rolling-30-day return ≥ 3% net**
- Rationale: A strategy that barely squeaks through Phase 1 (+10% over, say, 100 days =
  0.1%/day) won't sustain the Master Account. We need evidence of consistent, deployable edge,
  not a one-off path.

**7. Annualized Sharpe Ratio (Risk-Adjusted Sanity Check)**
- Method: Aggregate each day's net P&L (all trades on day D), compute daily returns; annualize.
- Formula: Sharpe = (mean daily return × 252) / (std dev daily return × √252)
- **Threshold: Sharpe ≥ 2.0**
- Note: This is weighted lightly on a ~2.9-month validation window. Daily Sharpe estimates are
  noisy. Use as corroboration, not proof.

**8. Maximum Intraday Floating Loss (Daily Risk Containment)**
- Method: Track peak-to-trough intraday loss on each day during validation.
- **Threshold: Worst-day floating loss < 2.5%** (this is already baked into the Monte Carlo
  sizing, but we report it to confirm sizing held in backtest)
- Hard stop: If any day breaches 4% loss in the validation backtest, the strategy fails on this
  criterion alone (it violates the challenge's hard daily limit in backtest; live it will
  certainly breach).

**9. Peak-to-Trough Drawdown (Total Risk)**
- Method: Maximum cumulative loss from any previous peak to any subsequent trough during
  validation window.
- **Threshold: < 6%** (leave 6% margin before the 12% hard floor; gives room for live slippage
  and regime noise)
- Reported both relative (% of account) and absolute ($) to confirm $50k → $47k floor is safe.

---

## Section 5: What This Design Does NOT Prove (Explicit Caveats)

1. **Regime Robustness:** All data is 2026, one macro regime (gold's bull run). The temporal OOS
   test (Feb–Apr → May–Jul) proves robustness to overfitting on Feb–Apr; it does not prove
   survival of a regime change (e.g., gold crashes or gold ranges). Regime robustness requires
   live trading and later testing on PUPrime's Dec 2025–Jan 2026 window (post-hoc bonus).

2. **Broker Independence:** The FundingPips-only test does not prove cross-broker robustness. It
   proves the edge survives temporal transfer on a single broker. PUPrime bonus (if run) can add
   confidence on broker independence, but it is not a gating criterion.

3. **Latency Realism:** This backtest does not model network latency, order-queue position, or
   market-impact slippage beyond the modeled 1-tick adverse. A real deployment must also pass
   latency and execution testing before live deployment. Backtest Pass → Live Pilot (paper
   trading on FundingPips SIM1) → then real money.

4. **Data Contamination:** We are *not* claiming the tick data is free from lookahead bias,
   multi-threading errors, or data-export artifacts. A cursory audit (tick count, bid/ask
   validity, spread distribution) will be performed; explicit data-quality issues invalidate the
   result.

---

## Section 6: Measurement, Analysis, and Reporting

**Primary Analysis Spine:**
- Cumulative equity curve (validation window, May 1 – Jul 26)
- Daily P&L (each bar a day's net trades)
- Maximum drawdown vs. $50k account (absolute dollars)
- Cost decomposition: gross P&L, spread cost, commission cost, slippage cost (each line-item)

**Secondary Reporting:**
- Monte Carlo Phase 1 / Phase 2 pass probabilities, with median trades/days to pass
- Median + worst rolling-30-day net return (and the calendar-month cross-check for
  fund-manager readability)
- Annualized Sharpe (daily returns)
- Worst-day intraday floating loss
- Peak-to-trough drawdown (relative % and absolute $)

**Failure Analysis (if edge does not pass):**
- Which primary criterion failed? (Run A, Run B, or OOS transfer)
- Diagnostic: if Run A passes but Run B fails, the edge is likely microstructure bounce. If OOS
  fails, the edge overfit on discovery. If all fail, the hypothesis (tick scalp on gold) is not
  yielding alpha in this data.
- Interim report (option 2): document findings, move to next hypothesis or pause PROPQUANT.

---

## Section 7: Integrity Constraints (The Rules That Keep It Honest)

1. **Discovery Window is Locked Monday–Tuesday:** All threshold tuning, indicator parameter
   selection, and strategy formation *only* on Feb 5 – Apr 30. By end of Tuesday, the code is
   frozen and no further changes are permitted.

2. **Validation Window is Touched Exactly Once, Wednesday EOD:** May 1 – Jul 26 is evaluated
   *only at the end of day Wednesday*. No mid-sprint "just checking the OOS" plots, no peeking,
   no partial runs. One evaluation, one verdict.

3. **Hard Stop: Wednesday, August 5, EOB UTC+3:** The sprint ends. All three primary criteria
   must pass by this time to advance to secondary reporting and Monte Carlo analysis. If any
   primary criterion fails, the sprint ends and findings are documented.

4. **Cost Assumptions are Fixed:** Bid/ask from data (not modeled), $5/lot commission (read from
   FundingPips ticket), 1-tick adverse slippage (not optimized). If actual FundingPips fills
   differ, we'll know in live pilot; backtest uses these fixed assumptions.

5. **Both Parties Sign Before Data is Touched:** Once signatures are affixed, the discovery and
   validation code is written and locked. No mid-sprint "one more idea" or goalpost drift.

---

## Section 8: Sprint Timeline (Actual)

| Day | Task | Owner | Gate |
|---|---|---|---|
| **Monday, Aug 3** | Export discovery ticks (Feb 5 – Apr 30) to CSV. Backtest harness ready. Begin hypothesis formation and threshold tuning on discovery data only. | Claude / T. Osodo | Discovery locked for strategy ideas by EOD. |
| **Tuesday, Aug 4** | Complete strategy tuning on discovery. Finalize code. Freeze strategy (no further changes). Prepare validation harness. | Claude / T. Osodo | Code frozen EOD. Validation window remains untouched. |
| **Wednesday, Aug 5** | Export validation ticks (May 1 – Jul 26) to CSV. Run backtest exactly once on validation window. Compute all primary criteria (Run A, Run B, OOS transfer). Generate report. | Claude / T. Osodo | All verdicts locked by EOD. |
| **Wednesday EOB** | **HARD STOP.** Decision: pass all primary → proceed to secondary/Monte Carlo. Fail any → document, write interim report, pause or pivot. | T. Osodo | Sprint ends. |

---

## Section 9: Success Path (If Primary Criteria Are Met by Wednesday EOB)

1. **Wednesday evening:** Secondary metrics computed (Monte Carlo, Sharpe, rolling monthly,
   drawdown). Full report written.
2. **Thursday morning:** Both parties review findings and sign addendum confirming edge passes
   all primary and secondary criteria.
3. **Following Monday (Aug 10):**
   - Paper trading on FundingPips SIM1 (no real money, challenge account constraints enforced by
     risk engine).
   - Execution audit: measure latency, slippage, fill quality vs. backtest assumption.
   - Live pilot decision: if paper trading holds up, schedule live deployment.
4. **Post-sprint (if desired):** Run the exact same logic on PUPrime Dec–Jan window (bonus
   cross-broker test) to add confidence, but this does not gate the decision.

---

## Section 10: Failure Path (If Primary Criteria Are Not Met by Wednesday EOB)

1. **Wednesday EOB:** Sprint ends. Findings documented.
2. **Thursday morning:** Interim report written explaining which primary criterion failed and
   diagnostic reasoning.
3. **Decision:**
   - **Option A:** Try a genuinely different hypothesis (e.g., momentum on a different asset,
     different timeframe).
   - **Option B:** Pause PROPQUANT, resume after Phoenix is complete, with more data/regime
     coverage.
   - **Option C:** Archive PROPQUANT (if conviction is low that a tick edge exists on gold at all).

---

## Section 11: Signatures & Commitment

By signing below, both parties commit to:
- Running only the discovery window (Feb 5 – Apr 30) for tuning, with code frozen by Tuesday EOD.
- Evaluating validation (May 1 – Jul 26) exactly once, Wednesday EOD.
- Respecting the hard stop (EOB Wednesday, August 5).
- Not moving goal posts or redefining success criteria mid-sprint.
- Reporting all findings honestly, including negative results.

**Senior Dev / Research Lead (Claude, Opus via Claude Code):**

> I have reviewed the 2-Step Flex rules (10% Phase 1 + 6% Phase 2, 4% daily, 12% max loss,
> $5/lot metals commission, no per-trade limit in phases). I have reviewed the on-disk tick
> inventory (FundingPips Feb 5 – Jul 26, PUPrime Dec 2025 – Jan 2026 with symbol `XAUUSD.s`).
> I understand the discovery/validation split, the cost runs, the Monte Carlo interpretation,
> the hard stop, and the integrity constraints. I commit to this sprint as written, with no
> edits after signature.

**Signature:** ✔ Claude (Opus), via Claude Code — Senior Dev / Research Lead
**Date:** 2026-07-29

---

**Project Lead (T. Osodo):**

> I own the success bar. I've set it as: net edge survives costs (Run A), survives cost stress
> (Run B), and transfers OOS (temporal, May–Jul). I've committed the interpretation (Monte Carlo
> Phase 1/2 pass probability) and the hard stop (Wednesday EOB, Aug 5). I understand this is a
> binary test: the tick edge either exists, or it doesn't. I'm signing this pre-reg locked, and
> I will not move it.

**Signature:** ________
**Date:** 2026-07-29

---

## Appendix: Pre-Sprint Checklist

- [ ] Calendar verified: sprint is Mon Aug 3 – Wed Aug 5, 2026 (EOB UTC+3)
- [ ] Data inventory verified: FundingPips Feb 5 – Apr 30 (~2.8 mo), May 1 – Jul 26 (~2.9 mo); PUPrime Dec 2025 – Jan 2026 (`XAUUSD.s`)
- [ ] Data export script (read FundingPips `.tkc` → CSV) tested on small subset, read-only, no EA attached
- [ ] Risk engine (`pq_risk.py`) confirmed in correct state (`is_master=False` for phase testing, cost assumptions hardcoded, $5/lot commission, 1-tick slippage baked in)
- [ ] Backtest harness ready (can ingest tick CSV, run strategy, output daily P&L, compute Sharpe, flag 4%/12% breaches)
- [ ] Discovery window locked from edits by Tuesday EOD
- [ ] Validation window locked until Wednesday EOD
- [ ] Both signatures affixed before Monday sprint start
