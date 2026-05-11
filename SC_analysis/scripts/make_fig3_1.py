#!/usr/bin/env python3
"""Fig. 3.1 – Family × Mechanism (unweighted, P(mech|family))."""
from fig_common import *

rows = load_rows()
mat  = build_fam_mech(rows, flat_weights(rows))
MLS  = [MECH_SHORT[m] for m in MECH_ORDER]

fig, ax = plt.subplots(figsize=(10, 7))
draw_heatmap(ax, mat, DISP_FAMS, MLS, "Blues", 0, 1,
             "Fig. 3.1 – Family × Mechanism\n(unweighted,  P(mech|family))",
             cbar_label="P(mech|family)", annot_frac=0.05)
fig.tight_layout()
fig.savefig(OUT_DIR / "fig3_1.png", dpi=150, bbox_inches="tight")
print("Saved → fig3_1.png")
plt.close()
