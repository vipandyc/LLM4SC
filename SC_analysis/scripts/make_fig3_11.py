#!/usr/bin/env python3
"""Fig. 3.11 – Evidence fraction per family (heatmap)."""
from fig_common import *
import numpy as np

rows       = load_rows()
fam_totals = Counter(r["family"] for r in rows)
fam_evid   = np.zeros((NF, NE))
for cat, r in explode_evidence(rows):
    fi = FAM_IDX.get(r["family"])
    ei = EVID_IDX.get(cat)
    if fi is not None and ei is not None:
        fam_evid[fi, ei] += 1
for fi, fam in enumerate(DISP_FAMS):
    fam_evid[fi] /= max(fam_totals.get(fam, 1), 1)

ELS  = [EVID_SHORT[e] for e in EVIDENCE_CATS]
vmax = fam_evid.max()

fig, ax = plt.subplots(figsize=(10, 7))
draw_heatmap(ax, fam_evid, DISP_FAMS, ELS, "Blues", 0, vmax,
             "Fig. 3.11 – Evidence Fraction per Family",
             cbar_label="Fraction of family papers", annot_frac=0.08)
fig.tight_layout()
fig.savefig(OUT_DIR / "fig3_11.png", dpi=150, bbox_inches="tight")
print("Saved → fig3_11.png")
plt.close()
