#!/usr/bin/env python3
"""Fig. 2.5 – Publication timeline stacked by mechanism."""
from fig_common import *
import numpy as np

rows = load_rows()
year_mech = {m: Counter() for m in MECH_ORDER}
for r in rows:
    if r["year"].strip().isdigit() and r["mechanism"] in MECH_ORDER:
        year_mech[r["mechanism"]][int(r["year"])] += 1

bottoms = np.zeros(len(YEARS))

fig, ax = plt.subplots(figsize=(11, 5))
for mech in MECH_ORDER:
    mvals = np.array([year_mech[mech].get(y, 0) for y in YEARS], dtype=float)
    ax.bar(YEARS, mvals, bottom=bottoms, color=MECH_COLORS[mech],
           label=MECH_SHORT[mech], width=1.0, edgecolor="none")
    bottoms += mvals

ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("Number of papers", fontsize=11)
ax.set_title("Fig. 2.5 – Publication Timeline by Mechanism", fontsize=13, fontweight="bold")
ax.legend(fontsize=7.5, loc="upper left", ncol=2, framealpha=0.75)
ax.set_xlim(1955, 2025)
ax.grid(axis="y", alpha=0.3, linewidth=0.5)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / "fig2_5.png", dpi=150, bbox_inches="tight")
print("Saved → fig2_5.png")
plt.close()
