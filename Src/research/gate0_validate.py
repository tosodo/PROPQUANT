#!/usr/bin/env python3
"""
PROPQUANT — Gate 0 integrity validator.  Pure stdlib, no dependencies.

Reads the raw MT5-export CSVs (tab-separated:
  <DATE> <TIME> <OPEN> <HIGH> <LOW> <CLOSE> <TICKVOL> <VOL> <SPREAD>)
and checks the things that would silently poison every downstream gate:

  * header matches the expected layout
  * every row parses; correct field count
  * timestamps strictly increasing (no duplicates, no out-of-order rows)
  * OHLC sanity: high >= max(open,close), low <= min(open,close), high>=low, all > 0
  * bar spacing: how many gaps equal the timeframe, how many are weekend/holiday
    gaps (expected), how many are UNEXPECTED intra-week gaps (a real problem)
  * spread / volume observations (reported, not judged)

It does NOT modify the data and does NOT infer the timezone. Verdict per file:
PASS (no integrity violations), or FAIL (violations that block research).

Usage:  python3 gate0_validate.py ../../Research/data
"""
import csv, os, sys
from datetime import datetime, timedelta

EXPECTED_HEADER = ["<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>",
                   "<CLOSE>", "<TICKVOL>", "<VOL>", "<SPREAD>"]
TF_SECONDS = {"H1": 3600, "H4": 14400}


def tf_from_name(fname):
    for tf in TF_SECONDS:
        if f"_{tf}." in fname:
            return tf
    return None


def parse_row(row):
    d, t = row[0], row[1]
    ts = datetime.strptime(f"{d} {t}", "%Y.%m.%d %H:%M:%S")
    o, h, l, c = (float(row[2]), float(row[3]), float(row[4]), float(row[5]))
    tickvol = int(row[6]); vol = int(row[7]); spread = int(row[8])
    return ts, o, h, l, c, tickvol, vol, spread


def validate(path):
    fname = os.path.basename(path)
    tf = tf_from_name(fname)
    exp = TF_SECONDS.get(tf)
    r = {"file": fname, "tf": tf, "rows": 0,
         "header_ok": False, "parse_errors": [], "ohlc_violations": [],
         "dupes": 0, "out_of_order": 0,
         "gap_exact": 0, "gap_weekend": 0, "gap_unexpected": [],
         "zero_spread": 0, "zero_tickvol": 0,
         "first": None, "last": None, "min_price": None, "max_price": None}

    with open(path, "r", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader, [])
        r["header_ok"] = (header == EXPECTED_HEADER)
        prev_ts = None
        for i, row in enumerate(reader, start=2):
            if len(row) != 9:
                if len(r["parse_errors"]) < 5:
                    r["parse_errors"].append((i, f"field count {len(row)}"))
                continue
            try:
                ts, o, h, l, c, tickvol, vol, spread = parse_row(row)
            except Exception as e:
                if len(r["parse_errors"]) < 5:
                    r["parse_errors"].append((i, str(e)))
                continue
            r["rows"] += 1
            if r["first"] is None:
                r["first"] = ts
            r["last"] = ts
            lo = min(o, c); hi = max(o, c)
            if not (h >= hi and l <= lo and h >= l and o > 0 and h > 0 and l > 0 and c > 0):
                if len(r["ohlc_violations"]) < 5:
                    r["ohlc_violations"].append((i, f"O{o} H{h} L{l} C{c}"))
            r["min_price"] = l if r["min_price"] is None else min(r["min_price"], l)
            r["max_price"] = h if r["max_price"] is None else max(r["max_price"], h)
            if spread == 0:
                r["zero_spread"] += 1
            if tickvol == 0:
                r["zero_tickvol"] += 1
            if prev_ts is not None:
                delta = (ts - prev_ts).total_seconds()
                if delta <= 0:
                    if ts == prev_ts:
                        r["dupes"] += 1
                    else:
                        r["out_of_order"] += 1
                elif exp and delta == exp:
                    r["gap_exact"] += 1
                else:
                    # crosses a weekend? (Saturday falls between prev and ts)
                    crosses_weekend = False
                    probe = prev_ts
                    steps = 0
                    while probe < ts and steps < 400:
                        if probe.weekday() == 5:  # Saturday
                            crosses_weekend = True
                            break
                        probe += timedelta(hours=1)
                        steps += 1
                    if crosses_weekend and delta <= 3 * 86400:
                        r["gap_weekend"] += 1
                    else:
                        if len(r["gap_unexpected"]) < 15:
                            r["gap_unexpected"].append(
                                (prev_ts.isoformat(), ts.isoformat(), int(delta)))
            prev_ts = ts
    return r


def verdict(r):
    fatal = []
    if not r["header_ok"]:
        fatal.append("header mismatch")
    if r["parse_errors"]:
        fatal.append(f"{len(r['parse_errors'])}+ parse errors")
    if r["ohlc_violations"]:
        fatal.append(f"{len(r['ohlc_violations'])}+ OHLC violations")
    if r["dupes"]:
        fatal.append(f"{r['dupes']} duplicate timestamps")
    if r["out_of_order"]:
        fatal.append(f"{r['out_of_order']} out-of-order rows")
    return ("FAIL", fatal) if fatal else ("PASS", [])


def main():
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    files = sorted(f for f in os.listdir(data_dir)
                   if f.startswith("PQ_") and f.endswith(".csv"))
    if not files:
        print(f"No PQ_*.csv found in {data_dir}", file=sys.stderr)
        sys.exit(2)

    any_fail = False
    for fn in files:
        r = validate(os.path.join(data_dir, fn))
        v, reasons = verdict(r)
        any_fail = any_fail or (v == "FAIL")
        span_days = (r["last"] - r["first"]).days if r["first"] else 0
        print(f"\n=== {fn}  [{v}] ===")
        print(f"  rows={r['rows']}  span={span_days}d  {r['first']} -> {r['last']}")
        print(f"  price range: {r['min_price']} .. {r['max_price']}")
        print(f"  gaps: exact={r['gap_exact']}  weekend/holiday={r['gap_weekend']}  "
              f"unexpected={len(r['gap_unexpected'])}")
        print(f"  zero-spread rows={r['zero_spread']}  zero-tickvol rows={r['zero_tickvol']}")
        if r["gap_unexpected"]:
            print("  sample unexpected gaps (prev -> next, seconds):")
            for a, b, d in r["gap_unexpected"][:8]:
                print(f"    {a} -> {b}  ({d}s = {d/3600:.1f}h)")
        if reasons:
            print(f"  FAIL reasons: {', '.join(reasons)}")
    print(f"\n===== GATE 0 {'FAIL' if any_fail else 'PASS'} =====")
    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
