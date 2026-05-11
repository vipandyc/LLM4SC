#!/usr/bin/env python3
"""Fig. 3.10 – Mechanism composition per family (normalised stacked bars)."""
from fig_common import *
import numpy as np

rows = load_rows()
fam_mech = np.zeros((NF, NM))
for r in rows:
    fi = FAM_IDX.get(r["family"])
    mi = MECH_IDX.get(r["mechanism"])
    if fi is not None and mi is not None:
        fam_mech[fi, mi] += 1
row_sums = fam_mech.sum(axis=1, keepdims=True)
row_sums[row_sums == 0] = 1
fam_mech_norm = fam_mech / row_sums

y_pos   = np.arange(NF)
bottoms = np.zeros(NF)

fig, ax = plt.subplots(figsize=(9, 7))
for mi, mech in enumerate(MECH_ORDER):
    ax.barh(y_pos, fam_mech_norm[:, mi], left=bottoms,
            color=MECH_COLORS[mech], label=MECH_SHORT[mech], height=0.72)
    bottoms += fam_mech_norm[:, mi]

ax.set_yticks(y_pos)
ax.set_yticklabels(DISP_FAMS, fontsize=9)
ax.set_xlabel("Fraction", fontsize=11)
ax.set_xlim(0, 1.0)
ax.set_title("Fig. 3.10 – Mechanism Composition per Family\n(normalised)",
             fontsize=13, fontweight="bold")
ax.legend(fontsize=8, bbox_to_anchor=(1.01, 1), loc="upper left", ncol=1, framealpha=0.8)
ax.grid(axis="x", alpha=0.3, linewidth=0.5)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / "fig3_10.png", dpi=150, bbox_inches="tight")
print("Saved → fig3_10.png")
plt.close()
