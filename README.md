# PROPQUANT

A quantitative trading system built to pass the **FundingPips 2-Step Flex** prop-firm
challenge on a **$50,000** account, targeting the **95% reward split**.

> **Status:** early. Rules + design captured; strategy edge **not yet validated**.
> Nothing here is proven to make money until `Research/` says so with real data.

---

## Ground rules for this project (read before adding anything)

1. **Evidence before code.** No EA is written until a mechanism is shown to have an edge
   on real historical data, out-of-sample. A good-looking equity curve on in-sample data
   is not evidence. A statistic with no mechanism behind it is not evidence.
2. **No fabricated results — ever.** Every number in `Research/` and `Reports/` must trace
   to a script in `Src/` that actually ran on real data, with the data source and date
   range stated. If it wasn't run, it doesn't get written down as a result.
   *(This project's brief was seeded from an AI chat that presented invented backtest
   numbers as real. We kept its rules; we discarded its "results". Don't reintroduce them.)*
3. **Claude never attaches the EA or enables AutoTrading.** Compiling and copying files is
   fine. Attaching to a live chart and turning on trading is Osodo's deliberate action at
   the terminal, never automated.
4. **Ask before anything irreversible or outward-facing** (push, publish, send, delete).

## Layout
```
Brief/      The project brief and its provenance
Design/     System architecture, risk rules, compliance logic
Research/   The validation funnel — what must be proven, and the results once proven
Src/        Code: backtests, strategy research, and (only once justified) the MQL5 EA
Reports/    Finished deliverables
```

## The challenge, in one screen
- **Phase 1:** +10% ($5,000). **Phase 2:** +6% ($3,000).
- **Daily loss:** 4% of the day's baseline (resets 00:00 UTC+3). **Max loss:** 12% → floor $44,000.
- **Per trade idea (Master):** max $1,000 loss (2% of $50K), incl. floating P&L + 10-min rule.
- **Inactivity:** must fully close a trade at least every 30 days.
- **Soft (Master):** no news-window trading, no weekend holds, no single idea > 60% of target.

See `Brief/brief.md` for the full rule set and `Design/` for how each rule is enforced.
