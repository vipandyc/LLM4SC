#!/usr/bin/env python3
"""Decade-by-decade alluvial of method-category composition + citation flows.

Columns are 10-year bins; column height is 1 and split by method category
shares p(cat | decade) = mean over decade papers of p(cat | paper).
Ribbons between adjacent columns aggregate internal citations:
for each edge (A cites B) with decade(A) = decade(B) + 1 we add
p(cat_i | A) * p(cat_j | B) to the (src_cat, tgt_cat) flow.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.path as mpath
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from fig_common import CSV_PATH
from make_fig4_method_chord import (
    CATEGORY, CAT_ORDER, CAT_SHORT, CAT_COLOR, parse_cites,
)

OUT_DIR = Path(__file__).parent.parent / "output" / "figures_4"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BIN_SIZE = 10


def sigmoid_ribbon(ax, x0, y0a, y0b, x1, y1a, y1b, color, alpha):
    n = 40
    xs = np.linspace(0, 1, n)
    s = xs * xs * (3 - 2 * xs)
    top_y = y0a + (y1a - y0a) * s
    bot_y = y0b + (y1b - y0b) * s
    xs_full = x0 + (x1 - x0) * xs
    verts = list(zip(xs_full, top_y)) + list(zip(xs_full[::-1], bot_y[::-1]))
    codes = [mpath.Path.MOVETO] + [mpath.Path.LINETO] * (len(verts) - 1)
    ax.add_patch(mpatches.PathPatch(mpath.Path(verts, codes),
                                    facecolor=color, edgecolor="none",
                                    alpha=alpha, linewidth=0))


def main() -> None:
    df = pd.read_csv(CSV_PATH)
    cols = list(df.columns)
    method_cols = cols[cols.index("DFT"):cols.index("other")]

    # category distribution per paper
    K = len(CAT_ORDER)
    cat_idx = {c: i for i, c in enumerate(CAT_ORDER)}
    meth_to_cat = {}
    for m in method_cols:
        for c, members in CATEGORY.items():
            if m in members:
                meth_to_cat[m] = cat_idx[c]
                break
    X = df[method_cols].fillna(0).astype(int).to_numpy()
    P = np.zeros((len(df), K), dtype=float)
    for j, m in enumerate(method_cols):
        c = meth_to_cat.get(m)
        if c is None:
            continue
        P[:, c] += X[:, j]
    rs = P.sum(axis=1, keepdims=True)
    P_norm = np.divide(P, rs, out=np.zeros_like(P), where=rs > 0)

    # keep only papers with at least one categorised method
    has_cat = (rs[:, 0] > 0)
    df = df[has_cat].reset_index(drop=True)
    P_norm = P_norm[has_cat]

    y_min = int(df["year"].min()) // BIN_SIZE * BIN_SIZE
    y_max = int(df["year"].max())
    bin_edges = list(range(y_min, y_max + BIN_SIZE + 1, BIN_SIZE))
    n_bins = len(bin_edges) - 1

    def bin_of(y):
        if pd.isna(y):
            return -1
        b = (int(y) - y_min) // BIN_SIZE
        return max(0, min(n_bins - 1, b))

    df["bin"] = df["year"].map(bin_of)

    # column stack: counts[b, k] = sum over papers in bin b of p(cat k | paper)
    counts = np.zeros((n_bins, K), dtype=float)
    for i, b in enumerate(df["bin"]):
        counts[b] += P_norm[i]

    # flow tensor: flow[b, k_src, k_tgt] = citations from bin b→bin b-1 papers
    flow = np.zeros((n_bins, K, K), dtype=float)
    id_to_row = {pid: i for i, pid in enumerate(df["id"])}
    for i, cites in enumerate(df["outgoing_internal_citing_papers"].map(parse_cites)):
        bs = df["bin"].iloc[i]
        pa = P_norm[i]
        if pa.sum() == 0:
            continue
        for tgt in cites:
            j = id_to_row.get(tgt)
            if j is None:
                continue
            bt = df["bin"].iloc[j]
            if bt != bs - 1:
                continue
            pb = P_norm[j]
            if pb.sum() == 0:
                continue
            flow[bs] += np.outer(pa, pb)

    # draw
    fig, ax = plt.subplots(figsize=(16, 8), dpi=160)
    ax.set_facecolor("white")
    col_w = 0.55
    xs = np.arange(n_bins, dtype=float)

    col_top = {}
    for b in range(n_bins):
        total = counts[b].sum()
        if total == 0:
            continue
        y = 0.0
        for k in range(K):
            h = counts[b, k] / total
            c = CAT_ORDER[k]
            ax.add_patch(mpatches.Rectangle(
                (xs[b] - col_w / 2, y), col_w, h,
                facecolor=CAT_COLOR[c], edgecolor="white", linewidth=0.6,
                zorder=3,
            ))
            col_top[(b, k)] = (y, y + h)
            y += h

    for b in range(1, n_bins):
        F = flow[b]
        if F.sum() == 0:
            continue
        src_outgoing = F.sum(axis=1)
        tgt_incoming = F.sum(axis=0)
        tgt_anchor = {k: col_top[(b - 1, k)][1] for k in range(K)
                      if (b - 1, k) in col_top}

        for ks in range(K):
            if src_outgoing[ks] == 0 or (b, ks) not in col_top:
                continue
            src_h = col_top[(b, ks)][1] - col_top[(b, ks)][0]
            stack_mass = counts[b, ks] / counts[b].sum() if counts[b].sum() else 0
            if stack_mass == 0:
                continue
            frac_of_stack = min(1.0, src_outgoing[ks] / (counts[b, ks] if counts[b, ks] else 1))
            src_band_h = src_h * frac_of_stack
            src_top = col_top[(b, ks)][1]

            for kt in range(K):
                v = F[ks, kt]
                if v <= 0 or (b - 1, kt) not in col_top:
                    continue
                h_s = (v / src_outgoing[ks]) * src_band_h
                tgt_h = col_top[(b - 1, kt)][1] - col_top[(b - 1, kt)][0]
                if counts[b - 1, kt] == 0 or tgt_incoming[kt] == 0:
                    continue
                frac_tgt = min(1.0, tgt_incoming[kt] / counts[b - 1, kt])
                tgt_band_h = tgt_h * frac_tgt
                h_t = (v / tgt_incoming[kt]) * tgt_band_h

                y0a = src_top
                y0b = src_top - h_s
                y1a = tgt_anchor[kt]
                y1b = y1a - h_t

                sigmoid_ribbon(
                    ax,
                    xs[b] - col_w / 2, y0a, y0b,
                    xs[b - 1] + col_w / 2, y1a, y1b,
                    CAT_COLOR[CAT_ORDER[ks]],
                    0.22,
                )
                src_top -= h_s
                tgt_anchor[kt] -= h_t

    ax.set_xlim(-0.7, n_bins - 0.3)
    ax.set_ylim(-0.02, 1.04)
    ax.set_yticks([])
    tick_x = np.arange(n_bins)
    tick_labels = [f"{bin_edges[b]}–{bin_edges[b + 1] - 1}" for b in range(n_bins)]
    ax.set_xticks(tick_x)
    ax.set_xticklabels(tick_labels, rotation=45, ha="right", fontsize=8)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(axis="y", left=False)

    handles = [plt.Line2D([0], [0], marker="s", linestyle="",
                          markerfacecolor=CAT_COLOR[c], markeredgecolor="none",
                          markersize=10, label=CAT_SHORT[c])
               for c in CAT_ORDER]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.01, 1.0),
              frameon=False, fontsize=9, title="Method category",
              title_fontsize=10)

    ax.set_title(
        f"Method-category composition by {BIN_SIZE}-year bin + "
        f"adjacent-bin citation flows\n"
        "column height normalised to 1; ribbons = citations from bin[t] papers "
        "to bin[t-1] papers, weighted by p(cat|paper), coloured by citing category",
        fontsize=12,
    )
    fig.tight_layout()

    out = OUT_DIR / "fig4_method_alluvial.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


if __name__ == "__main__":
    main()
