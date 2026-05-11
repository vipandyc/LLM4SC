#!/usr/bin/env python3
"""Fig. 3.2 – Family × Evidence (unweighted, fraction with tag)."""
from fig_common import *

rows = load_rows()
mat  = build_fam_evid(rows, flat_weights(rows))
ELS  = [EVID_SHORT[e] for e in EVIDENCE_CATS]

fig, ax = plt.subplots(figsize=(10, 7))
draw_heatmap(ax, mat, DISP_FAMS, ELS, "Blues", 0, mat.max(),
             "Fig. 3.2 – Family × Evidence\n(unweighted,  fraction with tag)",
             cbar_label="fraction", annot_frac=0.08)
fig.tight_layout()
fig.savefig(OUT_DIR / "fig3_2.png", dpi=150, bbox_inches="tight")
print("Saved → fig3_2.png")
plt.close()
