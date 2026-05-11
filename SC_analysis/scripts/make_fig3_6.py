#!/usr/bin/env python3
"""Fig. 3.6 – Family × Evidence (time-weighted, fraction with tag)."""
from fig_common import *

rows = load_rows()
mat  = build_fam_evid(rows, time_weights(rows))
ELS  = [EVID_SHORT[e] for e in EVIDENCE_CATS]

fig, ax = plt.subplots(figsize=(10, 7))
draw_heatmap(ax, mat, DISP_FAMS, ELS, "YlOrRd", 0, mat.max(),
             f"Fig. 3.6 – Family × Evidence\n(time-weighted,  fraction with tag)\n"
             f"w = exp({LAMBDA} × (year − {YEAR_MIN}))",
             cbar_label="fraction weighted", annot_frac=0.08)
fig.tight_layout()
fig.savefig(OUT_DIR / "fig3_6.png", dpi=150, bbox_inches="tight")
print("Saved → fig3_6.png")
plt.close()
