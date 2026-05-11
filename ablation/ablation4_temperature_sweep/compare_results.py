#!/usr/bin/env python3
"""
Ablation 4 — Compare score distributions across temperatures.

Reads results/scores_T*.csv, computes per-temperature per-mechanism stats,
parse failure rate, all-zero rate, and plots variance vs temperature.

Usage (from repo root):
    python ablation/ablation4_temperature_sweep/compare_results.py
"""

import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

RESULTS_DIR = Path(__file__).parent / "results"

MECHANISMS = [
    "pure el-ph coupling", "bipolaron el-ph coupling", "AFM fluctuation",
    "FM fluctuation", "charge density wave", "nematic fluctuation",
    "plasmon fluctuation", "pure el correlation", "spin liquid el correlation",
]
SHORT = {
    "pure el-ph coupling": "El-ph",
    "bipolaron el-ph coupling": "Bipolaron",
    "AFM fluctuation": "AFM",
    "FM fluctuation": "FM",
    "charge density wave": "CDW",
    "nematic fluctuation": "Nematic",
    "plasmon fluctuation": "Plasmon",
    "pure el correlation": "Correlation",
    "spin liquid el correlation": "Spin liquid",
}

TEMP_ORDER = [0.0, 0.3, 0.5, 0.7, 1.0]


def parse_output(raw) -> dict | None:
    if not isinstance(raw, str) or not raw.strip():
        return None
    raw = re.sub(r"```[a-z]*\n?", "", raw).strip().rstrip("`")
    try:
        return json.loads(raw)
    except Exception:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            try:
                return json.loads(m.group())
            except Exception:
                pass
    return None


def load_all() -> dict[float, pd.DataFrame]:
    dfs = {}
    for f in sorted(RESULTS_DIR.glob("scores_T*.csv")):
        label = f.stem[len("scores_T"):]
        temp = float(label.replace("p", "."))
        dfs[temp] = pd.read_csv(f)
    return dfs


def extract_scores(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    records, failures = [], 0
    for _, row in df.iterrows():
        obj = parse_output(row.get("GPT_output"))
        if obj is None:
            failures += 1
            records.append({m: 0.0 for m in MECHANISMS})
        else:
            records.append({m: float(obj.get(m, 0)) for m in MECHANISMS})
    return pd.DataFrame(records), failures


def build_summary(dfs: dict[float, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for temp in sorted(dfs.keys()):
        df = dfs[temp]
        scores, n_fail = extract_scores(df)
        n = len(df)
        all_zero = (scores[MECHANISMS].sum(axis=1) == 0).sum()
        row = {
            "temperature": temp,
            "n": n,
            "parse_failures": n_fail,
            "parse_fail_pct": round(100 * n_fail / n, 1),
            "all_zero_pct": round(100 * all_zero / n, 1),
        }
        for m in MECHANISMS:
            row[f"mean_{SHORT[m]}"] = round(scores[m].mean(), 3)
            row[f"std_{SHORT[m]}"] = round(scores[m].std(), 3)
        rows.append(row)
    return pd.DataFrame(rows)


def spearman_vs_baseline(dfs: dict[float, pd.DataFrame]) -> pd.DataFrame:
    # Use T=0.0 as baseline (most deterministic)
    baseline_key = 0.0
    if baseline_key not in dfs:
        return pd.DataFrame()
    base_scores, _ = extract_scores(dfs[baseline_key])
    rows = []
    for temp in sorted(dfs.keys()):
        if temp == baseline_key:
            continue
        scores, _ = extract_scores(dfs[temp])
        rhos = {"temperature": temp}
        for m in MECHANISMS:
            b, s = base_scores[m], scores[m]
            if b.std() > 0 and s.std() > 0:
                rho, _ = stats.spearmanr(b, s)
                rhos[SHORT[m]] = round(rho, 3)
            else:
                rhos[SHORT[m]] = "N/A"
        rows.append(rhos)
    return pd.DataFrame(rows)


def plot_variance_vs_temp(summary: pd.DataFrame):
    temps = summary["temperature"].tolist()
    fig, ax = plt.subplots(figsize=(9, 5))
    for m in MECHANISMS:
        stds = summary[f"std_{SHORT[m]}"].tolist()
        if max(stds) == 0:
            continue
        ax.plot(temps, stds, marker="o", label=SHORT[m])
    ax.set_xlabel("Temperature")
    ax.set_ylabel("Per-mechanism score std")
    ax.set_title("Ablation 4: Score std vs. Temperature (gpt-4.1-mini)")
    ax.set_xticks(temps)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    fig.tight_layout()
    out = RESULTS_DIR / "variance_vs_temp.png"
    fig.savefig(out, dpi=150)
    plt.close()
    print(f"Saved {out.name}")


def plot_all_zero_vs_temp(summary: pd.DataFrame):
    temps = summary["temperature"].tolist()
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(temps, summary["all_zero_pct"].tolist(), marker="o", color="coral")
    ax.set_xlabel("Temperature")
    ax.set_ylabel("All-zero output rate (%)")
    ax.set_title("Ablation 4: All-zero rate vs. Temperature")
    ax.set_xticks(temps)
    fig.tight_layout()
    out = RESULTS_DIR / "all_zero_vs_temp.png"
    fig.savefig(out, dpi=150)
    plt.close()
    print(f"Saved {out.name}")


def plot_mean_bars(summary: pd.DataFrame):
    mechanisms_short = [SHORT[m] for m in MECHANISMS]
    x = np.arange(len(mechanisms_short))
    n_temps = len(summary)
    width = 0.8 / n_temps
    colors = plt.cm.coolwarm(np.linspace(0, 1, n_temps))

    fig, ax = plt.subplots(figsize=(13, 5))
    for i, (_, row) in enumerate(summary.iterrows()):
        means = [row[f"mean_{s}"] for s in mechanisms_short]
        stds = [row[f"std_{s}"] for s in mechanisms_short]
        offset = (i - n_temps / 2 + 0.5) * width
        ax.bar(x + offset, means, width, label=f"T={row['temperature']}",
               color=colors[i], alpha=0.85, yerr=stds, capsize=2)

    ax.set_xticks(x)
    ax.set_xticklabels(mechanisms_short, rotation=25, ha="right")
    ax.set_ylabel("Mean score")
    ax.set_title("Ablation 4: Mean ± std per mechanism, by temperature")
    ax.legend(bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8)
    fig.tight_layout()
    out = RESULTS_DIR / "mean_bars_by_temp.png"
    fig.savefig(out, dpi=150)
    plt.close()
    print(f"Saved {out.name}")


def main():
    dfs = load_all()
    if not dfs:
        print("No result files found. Run run_ablation4.py first.")
        return

    summary = build_summary(dfs)
    print("\n=== Ablation 4: Temperature Sweep (gpt-4.1-mini) ===\n")
    cols = ["temperature", "parse_fail_pct", "all_zero_pct"] + [f"mean_{SHORT[m]}" for m in MECHANISMS]
    print(summary[cols].to_string(index=False))
    summary.to_csv(RESULTS_DIR / "summary_table.csv", index=False)
    print("\nSaved summary_table.csv")

    rho_df = spearman_vs_baseline(dfs)
    if not rho_df.empty:
        print("\n=== Spearman ρ vs T=0.0 baseline ===")
        print(rho_df.to_string(index=False))
        rho_df.to_csv(RESULTS_DIR / "spearman_vs_T0.csv", index=False)

    plot_variance_vs_temp(summary)
    plot_all_zero_vs_temp(summary)
    plot_mean_bars(summary)


if __name__ == "__main__":
    main()
