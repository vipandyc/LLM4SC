#!/usr/bin/env python3
"""Fig. 2.7 – Yearly portion by family (line chart).

For each year t: fraction_i(t) = count_i(t) / sum_j count_j(t)
"""
from fig_common import *
import numpy as np

STACK_FAMS = [
    "cuprate", "iron-based", "heavy-fermion", "nickelate",
    "kagome", "hydrogen", "ruthenate", "elemental", "MgB2", "2D", "organic",
]

rows = load_rows()

year_fam   = {f: Counter() for f in STACK_FAMS}
year_other = Counter()
for r in rows:
    if not r["year"].strip().isdigit():
        continue
    y = int(r["year"])
    f = r["family"]
    if f in STACK_FAMS:
        year_fam[f][y] += 1
    else:
        year_other[y] += 1

all_cats = STACK_FAMS + ["other/unknown"]
fracs    = {c: [] for c in all_cats}
for y in YEARS:
    counts = {f: year_fam[f].get(y, 0) for f in STACK_FAMS}
    counts["other/unknown"] = year_other.get(y, 0)
    total = sum(counts.values())
    for c in all_cats:
        fracs[c].append(counts[c] / total if total > 0 else 0)

colors = [FAM_COLORS[f] for f in STACK_FAMS] + ["#bbbbbb"]

fig, ax = plt.subplots(figsize=(11, 5))
for c, col in zip(all_cats, colors):
    ax.plot(YEARS, fracs[c], label=c, color=col, linewidth=1.5)

ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("Portion of papers", fontsize=11)
ax.set_title("Fig. 2.7 – Yearly Portion by Family", fontsize=13, fontweight="bold")
ax.set_xlim(YEARS[0], YEARS[-1])
ax.set_ylim(0, 1)
ax.legend(fontsize=7.5, loc="upper right", ncol=2, framealpha=0.75)
ax.grid(alpha=0.3, linewidth=0.5)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / "fig2_7.png", dpi=150, bbox_inches="tight")
print("Saved → fig2_7.png")
plt.close()
