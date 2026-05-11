#!/usr/bin/env python3
"""Method evolution network — ancestry (arrows) + siblings (x-proximity).

Every internal citation edge (paper A cites paper B) contributes an outer
product X_A ⊗ X_B to the 128×128 *method-flow* matrix ``F``, where X is the
paper's 0/1 method indicator vector.  Then:

* ``y`` coord of a method = median publication year of papers using it
* ``x`` coord = 1-D MDS of cosine distance between outgoing citation profiles
  (so two methods with similar "what they cite" land nearby → siblings)
* directed arrow  i → j  is drawn when

      F[i,j] ≥ MIN_FLOW
      F[i,j] / (F[i,j] + F[j,i]) ≥ ASYM_RATIO
      median_year[i]  ≥  median_year[j] − YEAR_SLACK

  i.e. method i is the younger method whose papers significantly cite papers
  using method j — an "i developed from j" signal.

Only the top-``K`` outgoing ancestry edges per method are kept.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from adjustText import adjust_text
from sklearn.manifold import MDS

sys.path.insert(0, str(Path(__file__).parent))
from fig_common import CSV_PATH
from make_fig4_method_chord import CATEGORY, CAT_COLOR, CAT_ORDER, CAT_SHORT

OUT_DIR = Path(__file__).parent.parent / "output" / "figures_4"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MIN_USE = 40           # keep only methods used in >= N papers
MIN_FLOW = 25          # minimum absolute flow for an arrow
ASYM_RATIO = 0.70      # i→j / (i→j + j→i) must exceed this
YEAR_SLACK = 3         # tolerate i being up to N years older than j
TOP_K = 4              # per-node ancestry edges to keep


def parse_cites(s):
    if not isinstance(s, str) or not s.strip():
        return []
    try:
        return list(json.loads(s))
    except Exception:
        return []


def cat_of(method):
    for c, members in CATEGORY.items():
        if method in members:
            return c
    return "other"


def main() -> None:
    df = pd.read_csv(CSV_PATH)
    cols = list(df.columns)
    method_cols = cols[cols.index("DFT"):cols.index("other")]
    X = df[method_cols].fillna(0).astype(np.int8).to_numpy()
    years = df["year"].to_numpy(dtype=float)
    id_to_row = {pid: i for i, pid in enumerate(df["id"])}

    # build (src, tgt) citation edge arrays
    src_list, tgt_list = [], []
    for i, cites in enumerate(df["outgoing_internal_citing_papers"].map(parse_cites)):
        for t in cites:
            j = id_to_row.get(t)
            if j is not None:
                src_list.append(i)
                tgt_list.append(j)
    src_arr = np.asarray(src_list)
    tgt_arr = np.asarray(tgt_list)
    print(f"paper-level edges: {len(src_arr):,}")

    # method-flow matrix: F[i,j] = # citations from method-i paper to method-j paper
    Xs = X[src_arr].astype(np.float64)
    Xt = X[tgt_arr].astype(np.float64)
    F = Xs.T @ Xt  # 128×128
    np.fill_diagonal(F, 0)  # suppress same-method self-loops (handled separately)

    count = X.sum(axis=0)
    median_year = np.full(X.shape[1], np.nan)
    for k in range(X.shape[1]):
        idx = X[:, k] == 1
        if idx.any():
            median_year[k] = np.median(years[idx])

    # --- filter methods --------------------------------------------------------
    keep = np.where(count >= MIN_USE)[0]
    names = [method_cols[k] for k in keep]
    F_sub = F[np.ix_(keep, keep)]
    cnt = count[keep]
    yr = median_year[keep]
    K = len(keep)
    print(f"kept {K} methods (use ≥ {MIN_USE})")

    # --- ancestry edges --------------------------------------------------------
    cand = []
    for i in range(K):
        for j in range(K):
            if i == j:
                continue
            fij = F_sub[i, j]
            fji = F_sub[j, i]
            if fij < MIN_FLOW:
                continue
            denom = fij + fji
            if denom <= 0 or fij / denom < ASYM_RATIO:
                continue
            if yr[i] + YEAR_SLACK < yr[j]:
                continue
            cand.append((i, j, fij, fij / denom))

    # keep top-K outgoing per node
    per_src = {}
    for (i, j, f, r) in cand:
        per_src.setdefault(i, []).append((j, f, r))
    edges = []
    for i, lst in per_src.items():
        lst.sort(key=lambda t: -t[1])
        for (j, f, r) in lst[:TOP_K]:
            edges.append((i, j, f, r))
    print(f"ancestry arrows after top-{TOP_K} pruning: {len(edges)}")

    # --- x coordinate from citation-profile MDS --------------------------------
    profile = F_sub / F_sub.sum(axis=1, keepdims=True).clip(min=1)
    norms = np.linalg.norm(profile, axis=1).clip(min=1e-9)
    cos = (profile @ profile.T) / np.outer(norms, norms)
    dist = np.clip(1.0 - cos, 0.0, 2.0)
    # symmetrise numerical noise
    dist = (dist + dist.T) / 2
    np.fill_diagonal(dist, 0.0)

    mds = MDS(
        n_components=1, dissimilarity="precomputed",
        random_state=7, n_init=6, normalized_stress="auto",
    )
    x_coord = mds.fit_transform(dist).flatten()
    x_coord = (x_coord - x_coord.min()) / (x_coord.max() - x_coord.min()) * 10

    # --- draw ------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(18, 12), dpi=160)
    ax.set_facecolor("#fafbfc")

    # arrows underneath
    for (i, j, f, r) in edges:
        x0, y0 = x_coord[i], yr[i]
        x1, y1 = x_coord[j], yr[j]
        # curve direction stable (arc to the right)
        rad = 0.18 if x1 >= x0 else -0.18
        ax.annotate(
            "", xy=(x1, y1), xytext=(x0, y0),
            arrowprops=dict(
                arrowstyle="-|>,head_length=0.45,head_width=0.25",
                color="#64748b",
                lw=0.45 + 1.1 * np.log1p(f) / np.log1p(F_sub.max()),
                alpha=0.35,
                connectionstyle=f"arc3,rad={rad}",
            ),
            zorder=1,
        )

    # nodes
    sizes = 50 + 9 * np.sqrt(cnt)
    colors = [CAT_COLOR.get(cat_of(n), "#bab0ac") for n in names]
    ax.scatter(x_coord, yr, s=sizes, c=colors,
               edgecolors="#0b1220", linewidths=0.5, zorder=3)
    # labels with adjustText to avoid overlaps
    texts = []
    for k, name in enumerate(names):
        texts.append(ax.text(x_coord[k], yr[k], name, fontsize=6.3,
                             ha="center", va="center", zorder=4))
    adjust_text(
        texts,
        ax=ax,
        expand=(1.06, 1.18),
        arrowprops=dict(arrowstyle="-", color="#9aa3b2", lw=0.3, alpha=0.6),
        only_move={"points": "y", "text": "xy"},
    )

    ax.set_xlabel("Citation-profile similarity (1-D MDS; nearby = siblings)", fontsize=10)
    ax.set_ylabel("Median publication year of papers using method", fontsize=10)
    ax.set_title(
        f"Method evolution network — ancestry arrows + sibling proximity\n"
        f"{K} methods (≥ {MIN_USE} papers);  {len(edges)} arrows "
        f"(flow ≥ {MIN_FLOW}, asymmetry ≥ {ASYM_RATIO:g}, newer → older);  "
        f"node size ∝ √(usage count);  colour = method category",
        fontsize=12,
    )
    ax.grid(True, axis="y", alpha=0.3, linewidth=0.4)
    ax.set_xticks([])
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)

    handles = [plt.Line2D([0], [0], marker="o", linestyle="",
                          markerfacecolor=CAT_COLOR[c], markeredgecolor="#0b1220",
                          markersize=8, label=CAT_SHORT[c]) for c in CAT_ORDER]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.01, 1.0),
              frameon=False, fontsize=9, title="Method category",
              title_fontsize=10)

    fig.tight_layout()
    out = OUT_DIR / "fig4_method_evolution.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


if __name__ == "__main__":
    main()
