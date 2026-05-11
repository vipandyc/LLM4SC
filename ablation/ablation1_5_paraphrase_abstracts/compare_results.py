#!/usr/bin/env python3
"""
Ablation 1.5 — Compare score distributions across K = {0, 1, 3, 5}.

Reads aggregated_k*.csv from results/, computes per-mechanism mean/std,
inter-K Spearman correlations vs original, and score variance as a function of K.

Usage (from repo root):
    python ablation/ablation1_5_paraphrase_abstracts/compare_results.py
"""

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

K_LABELS = {
    "k0": "Original (K=0)",
    "k1": "K=1",
    "k3": "K=3",
    "k5": "K=5",
}


def load_all() -> dict[str, pd.DataFrame]:
    dfs = {}
    for key in ["k0", "k1", "k3", "k5"]:
        fname = f"aggregated_{key}_original.csv" if key == "k0" else f"aggregated_{key}.csv"
        path = RESULTS_DIR / fname
        if path.exists():
            dfs[key] = pd.read_csv(path)
        else:
            print(f"WARNING: {path.name} not found — skipping K={key[1:]}")
    return dfs


def print_summary(dfs: dict[str, pd.DataFrame]):
    rows = []
    base = dfs.get("k0")
    for key, df in dfs.items():
        for m in MECHANISMS:
            if m not in df.columns:
                continue
            s = df[m]
            row = {
                "K": key[1:],
                "mechanism": SHORT[m],
                "mean": round(s.mean(), 3),
                "std": round(s.std(), 3),
            }
            if base is not None and key != "k0" and m in base.columns:
                common = pd.merge(base[["id", m]], df[["id", m]], on="id", suffixes=("_base", "_k"))
                if common[f"{m}_base"].std() > 0 and common[f"{m}_k"].std() > 0:
                    rho, _ = stats.spearmanr(common[f"{m}_base"], common[f"{m}_k"])
                    row["spearman_vs_original"] = round(rho, 3)
                else:
                    row["spearman_vs_original"] = "N/A"
            else:
                row["spearman_vs_original"] = "—"
            rows.append(row)

    table = pd.DataFrame(rows)
    print("\n=== Ablation 1.5: Score Statistics by K ===\n")
    print(table.to_string(index=False))
    table.to_csv(RESULTS_DIR / "comparison_table.csv", index=False)
    print(f"\nSaved comparison_table.csv")
    return table


def plot_variance_vs_k(dfs: dict[str, pd.DataFrame]):
    """For each mechanism, plot mean per-paper std of scores vs K."""
    # Per-paper std: std across K independently scored paraphrases.
    # We have aggregated (averaged) scores; we can measure cross-K spread by
    # computing std of per-mechanism mean across K levels for each paper.

    # Align all K levels on common paper IDs
    keys = [k for k in ["k0", "k1", "k3", "k5"] if k in dfs]
    merged = None
    for key in keys:
        df = dfs[key][["id"] + MECHANISMS].copy()
        suffix = f"_{key}"
        df = df.rename(columns={m: m + suffix for m in MECHANISMS})
        merged = df if merged is None else merged.merge(df, on="id", how="inner")

    if merged is None or len(merged) == 0:
        print("No overlapping papers across K levels — skipping variance plot.")
        return

    k_vals = [int(k[1:]) for k in keys]
    mean_stds = []  # per mechanism, per K: average std of paper scores across K levels up to this K

    for mech in MECHANISMS:
        cols = [mech + f"_{k}" for k in keys]
        available = [c for c in cols if c in merged.columns]
        vals = merged[available].values  # (n_papers, n_K_levels)
        stds_per_k = []
        for j in range(1, len(available) + 1):
            stds_per_k.append(np.std(vals[:, :j], axis=1).mean())
        mean_stds.append(stds_per_k)

    fig, ax = plt.subplots(figsize=(9, 5))
    for i, mech in enumerate(MECHANISMS):
        if max(mean_stds[i]) == 0:
            continue
        ax.plot(k_vals[:len(mean_stds[i])], mean_stds[i],
                marker="o", label=SHORT[mech])
    ax.set_xlabel("K (number of paraphrases averaged)")
    ax.set_ylabel("Mean per-paper score std across K levels")
    ax.set_title("Ablation 1.5: Score variance vs. K")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    ax.set_xticks(k_vals)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "variance_vs_k.png", dpi=150)
    plt.close()
    print("Saved variance_vs_k.png")


def plot_mean_by_k(dfs: dict[str, pd.DataFrame]):
    keys = [k for k in ["k0", "k1", "k3", "k5"] if k in dfs]
    n_k = len(keys)
    x = np.arange(len(MECHANISMS))
    width = 0.8 / n_k
    colors = ["steelblue", "seagreen", "coral", "mediumpurple"]

    fig, ax = plt.subplots(figsize=(13, 4.5))
    for i, (key, color) in enumerate(zip(keys, colors)):
        df = dfs[key]
        means = [df[m].mean() if m in df.columns else 0 for m in MECHANISMS]
        stds = [df[m].std() if m in df.columns else 0 for m in MECHANISMS]
        offset = (i - n_k / 2 + 0.5) * width
        ax.bar(x + offset, means, width, label=K_LABELS[key],
               color=color, alpha=0.8, yerr=stds, capsize=2)

    ax.set_xticks(x)
    ax.set_xticklabels([SHORT[m] for m in MECHANISMS], rotation=25, ha="right")
    ax.set_ylabel("Mean score")
    ax.set_title("Ablation 1.5: Mean ± std per mechanism, by K")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "mean_by_k.png", dpi=150)
    plt.close()
    print("Saved mean_by_k.png")


def main():
    dfs = load_all()
    if not dfs:
        print("No result files found. Run run_ablation1_5.py first.")
        return

    print_summary(dfs)
    plot_variance_vs_k(dfs)
    plot_mean_by_k(dfs)


if __name__ == "__main__":
    main()
