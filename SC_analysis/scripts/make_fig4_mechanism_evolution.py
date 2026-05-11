#!/usr/bin/env python3
"""Mechanism evolution network — same logic as method evolution but for the
9 mechanisms.

y = median publication year of papers with that mechanism.
x = 1-D MDS of citation-profile cosine distance.
Arrows i → j when mechanism-i papers significantly cite mechanism-j papers
(asymmetric flow), consistent with "i developed from j".
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.manifold import MDS

sys.path.insert(0, str(Path(__file__).parent))
from fig_common import CSV_PATH, MECH_ORDER, MECH_COLORS, MECH_SHORT

OUT_DIR = Path(__file__).parent.parent / "output" / "figures_4"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MIN_FLOW = 40
ASYM_RATIO = 0.58    # mechanisms are all "mature"; less strict threshold
YEAR_SLACK = 5
TOP_K = 3


def parse_cites(s):
    if not isinstance(s, str) or not s.strip():
        return []
    try:
        return list(json.loads(s))
    except Exception:
        return []


def main() -> None:
    df = pd.read_csv(CSV_PATH)
    df = df[df["mechanism"].isin(MECH_ORDER)].reset_index(drop=True)
    mech_idx = {m: i for i, m in enumerate(MECH_ORDER)}
    K = len(MECH_ORDER)

    # one-hot mechanism matrix (each paper has one mechanism)
    idx_arr = df["mechanism"].map(mech_idx).to_numpy()
    X = np.zeros((len(df), K), dtype=np.float64)
    X[np.arange(len(df)), idx_arr] = 1.0

    # citation edges
    id_to_row = {pid: i for i, pid in enumerate(df["id"])}
    src_list, tgt_list = [], []
    for i, cites in enumerate(df["outgoing_internal_citing_papers"].map(parse_cites)):
        for t in cites:
            j = id_to_row.get(t)
            if j is not None:
                src_list.append(i)
                tgt_list.append(j)
    src_arr = np.asarray(src_list)
    tgt_arr = np.asarray(tgt_list)
    print(f"paper-level edges (restricted to MECH_ORDER): {len(src_arr):,}")

    # 9×9 flow matrix
    F = X[src_arr].T @ X[tgt_arr]

    # median year per mechanism
    years = df["year"].to_numpy(dtype=float)
    yr = np.array([np.median(years[idx_arr == k]) for k in range(K)])
    counts = np.array([(idx_arr == k).sum() for k in range(K)])

    # ancestry arrows
    edges = []
    for i in range(K):
        for j in range(K):
            if i == j:
                continue
            fij = F[i, j]
            fji = F[j, i]
            if fij < MIN_FLOW:
                continue
            denom = fij + fji
            if denom <= 0 or fij / denom < ASYM_RATIO:
                continue
            if yr[i] + YEAR_SLACK < yr[j]:
                continue
            edges.append((i, j, fij, fij / denom))

    # top-K outgoing per mechanism (K mechanisms, fewer edges so more permissive)
    per_src = {}
    for (i, j, f, r) in edges:
        per_src.setdefault(i, []).append((j, f, r))
    edges = []
    for i, lst in per_src.items():
        lst.sort(key=lambda t: -t[1])
        for (j, f, r) in lst[:TOP_K]:
            edges.append((i, j, f, r))
    print(f"ancestry arrows: {len(edges)}")

    # x = 1-D MDS of cosine distance on outgoing citation profiles
    prof = F / F.sum(axis=1, keepdims=True).clip(min=1)
    norms = np.linalg.norm(prof, axis=1).clip(min=1e-9)
    cos = (prof @ prof.T) / np.outer(norms, norms)
    dist = np.clip(1.0 - cos, 0.0, 2.0)
    dist = (dist + dist.T) / 2
    np.fill_diagonal(dist, 0.0)

    mds = MDS(n_components=1, dissimilarity="precomputed",
              random_state=7, n_init=8, normalized_stress="auto")
    x_coord = mds.fit_transform(dist).flatten()
    x_coord = (x_coord - x_coord.min()) / (x_coord.max() - x_coord.min()) * 10

    # --- draw ------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(12, 9), dpi=160)
    ax.set_facecolor("#fafbfc")

    for (i, j, f, r) in edges:
        x0, y0 = x_coord[i], yr[i]
        x1, y1 = x_coord[j], yr[j]
        rad = 0.22 if x1 >= x0 else -0.22
        lw = 0.8 + 2.5 * np.log1p(f) / np.log1p(F.max())
        ax.annotate(
            "", xy=(x1, y1), xytext=(x0, y0),
            arrowprops=dict(
                arrowstyle="-|>,head_length=0.55,head_width=0.32",
                color="#475569", lw=lw, alpha=0.5,
                connectionstyle=f"arc3,rad={rad}",
            ),
            zorder=1,
        )

    sizes = 120 + 25 * np.sqrt(counts)
    for k, m in enumerate(MECH_ORDER):
        color = MECH_COLORS[m]
        ax.scatter(x_coord[k], yr[k], s=sizes[k], c=[color],
                   edgecolors="#0b1220", linewidths=0.8, zorder=3)
        ax.text(x_coord[k], yr[k], MECH_SHORT.get(m, m),
                fontsize=9, ha="center", va="center", zorder=4,
                fontweight="bold", color="#0b1220",
                bbox=dict(boxstyle="round,pad=0.18", fc="white",
                          ec="none", alpha=0.80))

    ax.set_xlabel("Citation-profile similarity (1-D MDS; nearby = siblings)", fontsize=10)
    ax.set_ylabel("Median publication year of papers with mechanism", fontsize=10)
    ax.set_title(
        f"Mechanism evolution network — ancestry arrows + sibling proximity\n"
        f"{K} mechanisms;  {len(edges)} arrows "
        f"(flow ≥ {MIN_FLOW}, asymmetry ≥ {ASYM_RATIO:g}, newer → older);  "
        f"node size ∝ √(paper count)",
        fontsize=12,
    )
    ax.grid(True, axis="y", alpha=0.3, linewidth=0.4)
    ax.set_xticks([])
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)

    fig.tight_layout()
    out = OUT_DIR / "fig4_mechanism_evolution.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


if __name__ == "__main__":
    main()
