#!/usr/bin/env python3
"""Fig. 3.3 – Mechanism × Evidence (unweighted, fraction with tag)."""
from fig_common import *

rows = load_rows()
mat  = build_mech_evid(rows, flat_weights(rows))
MLS  = [MECH_SHORT[m] for m in MECH_ORDER]
ELS  = [EVID_SHORT[e] for e in EVIDENCE_CATS]

fig, ax = plt.subplots(figsize=(10, 6))
draw_heatmap(ax, mat, MLS, ELS, "Blues", 0, mat.max(),
             "Fig. 3.3 – Mechanism × Evidence\n(unweighted,  fraction with tag)",
             cbar_label="fraction", annot_frac=0.08)
fig.tight_layout()
fig.savefig(OUT_DIR / "fig3_3.png", dpi=150, bbox_inches="tight")
print("Saved → fig3_3.png")
plt.close()
