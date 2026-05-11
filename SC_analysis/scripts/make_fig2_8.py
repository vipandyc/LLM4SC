#!/usr/bin/env python3
"""Fig. 2.8 – Yearly portion by mechanism (line chart).

For each year t: fraction_i(t) = count_i(t) / sum_j count_j(t)
"""
from fig_common import *
import numpy as np

rows = load_rows()

year_mech = {m: Counter() for m in MECH_ORDER}
for r in rows:
    if r["year"].strip().isdigit() and r["mechanism"] in MECH_ORDER:
        year_mech[r["mechanism"]][int(r["year"])] += 1

fracs = {m: [] for m in MECH_ORDER}
for y in YEARS:
    counts = {m: year_mech[m].get(y, 0) for m in MECH_ORDER}
    total  = sum(counts.values())
    for m in MECH_ORDER:
        fracs[m].append(counts[m] / total if total > 0 else 0)

fig, ax = plt.subplots(figsize=(11, 5))
for m in MECH_ORDER:
    ax.plot(YEARS, fracs[m], label=MECH_SHORT[m], color=MECH_COLORS[m], linewidth=1.5)

ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("Portion of papers", fontsize=11)
ax.set_title("Fig. 2.8 – Yearly Portion by Mechanism", fontsize=13, fontweight="bold")
ax.set_xlim(YEARS[0], YEARS[-1])
ax.set_ylim(0, 1)
ax.legend(fontsize=7.5, loc="upper right", ncol=2, framealpha=0.75)
ax.grid(alpha=0.3, linewidth=0.5)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / "fig2_8.png", dpi=150, bbox_inches="tight")
print("Saved → fig2_8.png")
plt.close()
