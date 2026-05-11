#!/usr/bin/env python3
"""Decade-by-decade alluvial of mechanism composition with citation flows.

Columns are 5-year bins; column height is split by mechanism (stacked bars).
Ribbons between adjacent columns show citation flows: for each edge (A cites B),
contribute flow from (bin_of_A, mech_of_A) to (bin_of_B, mech_of_B) where
bin_of_A > bin_of_B (forward in time).  Only flows between adjacent bins are
rendered to keep the figure readable; longer-range flows are aggregated into
a "deep-history" band at the left edge of each bin.
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
from fig_common import MECH_ORDER, MECH_COLORS, MECH_SHORT, CSV_PATH

OUT_DIR = Path(__file__).parent.parent / "output" / "figures_4"
OUT_DIR.mkdir(parents=True, exist_ok=True)


BIN_SIZE = 10  # years per bin


def parse_cites(s):
    if not isinstance(s, str) or not s.strip():
        return []
    try:
        return list(json.loads(s))
    except Exception:
        return []


def sigmoid_ribbon(ax, x0, y0a, y0b, x1, y1a, y1b, color, alpha):
    n = 40
    xs = np.linspace(0, 1, n)
    # smoothstep
    s = xs * xs * (3 - 2 * xs)
    top_y = y0a + (y1a - y0a) * s
    bot_y = y0b + (y1b - y0b) * s
    xs_full = x0 + (x1 - x0) * xs
    verts = list(zip(xs_full, top_y)) + list(zip(xs_full[::-1], bot_y[::-1]))
    codes = [mpath.Path.MOVETO] + [mpath.Path.LINETO] * (len(verts) - 1)
    path = mpath.Path(verts, codes)
    patch = mpatches.PathPatch(path, facecolor=color, edgecolor="none",
                               alpha=alpha, linewidth=0)
    ax.add_patch(patch)


def main() -> None:
    df = pd.read_csv(CSV_PATH)
    df = df[df["mechanism"].isin(MECH_ORDER)].copy()
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
    K = len(MECH_ORDER)

    # column stacks: counts[b, k] = number of papers
    counts = np.zeros((n_bins, K), dtype=float)
    for b, m in zip(df["bin"], df["mechanism"]):
        counts[b, MECH_ORDER.index(m)] += 1

    # flow tensor: flow[b_src, k_src, k_tgt] = citations from bin b_src,mech k_src
    # to bin b_src-1, mech k_tgt  (i.e. between adjacent bins)
    flow = np.zeros((n_bins, K, K), dtype=float)

    pid_bin = dict(zip(df["id"], df["bin"]))
    pid_mech = dict(zip(df["id"], df["mechanism"]))

    for src_id, cites in zip(df["id"], df["outgoing_internal_citing_papers"].map(parse_cites)):
        bs = pid_bin.get(src_id, -1)
        ms = pid_mech.get(src_id)
        if bs < 0 or ms is None:
            continue
        ks = MECH_ORDER.index(ms)
        for tgt_id in cites:
            bt = pid_bin.get(tgt_id, -1)
            mt = pid_mech.get(tgt_id)
            if bt < 0 or mt is None:
                continue
            if bt == bs - 1:  # only adjacent back-citation
                kt = MECH_ORDER.index(mt)
                flow[bs, ks, kt] += 1

    # ── drawing ───────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(16, 8), dpi=160)
    ax.set_facecolor("white")

    col_w = 0.55  # width of each column as fraction of 1 unit
    xs = np.arange(n_bins, dtype=float)

    # column stacks
    col_top = {}    # (b, k) -> (y_low, y_high)
    for b in range(n_bins):
        y = 0.0
        # normalise within column so column height = 1
        total = counts[b].sum()
        if total == 0:
            continue
        for k in range(K):
            h = counts[b, k] / total
            m = MECH_ORDER[k]
            ax.add_patch(mpatches.Rectangle(
                (xs[b] - col_w / 2, y), col_w, h,
                facecolor=MECH_COLORS[m], edgecolor="white", linewidth=0.6,
                zorder=3,
            ))
            col_top[(b, k)] = (y, y + h)
            y += h

    # ribbons: for each adjacent pair, split each source stack & target stack
    # into subslots by the (k_src, k_tgt) flow matrix.
    for b in range(1, n_bins):
        F = flow[b]  # K x K
        if F.sum() == 0:
            continue
        # split source column (bin b) from top of each mech stack downward by
        # outgoing flow fractions; split target column (bin b-1) by incoming
        src_outgoing = F.sum(axis=1)  # K
        tgt_incoming = F.sum(axis=0)  # K

        # for each source mech, anchor within its stack
        src_anchor = {k: col_top[(b, k)][1] for k in range(K)}  # start at top, move down
        tgt_anchor = {k: col_top[(b - 1, k)][1] for k in range(K)}

        # iterate mechanisms in order so ribbons don't jumble
        for ks in range(K):
            if src_outgoing[ks] == 0:
                continue
            src_h = col_top[(b, ks)][1] - col_top[(b, ks)][0]
            if counts[b, ks] == 0:
                continue
            # fraction of stack that is "cited forward"
            frac_of_stack = min(1.0, src_outgoing[ks] / max(counts[b, ks], 1))
            src_band_h = src_h * frac_of_stack
            src_base = col_top[(b, ks)][0]  # bottom
            # but paint from top of stack downward
            src_top = col_top[(b, ks)][1]

            for kt in range(K):
                v = F[ks, kt]
                if v <= 0:
                    continue
                h_s = (v / src_outgoing[ks]) * src_band_h
                # target slot: proportional to fraction of its incoming
                tgt_h = col_top[(b - 1, kt)][1] - col_top[(b - 1, kt)][0]
                if counts[b - 1, kt] == 0 or tgt_incoming[kt] == 0:
                    continue
                frac_tgt = min(1.0, tgt_incoming[kt] / max(counts[b - 1, kt], 1))
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
                    MECH_COLORS[MECH_ORDER[ks]],
                    0.22,
                )
                src_top -= h_s
                tgt_anchor[kt] -= h_t

    # axes cosmetics
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
                          markerfacecolor=MECH_COLORS[m], markeredgecolor="none",
                          markersize=10, label=MECH_SHORT.get(m, m))
               for m in MECH_ORDER]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.01, 1.0),
              frameon=False, fontsize=9, title="Mechanism", title_fontsize=10)

    ax.set_title(
        f"Mechanism composition by {BIN_SIZE}-year bin + adjacent-bin citation flows\n"
        "column height normalised to 1; ribbons = citations from bin[t] papers "
        "to bin[t-1] papers, coloured by citing mechanism",
        fontsize=12,
    )
    fig.tight_layout()

    out = OUT_DIR / "fig4_mechanism_alluvial.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


if __name__ == "__main__":
    main()
