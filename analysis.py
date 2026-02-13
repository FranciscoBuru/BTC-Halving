import pandas as pd
import numpy as np
import math

FILE_NAME = "./btc-usd-max.csv"
DATE_INDEX = "snapped_at"
PRICE = "price"

# Halving dates
DATE0 = "2012-11-28"
DATE1 = "2016-07-09"
DATE2 = "2020-05-11"
DATE3 = "2024-04-19"
# Expected next halving (~April 2028)
DATE4 = "2028-04-15"

DAYS_BEFORE = 180
DAYS_AFTER = 530


def read_file(name):
    data = pd.read_csv(name)
    data = data[[DATE_INDEX, PRICE]]
    data[DATE_INDEX] = pd.to_datetime(data[DATE_INDEX])
    df = data.set_index([DATE_INDEX])
    df1 = df[:DATE1]
    df2 = df[DATE1:DATE2]
    df3 = df[DATE2:DATE3]
    df4 = df[DATE3:]
    return df1, df2, df3, df4


def cycle_stats(df, label, peak_cutoff=None):
    """peak_cutoff: optional date string to cap where we look for the ATH
    (e.g. cycle 3 peaked Nov 2021, not in the 2024 pre-halving rally)"""
    min_p = df[PRICE].min()
    min_date = df[PRICE].idxmin()
    if peak_cutoff:
        df_peak = df[:peak_cutoff]
    else:
        df_peak = df
    max_p = df_peak[PRICE].max()
    max_date = df_peak[PRICE].idxmax()
    mult = max_p / min_p
    return {
        "label": label,
        "min": min_p,
        "max": max_p,
        "mult": mult,
        "min_date": min_date,
        "max_date": max_date,
    }


def days_after_halving(halving_date, event_date):
    return (event_date.tz_localize(None) - pd.Timestamp(halving_date)).days


