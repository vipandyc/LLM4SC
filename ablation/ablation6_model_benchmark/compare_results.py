#!/usr/bin/env python3
"""
Ablation 6 — Compare score distributions across models.

Reads results/scores_<model>.csv, computes per-model per-mechanism stats,
parse failure rate, fraction all-zero outputs, and plots a score heatmap.

Usage (from repo root):
    python ablation/ablation6_model_benchmark/compare_results.py
"""

import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
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

MODEL_ORDER = ["gpt-5-mini", "gpt-4.1-mini", "gpt-4.1", "o4-mini",
               "gpt-5", "o3", "gpt-5.4",
               "claude-sonnet-4-5", "claude-opus-4-5"]


def parse_output(raw) -> dict | None:
    """Returns parsed dict or None on failure."""
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


def load_all() -> dict[str, pd.DataFrame]:
    dfs = {}
    for f in sorted(RESULTS_DIR.glob("scores_*.csv")):
        model = f.stem[len("scores_"):]
        dfs[model] = pd.read_csv(f)
    return dfs


def extract_scores(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Returns (scores_df, n_parse_failures)."""
    records, failures = [], 0
    for _, row in df.iterrows():
        obj = parse_output(row.get("GPT_output"))
        if obj is None:
            failures += 1
            records.append({m: 0.0 for m in MECHANISMS})
        else:
            records.append({m: float(obj.get(m, 0)) for m in MECHANISMS})
    return pd.DataFrame(records), failures


def build_summary(dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for model, df in dfs.items():
        scores, n_fail = extract_scores(df)
        n = len(df)
        all_zero = (scores[MECHANISMS].sum(axis=1) == 0).sum()
        row = {
            "model": model,
            "n": n,
            "parse_failures": n_fail,
            "parse_fail_pct": round(100 * n_fail / n, 1),
            "all_zero_pct": round(100 * all_zero / n, 1),
        }
        for m in MECHANISMS:
            row[f"mean_{SHORT[m]}"] = round(scores[m].mean(), 3)
            row[f"std_{SHORT[m]}"] = round(scores[m].std(), 3)
        rows.append(row)

    df_out = pd.DataFrame(rows)
    # Sort by MODEL_ORDER where possible
    order = {m: i for i, m in enumerate(MODEL_ORDER)}
    df_out["_order"] = df_out["model"].map(lambda x: order.get(x, 99))
    df_out = df_out.sort_values("_order").drop(columns="_order").reset_index(drop=True)
    return df_out


def print_summary(summary: pd.DataFrame):
    print("\n=== Ablation 6: Model Benchmark ===\n")
    cols = ["model", "parse_fail_pct", "all_zero_pct"] + [f"mean_{SHORT[m]}" for m in MECHANISMS]
    print(summary[cols].to_string(index=False))


def spearman_vs_baseline(dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    baseline_key = "gpt-5-mini"
    if baseline_key not in dfs:
        return pd.DataFrame()
    base_scores, _ = extract_scores(dfs[baseline_key])
    rows = []
    for model, df in dfs.items():
        if model == baseline_key:
            continue
        scores, _ = extract_scores(df)
        rhos = {}
        for m in MECHANISMS:
            b, s = base_scores[m], scores[m]
            if b.std() > 0 and s.std() > 0:
                rho, _ = stats.spearmanr(b, s)
                rhos[SHORT[m]] = round(rho, 3)
            else:
                rhos[SHORT[m]] = "N/A"
        rows.append({"model": model, **rhos})
    return pd.DataFrame(rows)


def plot_heatmap(summary: pd.DataFrame):
    mean_cols = [f"mean_{SHORT[m]}" for m in MECHANISMS]
    heat = summary.set_index("model")[mean_cols].copy()
    heat.columns = [SHORT[m] for m in MECHANISMS]

    fig, ax = plt.subplots(figsize=(12, max(3, len(heat) * 0.7 + 1.5)))
    sns.heatmap(heat, annot=True, fmt=".2f", cmap="YlOrRd", linewidths=0.4,
                cbar_kws={"label": "Mean score"}, ax=ax)
    ax.set_title("Ablation 6: Mean score per mechanism × model")
    ax.set_ylabel("")
    fig.tight_layout()
    out = RESULTS_DIR / "heatmap_model_mechanism.png"
    fig.savefig(out, dpi=150)
    plt.close()
    print(f"Saved {out.name}")


def plot_parse_failures(summary: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].bar(summary["model"], summary["parse_fail_pct"], color="steelblue", alpha=0.8)
    axes[0].set_title("Parse failure rate (%)")
    axes[0].set_ylabel("%")
    axes[0].tick_params(axis="x", rotation=30)

    axes[1].bar(summary["model"], summary["all_zero_pct"], color="coral", alpha=0.8)
    axes[1].set_title("All-zero output rate (%)")
    axes[1].set_ylabel("%")
    axes[1].tick_params(axis="x", rotation=30)

    fig.tight_layout()
    out = RESULTS_DIR / "parse_and_zero_rates.png"
    fig.savefig(out, dpi=150)
    plt.close()
    print(f"Saved {out.name}")


def plot_mean_bars(summary: pd.DataFrame):
    mechanisms_short = [SHORT[m] for m in MECHANISMS]
    x = np.arange(len(mechanisms_short))
    n_models = len(summary)
    width = 0.8 / n_models
    colors = plt.cm.tab10(np.linspace(0, 1, n_models))

    fig, ax = plt.subplots(figsize=(13, 5))
    for i, (_, row) in enumerate(summary.iterrows()):
        means = [row[f"mean_{s}"] for s in mechanisms_short]
        stds = [row[f"std_{s}"] for s in mechanisms_short]
        offset = (i - n_models / 2 + 0.5) * width
        ax.bar(x + offset, means, width, label=row["model"],
               color=colors[i], alpha=0.85, yerr=stds, capsize=2)

    ax.set_xticks(x)
    ax.set_xticklabels(mechanisms_short, rotation=25, ha="right")
    ax.set_ylabel("Mean score")
    ax.set_title("Ablation 6: Mean ± std per mechanism, by model")
    ax.legend(bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8)
    fig.tight_layout()
    out = RESULTS_DIR / "mean_bars_by_model.png"
    fig.savefig(out, dpi=150)
    plt.close()
    print(f"Saved {out.name}")


def main():
    dfs = load_all()
    if not dfs:
        print("No result files found. Run run_ablation6.py first.")
        return

    summary = build_summary(dfs)
    print_summary(summary)
    summary.to_csv(RESULTS_DIR / "summary_table.csv", index=False)
    print(f"\nSaved summary_table.csv")

    rho_df = spearman_vs_baseline(dfs)
    if not rho_df.empty:
        print("\n=== Spearman ρ vs gpt-5-mini baseline ===")
        print(rho_df.to_string(index=False))
        rho_df.to_csv(RESULTS_DIR / "spearman_vs_baseline.csv", index=False)

    plot_heatmap(summary)
    plot_parse_failures(summary)
    plot_mean_bars(summary)


if __name__ == "__main__":
    main()
