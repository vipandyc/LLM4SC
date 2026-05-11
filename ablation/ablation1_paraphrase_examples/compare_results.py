#!/usr/bin/env python3
"""
Ablation 1 — Step 3: Compare score distributions between baseline and paraphrased prompts.

Reads results/baseline_scores.csv and results/paraphrased_scores.csv,
computes per-mechanism mean/std, and prints a summary table plus saves plots.

Usage (from repo root):
    python ablation/ablation1_paraphrase_examples/compare_results.py
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
BASELINE_FILE = RESULTS_DIR / "baseline_scores.csv"
PARA_FILE = RESULTS_DIR / "paraphrased_scores.csv"

MECHANISMS = [
    "pure el-ph coupling",
    "bipolaron el-ph coupling",
    "AFM fluctuation",
    "FM fluctuation",
    "charge density wave",
    "nematic fluctuation",
    "plasmon fluctuation",
    "pure el correlation",
    "spin liquid el correlation",
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


def parse_gpt_output(raw) -> dict:
    if not isinstance(raw, str) or not raw.strip():
        return {}
    # Strip markdown fences if present
    raw = re.sub(r"```[a-z]*\n?", "", raw).strip().rstrip("`")
    try:
        return json.loads(raw)
    except Exception:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    return {}


def extract_scores(df: pd.DataFrame) -> pd.DataFrame:
    records = []
    for _, row in df.iterrows():
        obj = parse_gpt_output(row.get("GPT_output"))
        rec = {"id": row.get("id", "")}
        for m in MECHANISMS:
            try:
                rec[m] = float(obj.get(m, 0))
            except (TypeError, ValueError):
                rec[m] = 0.0
        records.append(rec)
    return pd.DataFrame(records)


def print_summary(base_scores: pd.DataFrame, para_scores: pd.DataFrame):
    rows = []
    for m in MECHANISMS:
        b = base_scores[m]
        p = para_scores[m]
        # Only compare rows where both are present
        common = min(len(b), len(p))
        b, p = b.iloc[:common], p.iloc[:common]

        # Mean absolute difference per paper
        mad = (b - p).abs().mean()

        # Spearman correlation
        if b.std() > 0 and p.std() > 0:
            rho, pval = stats.spearmanr(b, p)
        else:
            rho, pval = float("nan"), float("nan")

        rows.append({
            "mechanism": SHORT[m],
            "baseline_mean": round(b.mean(), 3),
            "baseline_std": round(b.std(), 3),
            "para_mean": round(p.mean(), 3),
            "para_std": round(p.std(), 3),
            "mean_abs_diff": round(mad, 3),
            "spearman_rho": round(rho, 3) if not np.isnan(rho) else "N/A",
            "p_value": round(pval, 4) if not np.isnan(pval) else "N/A",
        })

    table = pd.DataFrame(rows)
    print("\n=== Ablation 1: Paraphrase Examples — Score Comparison ===\n")
    print(table.to_string(index=False))
    table.to_csv(RESULTS_DIR / "comparison_table.csv", index=False)
    print(f"\nSaved comparison_table.csv to {RESULTS_DIR}")
    return table


def plot_distributions(base_scores: pd.DataFrame, para_scores: pd.DataFrame):
    n = len(MECHANISMS)
    ncols = 3
    nrows = (n + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(14, nrows * 3.5))
    axes = axes.flatten()

    for i, m in enumerate(MECHANISMS):
        ax = axes[i]
        b = base_scores[m].values
        p = para_scores[m].values
        bins = np.arange(0, 6.5, 0.5)
        ax.hist(b, bins=bins, alpha=0.6, label="Baseline", color="steelblue", density=True)
        ax.hist(p, bins=bins, alpha=0.6, label="Paraphrased", color="coral", density=True)
        ax.set_title(SHORT[m], fontsize=10)
        ax.set_xlabel("Score")
        ax.set_ylabel("Density")
        ax.legend(fontsize=7)

    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    fig.suptitle("Ablation 1: Score distributions — Baseline vs. Paraphrased examples", fontsize=12)
    fig.tight_layout()
    out = RESULTS_DIR / "distribution_comparison.png"
    fig.savefig(out, dpi=150)
    plt.close()
    print(f"Saved distribution_comparison.png to {RESULTS_DIR}")


def plot_mean_comparison(table: pd.DataFrame):
    x = np.arange(len(MECHANISMS))
    width = 0.35
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.bar(x - width / 2, table["baseline_mean"], width, label="Baseline",
           color="steelblue", alpha=0.8,
           yerr=table["baseline_std"], capsize=3)
    ax.bar(x + width / 2, table["para_mean"], width, label="Paraphrased",
           color="coral", alpha=0.8,
           yerr=table["para_std"], capsize=3)
    ax.set_xticks(x)
    ax.set_xticklabels(table["mechanism"], rotation=25, ha="right")
    ax.set_ylabel("Mean score")
    ax.set_title("Ablation 1: Mean ± std per mechanism")
    ax.legend()
    fig.tight_layout()
    out = RESULTS_DIR / "mean_std_comparison.png"
    fig.savefig(out, dpi=150)
    plt.close()
    print(f"Saved mean_std_comparison.png to {RESULTS_DIR}")


def main():
    if not BASELINE_FILE.exists() or not PARA_FILE.exists():
        print("ERROR: result files not found. Run run_ablation1.py first.")
        return

    base_df = pd.read_csv(BASELINE_FILE)
    para_df = pd.read_csv(PARA_FILE)

    base_scores = extract_scores(base_df)
    para_scores = extract_scores(para_df)

    parse_fail_base = (base_df["GPT_output"].apply(lambda x: parse_gpt_output(x) == {})).sum()
    parse_fail_para = (para_df["GPT_output"].apply(lambda x: parse_gpt_output(x) == {})).sum()
    n = len(base_df)
    print(f"Parse failures — Baseline: {parse_fail_base}/{n}  Paraphrased: {parse_fail_para}/{n}")

    table = print_summary(base_scores, para_scores)
    plot_distributions(base_scores, para_scores)
    plot_mean_comparison(table)


if __name__ == "__main__":
    main()
