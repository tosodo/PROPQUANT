#!/usr/bin/env python3
"""
PROPQUANT — Gate 1c: test Hypothesis 002 (active-hours breakout momentum).

Pre-registered rule (Research/HYPOTHESIS_002.md), NOT tuned:
  Donchian(20) breakout: close > prior-20 high -> BUY ; close < prior-20 low -> SELL.
  entry next bar open; exit first of 1.5*ATR stop / 3.0*ATR target / 24-bar time stop.
  one position at a time; net of conservative cost.

Decisive output = expectancy by entry hour, for GOLD and (as a control) EURUSD.
Mechanism predicts: gold positive & concentrated in active hours; EURUSD weak/negative.

Usage: .venv/bin/python Src/research/gate1c_breakout.py Research/data
"""
import os, sys
import numpy as np
import pandas as pd

COST = {"EURUSD": 0.0001, "XAUUSD": 0.35}
DONCHIAN, ATR_N = 20, 14
ATR_STOP, ATR_TP, TIME_STOP = 1.5, 3.0, 24


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
    df["hh"] = df["high"].rolling(DONCHIAN).max().shift(1)   # prior-20 high (excl current)
    df["ll"] = df["low"].rolling(DONCHIAN).min().shift(1)
    df["atr"] = atr(df, ATR_N)
    o, h, l, c = (df["open"].values, df["high"].values, df["low"].values, df["close"].values)
    hh, ll, atrv = df["hh"].values, df["ll"].values, df["atr"].values
    hours = df.index.hour.values
    n = len(df)
    trades = []
    i = 1
    while i < n:
        if not np.isfinite(atrv[i-1]) or atrv[i-1] <= 0 or not np.isfinite(hh[i-1]):
            i += 1; continue
        want = 0
        if c[i-1] > hh[i-1]:
            want = 1
        elif c[i-1] < ll[i-1]:
            want = -1
        if want == 0:
            i += 1; continue
        entry = o[i]; sd = ATR_STOP * atrv[i-1]; td = ATR_TP * atrv[i-1]
        if want == 1:
            sl, tp = entry - sd, entry + td
        else:
            sl, tp = entry + sd, entry - td
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
        trades.append((int(hours[i]), want, pnl - cost))
        i = j + 1
    return trades


def agg(rows):
    if not rows: return None
    p = np.array([r[2] for r in rows]); wins = p[p > 0]; gl = -p[p <= 0].sum()
    return dict(n=len(p), win=len(wins)/len(p)*100,
                pf=(wins.sum()/gl) if gl > 0 else float("inf"), exp=p.mean(), total=p.sum())


def main():
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "Research/data"
    for sym in ("XAUUSD", "EURUSD"):
        trades = simulate(load(os.path.join(data_dir, f"PQ_{sym}_H1.csv")), COST[sym])
        u = "$" if sym == "XAUUSD" else "px"
        a = agg(trades)
        print(f"\n===== {sym} H1 — Hyp002 breakout momentum (cost {COST[sym]}{u}) =====")
        if a:
            print(f"ALL HOURS: n={a['n']}  win={a['win']:.1f}%  PF={a['pf']:.2f}  "
                  f"exp={a['exp']:+.5f}{u}  total={a['total']:+.2f}{u}")
        totals = {}
        print("  by entry hour:")
        for hr in range(24):
            s = agg([t for t in trades if t[0] == hr])
            totals[hr] = s["total"] if s else 0.0
            if s:
                print(f"   {hr:2d} | n={s['n']:4d} win={s['win']:4.1f}% PF={s['pf']:4.2f} "
                      f"exp={s['exp']:+.5f}{u} total={s['total']:+8.2f}{u}")
        best, bv = None, -1e18
        for st in range(24):
            blk = [(st + k) % 24 for k in range(6)]
            v = sum(totals[hr] for hr in blk)
            if v > bv: bv, best = v, blk
        print(f"  best contiguous 6h block: {best} -> {bv:+.2f}{u}")


if __name__ == "__main__":
    main()
