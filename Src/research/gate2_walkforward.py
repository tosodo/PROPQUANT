#!/usr/bin/env python3
"""
PROPQUANT — Gate 2: walk-forward (out-of-sample) test of EURUSD quiet-hours mean-reversion.

The Gate 1b edge was found IN-SAMPLE across the whole series. Gate 2 asks the only question
that matters: does it hold on data it was NOT derived from?

Two independent views:

  (A) FIXED overnight block (server hours 0-5, pre-committed from the hypothesis):
      report expectancy split into an early half and a late half, and year by year.
      Tests TIME-STABILITY of the mechanism — did it keep working in years never used to
      form the hypothesis?

  (B) ADAPTIVE rolling walk-forward: on each training window, SELECT the hours that were
      profitable in training (net of cost, min trade count), then trade ONLY those hours in
      the next unseen year. Aggregate all out-of-sample trades. Tests whether hour-selection
      GENERALISES, and compares against trading all-hours (no selection) out-of-sample.

Same pre-registered rule as Gate 1b (unchanged, not tuned).
Usage: .venv/bin/python Src/research/gate2_walkforward.py Research/data
"""
import os, sys
import numpy as np
import pandas as pd

COST = 0.0001
SMA_N, ATR_N, Z_ENTRY, ATR_STOP, TIME_STOP = 20, 14, 1.0, 2.0, 12
FIXED_BLOCK = {0, 1, 2, 3, 4, 5}


def load(path):
    df = pd.read_csv(path, sep="\t")
    df.columns = ["date", "time", "open", "high", "low", "close", "tickvol", "vol", "spread"]
    df["ts"] = pd.to_datetime(df["date"] + " " + df["time"], format="%Y.%m.%d %H:%M:%S")
    return df.set_index("ts")[["open", "high", "low", "close"]].astype(float)


def atr(df, n):
    tr = pd.concat([df["high"] - df["low"],
                    (df["high"] - df["close"].shift()).abs(),
                    (df["low"] - df["close"].shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def gen_trades(df):
    """Return DataFrame of trades: entry_ts, hour, dir, pnl_net."""
    df = df.copy()
    df["sma"] = df["close"].rolling(SMA_N).mean()
    df["atr"] = atr(df, ATR_N)
    df["z"] = (df["close"] - df["sma"]) / df["atr"]
    o, h, l = df["open"].values, df["high"].values, df["low"].values
    c = df["close"].values
    sma, atrv, z = df["sma"].values, df["atr"].values, df["z"].values
    idx = df.index
    n = len(df)
    rows = []
    i = 1
    while i < n:
        if not np.isfinite(z[i-1]) or not np.isfinite(atrv[i-1]) or atrv[i-1] <= 0:
            i += 1; continue
        want = -1 if z[i-1] >= Z_ENTRY else (1 if z[i-1] <= -Z_ENTRY else 0)
        if want == 0:
            i += 1; continue
        entry = o[i]; stop_d = ATR_STOP * atrv[i-1]; tp = sma[i-1]
        sl = entry - stop_d if want == 1 else entry + stop_d
        j = i; pnl = None
        while j < n and (j - i) < TIME_STOP:
            if want == 1:
                if l[j] <= sl: pnl = sl - entry; break
                if h[j] >= tp: pnl = tp - entry; break
            else:
                if h[j] >= sl: pnl = entry - sl; break
                if l[j] <= tp: pnl = entry - tp; break
            j += 1
        if pnl is None:
            if j >= n: break
            pnl = (c[min(j, n-1)] - entry) * want
        rows.append((idx[i], idx[i].hour, want, pnl - COST))
        i = j + 1
    return pd.DataFrame(rows, columns=["ts", "hour", "dir", "pnl"])


def stats(p):
    p = np.asarray(p)
    if len(p) == 0:
        return None
    wins = p[p > 0]; gl = -p[p <= 0].sum()
    return dict(n=len(p), win=len(wins)/len(p)*100,
                pf=(wins.sum()/gl) if gl > 0 else float("inf"),
                exp=p.mean(), total=p.sum())


def show(tag, s, u="px"):
    if s is None:
        print(f"  {tag:28s} no trades"); return
    print(f"  {tag:28s} n={s['n']:5d}  win={s['win']:5.1f}%  PF={s['pf']:.2f}  "
          f"exp={s['exp']:+.5f}{u}  total={s['total']:+.3f}{u}")


def main():
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "Research/data"
    tr = gen_trades(load(os.path.join(data_dir, "PQ_EURUSD_H1.csv")))
    tr["year"] = tr["ts"].dt.year

    print("===== GATE 2 — EURUSD quiet-hours mean-reversion, out-of-sample =====")
    print(f"total trades generated: {len(tr)}  ({tr['ts'].min().date()} .. {tr['ts'].max().date()})\n")

    # ---- (A) FIXED overnight block: time stability ----
    print("(A) FIXED overnight block (server hours 0-5), pre-committed:")
    blk = tr[tr["hour"].isin(FIXED_BLOCK)]
    mid = pd.Timestamp("2020-01-01")
    show("all years", stats(blk["pnl"]))
    show("early (<2020, in-sample-ish)", stats(blk[blk["ts"] < mid]["pnl"]))
    show("late  (>=2020, OOS-ish)", stats(blk[blk["ts"] >= mid]["pnl"]))
    print("  year-by-year (block 0-5):")
    for y in sorted(blk["year"].unique()):
        s = stats(blk[blk["year"] == y]["pnl"])
        if s:
            print(f"     {y}: n={s['n']:3d}  win={s['win']:5.1f}%  PF={s['pf']:.2f}  total={s['total']:+.4f}px")

    # ---- (B) ADAPTIVE rolling walk-forward ----
    print("\n(B) ADAPTIVE rolling walk-forward (train 4y -> select hours exp>0 & n>=15 -> test next 1y):")
    years = sorted(tr["year"].unique())
    oos_sel, oos_all, fold_lines = [], [], []
    for test_y in range(years[0] + 4, years[-1] + 1):
        train = tr[(tr["year"] >= test_y - 4) & (tr["year"] < test_y)]
        test = tr[tr["year"] == test_y]
        if len(train) == 0 or len(test) == 0:
            continue
        # select hours profitable in TRAIN only
        good = []
        for hr in range(24):
            s = stats(train[train["hour"] == hr]["pnl"])
            if s and s["n"] >= 15 and s["exp"] > 0:
                good.append(hr)
        sel = test[test["hour"].isin(good)]
        oos_sel += list(sel["pnl"]); oos_all += list(test["pnl"])
        s_sel = stats(sel["pnl"])
        fold_lines.append(f"     {test_y}: hours={sorted(good)}  "
                          f"OOS n={0 if s_sel is None else s_sel['n']:3d} "
                          f"total={0.0 if s_sel is None else s_sel['total']:+.4f}px")
    for ln in fold_lines:
        print(ln)
    print("\n  aggregate OUT-OF-SAMPLE:")
    show("selected hours (WF)", stats(oos_sel))
    show("all hours (no selection)", stats(oos_all))

    print("\n(interpret: selected-hours OOS should beat all-hours OOS and be positive net of cost)")


if __name__ == "__main__":
    main()
