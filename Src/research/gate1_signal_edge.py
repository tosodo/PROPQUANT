#!/usr/bin/env python3
"""
PROPQUANT — Gate 1: does the candidate signal core have an in-sample edge?

Candidate rule (from the brief, to be judged, not assumed):
  LONG  when, on H1:  EMA50 > EMA200  AND  MACD > MACD_signal  AND  RSI > 50
                and the H4 trend agrees: H4 EMA50 > H4 EMA200
  SHORT is the mirror image.
Entry at the next H1 bar's open. Exit is an ATR bracket: stop = 1.5*ATR(14) from
entry, target = 1.2 * stop distance (the brief's ~1:1.2 R:R). One position at a
time. If a bar's range spans both stop and target, we assume the STOP fills first
(conservative). Signal is measured on the FULL series here (in-sample) — Gate 2
does the out-of-sample walk-forward; Gate 1 only asks "is there anything here at all?"

We report EXPECTANCY, PROFIT FACTOR, WIN RATE, trade count, gross and net of a
conservative per-trade cost. If the gross edge is absent, costs are moot and the
candidate dies here — which is a valid, useful outcome.

Usage: .venv/bin/python Src/research/gate1_signal_edge.py Research/data
"""
import os, sys
import numpy as np
import pandas as pd

# Conservative round-turn cost per unit price move, per instrument (spread+commission).
# EURUSD: ~1.0 pip = 0.0001.  XAUUSD: ~$0.35.  Deliberately not optimistic.
COST = {"EURUSD": 0.0001, "XAUUSD": 0.35}

ATR_MULT_SL = 1.5
RR = 1.2


def load(path):
    df = pd.read_csv(path, sep="\t")
    df.columns = ["date", "time", "open", "high", "low", "close", "tickvol", "vol", "spread"]
    df["ts"] = pd.to_datetime(df["date"] + " " + df["time"], format="%Y.%m.%d %H:%M:%S")
    df = df.set_index("ts")[["open", "high", "low", "close"]].astype(float)
    return df


def ema(s, n):
    return s.ewm(span=n, adjust=False).mean()


def rsi(s, n=14):
    d = s.diff()
    up = d.clip(lower=0).ewm(alpha=1/n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1/n, adjust=False).mean()
    rs = up / dn.replace(0, np.nan)
    return 100 - 100 / (1 + rs)


def atr(df, n=14):
    tr = pd.concat([
        df["high"] - df["low"],
        (df["high"] - df["close"].shift()).abs(),
        (df["low"] - df["close"].shift()).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def build(df):
    df = df.copy()
    df["ema50"] = ema(df["close"], 50)
    df["ema200"] = ema(df["close"], 200)
    macd = ema(df["close"], 12) - ema(df["close"], 26)
    df["macd"] = macd
    df["macd_sig"] = ema(macd, 9)
    df["rsi"] = rsi(df["close"], 14)
    df["atr"] = atr(df, 14)
    return df


def add_h4_trend(h1, h4):
    h4 = h4.copy()
    h4["h4_up"] = (ema(h4["close"], 50) > ema(h4["close"], 200))
    # align each H1 bar to the most recent completed H4 bar
    merged = pd.merge_asof(h1.sort_index(), h4[["h4_up"]].sort_index(),
                           left_index=True, right_index=True, direction="backward")
    return merged


def simulate(df, cost):
    """Single pass, one position at a time, ATR bracket exits."""
    o = df["open"].values; h = df["high"].values; l = df["low"].values
    ema50 = df["ema50"].values; ema200 = df["ema200"].values
    macd = df["macd"].values; sig = df["macd_sig"].values
    rsi_ = df["rsi"].values; atr_ = df["atr"].values
    h4up = df["h4_up"].values
    n = len(df)

    long_sig = (ema50 > ema200) & (macd > sig) & (rsi_ > 50) & (h4up == True)
    short_sig = (ema50 < ema200) & (macd < sig) & (rsi_ < 50) & (h4up == False)

    trades = []  # (dir, entry, exit, pnl_gross)
    i = 1
    while i < n:
        want = 0
        if long_sig[i-1]:
            want = 1
        elif short_sig[i-1]:
            want = -1
        if want == 0 or not np.isfinite(atr_[i-1]) or atr_[i-1] <= 0:
            i += 1
            continue
        entry = o[i]
        sl_dist = ATR_MULT_SL * atr_[i-1]
        if want == 1:
            sl = entry - sl_dist; tp = entry + RR * sl_dist
        else:
            sl = entry + sl_dist; tp = entry - RR * sl_dist
        # scan forward for first touch
        j = i
        pnl = None
        while j < n:
            if want == 1:
                if l[j] <= sl:
                    pnl = sl - entry; break
                if h[j] >= tp:
                    pnl = tp - entry; break
            else:
                if h[j] >= sl:
                    pnl = entry - sl; break
                if l[j] <= tp:
                    pnl = entry - tp; break
            j += 1
        if pnl is None:  # ran off the end
            break
        trades.append((want, entry, pnl - cost))
        i = j + 1  # flat until the bar after exit
    return trades


def stats(trades):
    if not trades:
        return None
    pnls = np.array([t[2] for t in trades])
    wins = pnls[pnls > 0]; losses = pnls[pnls <= 0]
    gross_win = wins.sum(); gross_loss = -losses.sum()
    return {
        "trades": len(trades),
        "win_rate": len(wins) / len(trades) * 100,
        "expectancy": pnls.mean(),
        "profit_factor": (gross_win / gross_loss) if gross_loss > 0 else float("inf"),
        "total": pnls.sum(),
        "avg_win": wins.mean() if len(wins) else 0.0,
        "avg_loss": losses.mean() if len(losses) else 0.0,
        "longs": sum(1 for t in trades if t[0] == 1),
        "shorts": sum(1 for t in trades if t[0] == -1),
    }


def report_line(name, s, unit):
    if s is None:
        print(f"{name:16s}  NO TRADES")
        return
    print(f"{name:16s}  n={s['trades']:5d}  win={s['win_rate']:5.1f}%  "
          f"PF={s['profit_factor']:.2f}  exp={s['expectancy']:+.5f}{unit}/trade  "
          f"total={s['total']:+.4f}{unit}  (L{s['longs']}/S{s['shorts']})")


def main():
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "Research/data"
    print("GATE 1 — in-sample signal-edge test (net of conservative costs)\n")
    for sym in ("EURUSD", "XAUUSD"):
        h1 = build(load(os.path.join(data_dir, f"PQ_{sym}_H1.csv")))
        h4 = load(os.path.join(data_dir, f"PQ_{sym}_H4.csv"))
        df = add_h4_trend(h1, h4).dropna(subset=["ema200", "atr", "h4_up"])
        cost = COST[sym]
        trades = simulate(df, cost)
        unit = "" if sym == "XAUUSD" else ""
        u = "$" if sym == "XAUUSD" else "px"
        s = stats(trades)
        print(f"--- {sym} (H1, H4-confirmed) | cost/trade={cost}{u} ---")
        report_line("ALL", s, u)
        report_line("longs only", stats([t for t in trades if t[0] == 1]), u)
        report_line("shorts only", stats([t for t in trades if t[0] == -1]), u)
        print()


if __name__ == "__main__":
    main()
