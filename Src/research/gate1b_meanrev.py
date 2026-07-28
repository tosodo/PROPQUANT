#!/usr/bin/env python3
"""
PROPQUANT — Gate 1b: test Hypothesis 001 (quiet-hours mean-reversion).

Pre-registered rule (see Research/HYPOTHESIS_001.md), NOT tuned:
  z = (close - SMA20) / ATR14
  z >= +1.0 -> SELL ;  z <= -1.0 -> BUY   (fade the overshoot)
  entry next bar open; exit at first of: revert to SMA20 (TP) / 2.0*ATR adverse stop /
  12-bar time stop. One position at a time. Net of conservative cost.

The decisive output is expectancy BY ENTRY HOUR (server clock). The mechanism predicts a
contiguous overnight block that is positive, and a London/NY block that is not. We print the
per-hour table and the mechanism won't be accepted on a single aggregate number.

Usage: .venv/bin/python Src/research/gate1b_meanrev.py Research/data
"""
import os, sys
import numpy as np
import pandas as pd

COST = {"EURUSD": 0.0001, "XAUUSD": 0.35}
SMA_N = 20
ATR_N = 14
Z_ENTRY = 1.0
ATR_STOP = 2.0
TIME_STOP = 12


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


def simulate(df, cost):
    df = df.copy()
    df["sma"] = df["close"].rolling(SMA_N).mean()
    df["atr"] = atr(df, ATR_N)
    df["z"] = (df["close"] - df["sma"]) / df["atr"]
    o = df["open"].values; h = df["high"].values; l = df["low"].values
    sma = df["sma"].values; atrv = df["atr"].values; z = df["z"].values
    hours = df.index.hour.values
    n = len(df)

    trades = []  # (entry_hour, dir, pnl_net)
    i = 1
    while i < n:
        if not np.isfinite(z[i-1]) or not np.isfinite(atrv[i-1]) or atrv[i-1] <= 0:
            i += 1; continue
        want = 0
        if z[i-1] >= Z_ENTRY:
            want = -1
        elif z[i-1] <= -Z_ENTRY:
            want = 1
        if want == 0:
            i += 1; continue
        entry = o[i]
        stop_d = ATR_STOP * atrv[i-1]
        tp = sma[i-1]  # revert-to-mean target (level at signal bar)
        if want == 1:
            sl = entry - stop_d
        else:
            sl = entry + stop_d
        j = i; pnl = None
        while j < n and (j - i) < TIME_STOP:
            if want == 1:
                if l[j] <= sl: pnl = sl - entry; break
                if h[j] >= tp: pnl = tp - entry; break
            else:
                if h[j] >= sl: pnl = sl - entry if False else entry - sl; break
                if l[j] <= tp: pnl = entry - tp; break
            j += 1
        if pnl is None:
            if j >= n: break
            pnl = (df["close"].values[min(j, n-1)] - entry) * want  # time-stop at close
        trades.append((int(hours[i]), want, pnl - cost))
        i = j + 1
    return trades


def agg(rows):
    if not rows:
        return None
    p = np.array([r[2] for r in rows])
    wins = p[p > 0]; losses = p[p <= 0]
    gl = -losses.sum()
    return dict(n=len(rows), win=len(wins)/len(rows)*100,
                pf=(wins.sum()/gl) if gl > 0 else float("inf"),
                exp=p.mean(), total=p.sum())


def main():
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "Research/data"
    for sym in ("EURUSD", "XAUUSD"):
        df = load(os.path.join(data_dir, f"PQ_{sym}_H1.csv"))
        trades = simulate(df, COST[sym])
        u = "$" if sym == "XAUUSD" else "px"
        a = agg(trades)
        print(f"\n===== {sym} H1 — Hypothesis 001 mean-reversion (cost {COST[sym]}{u}/trade) =====")
        if a:
            print(f"ALL HOURS: n={a['n']}  win={a['win']:.1f}%  PF={a['pf']:.2f}  "
                  f"exp={a['exp']:+.5f}{u}  total={a['total']:+.2f}{u}")
        print("\n  by entry hour (server clock):")
        print("   hr |    n | win%  |  PF  |  expectancy | total")
        for hr in range(24):
            s = agg([t for t in trades if t[0] == hr])
            if s:
                print(f"   {hr:2d} | {s['n']:4d} | {s['win']:4.1f} | {s['pf']:4.2f} | "
                      f"{s['exp']:+.5f}{u} | {s['total']:+8.2f}{u}")
        # contiguous-block scan: best 6-hour window by total (diagnostic, reported not fitted)
        totals = {hr: (agg([t for t in trades if t[0] == hr]) or {"total": 0})["total"] for hr in range(24)}
        best_hr, best_val = None, -1e18
        for start in range(24):
            block = [(start + k) % 24 for k in range(6)]
            v = sum(totals[hr] for hr in block)
            if v > best_val:
                best_val, best_hr = v, block
        print(f"\n  best contiguous 6h block by total: hours {best_hr} -> {best_val:+.2f}{u}")


if __name__ == "__main__":
    main()