def main():
    df1, df2, df3, df4 = read_file(FILE_NAME)

    halvings = [DATE0, DATE1, DATE2, DATE3]
    labels = ["Cycle 1 (2012-2016)", "Cycle 2 (2016-2020)", "Cycle 3 (2020-2024)", "Cycle 4 (2024-now)"]
    # Cycle 3 peaked Nov 2021, cap before the 2024 pre-halving rally
    peak_cutoffs = [None, None, "2022-06-01", None]
    dfs = [df1, df2, df3, df4]

    stats = []
    for df, label, h_date, cutoff in zip(dfs, labels, halvings, peak_cutoffs):
        s = cycle_stats(df, label, peak_cutoff=cutoff)
        s["halving_date"] = h_date
        s["days_to_min"] = days_after_halving(h_date, s["min_date"])
        s["days_to_max"] = days_after_halving(h_date, s["max_date"])
        stats.append(s)

    # --- Cycle Stats ---
    print("=" * 60)
    print("  BTC HALVING CYCLE ANALYSIS")
    print("=" * 60)

    for s in stats:
        print(f"\n  {s['label']}")
        print(f"    Min:  ${s['min']:>12,.2f}  (day {s['days_to_min']:>4} after halving)")
        print(f"    Max:  ${s['max']:>12,.2f}  (day {s['days_to_max']:>4} after halving)")
        print(f"    Mult: {s['mult']:.2f}x")

    # --- Peak-to-peak multipliers ---
    print("\n" + "=" * 60)
    print("  PEAK-TO-PEAK MULTIPLIERS")
    print("=" * 60)

    peak_mults = []
    for i in range(1, len(stats)):
        m = stats[i]["max"] / stats[i - 1]["max"]
        peak_mults.append(m)
        print(f"  Cycle {i} → {i+1}:  {m:.2f}x")

    # --- Days to peak ---
    print("\n" + "=" * 60)
    print("  DAYS TO PEAK AFTER HALVING")
    print("=" * 60)

    days_to_peaks = []
    for s in stats:
        days_to_peaks.append(s["days_to_max"])
        print(f"  {s['label']}:  {s['days_to_max']} days")

    # --- Days before/after halving price comparison ---
    print("\n" + "=" * 60)
    print(f"  PRICE {DAYS_BEFORE} DAYS BEFORE vs {DAYS_AFTER} DAYS AFTER HALVING")
    print("=" * 60)

    for i in range(1, len(dfs)):
        prev_df = dfs[i - 1].reset_index(drop=True)
        curr_df = dfs[i].reset_index(drop=True)
        if len(prev_df) >= DAYS_BEFORE and len(curr_df) > DAYS_AFTER:
            price_before = prev_df[PRICE].iloc[-DAYS_BEFORE]
            price_after = curr_df[PRICE].iloc[DAYS_AFTER]
            mult = price_after / price_before
            print(f"\n  {stats[i]['label']}:")
            print(f"    {DAYS_BEFORE}d before: ${price_before:>12,.2f}")
            print(f"    {DAYS_AFTER}d after:  ${price_after:>12,.2f}")
            print(f"    Multiplier:   {mult:.2f}x")

    # --- Projections for Cycle 5 ---
    print("\n" + "=" * 60)
    print("  CYCLE 5 PROJECTIONS")
    print("=" * 60)

    ln_mults = [math.log(m) for m in peak_mults]

    # Method 1: Log decay ratio
    ratios = [ln_mults[i + 1] / ln_mults[i] for i in range(len(ln_mults) - 1)]
    avg_ratio = np.mean(ratios)
    next_ln = ln_mults[-1] * avg_ratio
    m1 = math.exp(next_ln)
    p1 = stats[-1]["max"] * m1

    # Method 2: Square root
    m2 = math.sqrt(peak_mults[-1])
    p2 = stats[-1]["max"] * m2

    # Method 3: Log differences decay
    ln_diffs = [ln_mults[i + 1] - ln_mults[i] for i in range(len(ln_mults) - 1)]
    if len(ln_diffs) >= 2:
        diff_ratio = ln_diffs[-1] / ln_diffs[-2]
        next_diff = ln_diffs[-1] * diff_ratio
        next_ln3 = ln_mults[-1] + next_diff
    else:
        next_diff = ln_diffs[-1] * 0.38
        next_ln3 = ln_mults[-1] + next_diff
    m3 = math.exp(next_ln3)
    p3 = stats[-1]["max"] * m3

    print(f"\n  Current cycle 4 peak: ${stats[-1]['max']:,.2f}")
    print(f"  Peak-to-peak multipliers: {' → '.join(f'{m:.2f}x' for m in peak_mults)}")
    print(f"  ln(multipliers): {' → '.join(f'{l:.3f}' for l in ln_mults)}")

    print(f"\n  Method 1 (log decay ratio, avg ratio={avg_ratio:.3f}):")
    print(f"    Next multiplier: {m1:.2f}x → ${p1:>12,.0f}")

    print(f"  Method 2 (sqrt of last multiplier):")
    print(f"    Next multiplier: {m2:.2f}x → ${p2:>12,.0f}")

    print(f"  Method 3 (log differences decay):")
    print(f"    Next multiplier: {m3:.2f}x → ${p3:>12,.0f}")

    avg_price = (p1 + p2 + p3) / 3
    print(f"\n  Average estimate: ${avg_price:>12,.0f}")

    # Timing
    avg_days = int(np.mean(days_to_peaks))
    recent_avg = int(np.mean(days_to_peaks[-3:]))
    est_date = pd.Timestamp(DATE4) + pd.Timedelta(days=recent_avg)
    print(f"\n  Days-to-peak history: {' → '.join(str(d) for d in days_to_peaks)}")
    print(f"  Recent avg (last 3): {recent_avg} days")
    print(f"  Expected halving: ~{DATE4}")
    print(f"  Estimated peak:   ~{est_date.strftime('%B %Y')} (±2 months)")

    print(f"\n  {'='*40}")
    print(f"  CYCLE 5 ESTIMATE: ${min(p1,p2,p3):,.0f} - ${max(p1,p2,p3):,.0f}")
    print(f"  TIMING:           ~{est_date.strftime('%B %Y')}")
    print(f"  {'='*40}")

    # Current price context
    current_price = df4[PRICE].iloc[-1]
    current_date = df4.index[-1]
    days_since = days_after_halving(DATE3, current_date)
    print(f"\n  Current BTC price: ${current_price:,.2f} ({current_date.strftime('%Y-%m-%d')})")
    print(f"  Days since halving: {days_since}")
    print()


main()
