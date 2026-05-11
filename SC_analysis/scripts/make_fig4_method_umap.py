#!/usr/bin/env python3
"""UMAP of papers in 128-d method space, coloured by mechanism.

Each paper is a 128-bit indicator vector (one bit per method).  UMAP reduces
to 2-D so we can see whether mechanism labels cluster in method-space.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import umap

sys.path.insert(0, str(Path(__file__).parent))
from fig_common import MECH_ORDER, MECH_COLORS, MECH_SHORT, CSV_PATH

OUT_DIR = Path(__file__).parent.parent / "output" / "figures_4"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    df = pd.read_csv(CSV_PATH)
    cols = list(df.columns)
    method_cols = cols[cols.index("DFT"):cols.index("other")]
    X = df[method_cols].fillna(0).astype(float).to_numpy()
    # drop papers with no methods at all (they carry no signal)
    has = X.sum(axis=1) > 0
    X = X[has]
    sub = df[has].reset_index(drop=True)

    # UMAP on Jaccard distance (right for binary vectors)
    reducer = umap.UMAP(
        n_neighbors=50,
        min_dist=0.25,
        metric="jaccard",
        random_state=7,
        n_components=2,
    )
    emb = reducer.fit_transform(X)

    # clip to the dense core: drop outer 10% on each axis
    lo = np.percentile(emb, 10, axis=0)
    hi = np.percentile(emb, 90, axis=0)
    pad = (hi - lo) * 0.04
    xlim = (lo[0] - pad[0], hi[0] + pad[0])
    ylim = (lo[1] - pad[1], hi[1] + pad[1])
    # additionally drop points outside this window from the plot data
    in_box = (
        (emb[:, 0] >= xlim[0]) & (emb[:, 0] <= xlim[1]) &
        (emb[:, 1] >= ylim[0]) & (emb[:, 1] <= ylim[1])
    )
    emb = emb[in_box]
    sub = sub[in_box].reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(12, 10), dpi=160)
    ax.set_facecolor("#f7f8fb")

    known = sub["mechanism"].isin(MECH_ORDER)
    # unknown mechanism first, grey, back layer
    unk = emb[~known]
    if len(unk):
        ax.scatter(unk[:, 0], unk[:, 1], s=6, c="#d0d4db",
                   alpha=0.5, linewidths=0, label="other / none")
    # per-mechanism overlay
    for m in MECH_ORDER:
        mask = (sub["mechanism"] == m).to_numpy()
        if not mask.any():
            continue
        pts = emb[mask]
        ax.scatter(pts[:, 0], pts[:, 1], s=8, c=[MECH_COLORS[m]], alpha=0.78,
                   linewidths=0, label=f"{MECH_SHORT.get(m, m)} (n={mask.sum()})")

    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ("top", "right", "left", "bottom"):
        ax.spines[sp].set_visible(False)
    ax.legend(loc="center left", bbox_to_anchor=(1.00, 0.5), frameon=False,
              fontsize=9, title="Mechanism", title_fontsize=10)
    ax.set_title(
        f"UMAP of {len(sub):,} papers in 128-d method space, Jaccard metric\n"
        "colour = GPT-labelled mechanism;  position = shared method usage",
        fontsize=12,
    )
    fig.tight_layout()

    out = OUT_DIR / "fig4_method_umap.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


if __name__ == "__main__":
    main()
