#!/usr/bin/env python3
"""Fig. 3.5 – Family × Mechanism (time-weighted, P(mech|family))."""
from fig_common import *

rows = load_rows()
mat  = build_fam_mech(rows, time_weights(rows))
MLS  = [MECH_SHORT[m] for m in MECH_ORDER]

fig, ax = plt.subplots(figsize=(10, 7))
draw_heatmap(ax, mat, DISP_FAMS, MLS, "YlOrRd", 0, 1,
             f"Fig. 3.5 – Family × Mechanism\n(time-weighted,  P(mech|family))\n"
             f"w = exp({LAMBDA} × (year − {YEAR_MIN}))",
             cbar_label="P(mech|family) weighted", annot_frac=0.05)
fig.tight_layout()
fig.savefig(OUT_DIR / "fig3_5.png", dpi=150, bbox_inches="tight")
print("Saved → fig3_5.png")
plt.close()
