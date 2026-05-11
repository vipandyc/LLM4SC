#!/usr/bin/env python3
"""Fig. 2.4 – Publication timeline stacked by family."""
from fig_common import *

STACK_FAMS = [
    "cuprate", "iron-based", "heavy-fermion", "nickelate",
    "kagome", "hydrogen", "ruthenate", "elemental", "MgB2", "2D", "organic",
]

rows = load_rows()
year_fam   = {f: Counter() for f in STACK_FAMS}
year_total = Counter()
for r in rows:
    if r["year"].strip().isdigit():
        y = int(r["year"])
        year_total[y] += 1
        if r["family"] in STACK_FAMS:
            year_fam[r["family"]][y] += 1

import numpy as np
bottoms = np.zeros(len(YEARS))

fig, ax = plt.subplots(figsize=(11, 5))
for fam in STACK_FAMS:
    fvals = np.array([year_fam[fam].get(y, 0) for y in YEARS], dtype=float)
    ax.bar(YEARS, fvals, bottom=bottoms, color=FAM_COLORS[fam],
           label=fam, width=1.0, edgecolor="none")
    bottoms += fvals

rest = np.array([max(year_total.get(y, 0) - bottoms[i], 0) for i, y in enumerate(YEARS)])
ax.bar(YEARS, rest, bottom=bottoms, color="#bbbbbb",
       label="other/unknown", width=1.0, edgecolor="none")

ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("Number of papers", fontsize=11)
ax.set_title("Fig. 2.4 – Publication Timeline by Family", fontsize=13, fontweight="bold")
ax.legend(fontsize=7.5, loc="upper left", ncol=2, framealpha=0.75)
ax.set_xlim(1955, 2025)
ax.grid(axis="y", alpha=0.3, linewidth=0.5)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / "fig2_4.png", dpi=150, bbox_inches="tight")
print("Saved → fig2_4.png")
plt.close()
