#!/usr/bin/env python3
"""Fig. 3.9 – Δ Family × Evidence (time-weighted minus unweighted)."""
from fig_common import *
import numpy as np

rows   = load_rows()
W_flat = flat_weights(rows)
W_time = time_weights(rows)
delta  = build_fam_evid(rows, W_time) - build_fam_evid(rows, W_flat)
ELS    = [EVID_SHORT[e] for e in EVIDENCE_CATS]
lim    = max(abs(delta).max(), 1e-6)

fig, ax = plt.subplots(figsize=(10, 7))
draw_heatmap(ax, delta, DISP_FAMS, ELS, "RdBu_r", -lim, lim,
             "Fig. 3.9 – Δ Family × Evidence\n(weighted − unweighted;  red = more recent)",
             cbar_label="Δ fraction", annot_frac=0.15, diverging=True)
fig.tight_layout()
fig.savefig(OUT_DIR / "fig3_9.png", dpi=150, bbox_inches="tight")
print("Saved → fig3_9.png")
plt.close()
