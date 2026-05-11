#!/usr/bin/env python3
"""Fig. 3.4 – Evidence self-correlation (phi coefficient)."""
from fig_common import *

rows = load_rows()
mat  = build_evid_selfcorr(rows, flat_weights(rows))
ELS  = [EVID_SHORT[e] for e in EVIDENCE_CATS]

fig, ax = plt.subplots(figsize=(8, 7))
draw_heatmap(ax, mat, ELS, ELS, "RdBu_r", -1, 1,
             "Fig. 3.4 – Evidence Self-Correlation\n(φ coefficient,  papers with ≥1 tag)",
             cbar_label="φ coefficient", annot_frac=0.05, diverging=True)
fig.tight_layout()
fig.savefig(OUT_DIR / "fig3_4.png", dpi=150, bbox_inches="tight")
print("Saved → fig3_4.png")
plt.close()
