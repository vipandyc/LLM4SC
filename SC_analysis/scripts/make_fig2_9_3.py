#!/usr/bin/env python3
"""Fig. 2.9_3 – Yearly portion by computational evidence (line chart, multi-label)."""
from fig_common import *
import numpy as np
import matplotlib.pyplot as plt

METHODS = ["DFT", "DFPT", "QMC", "DMFT", "ED", "DMRG"]
COLORS  = {m: plt.cm.Set2(i / (len(METHODS) - 1)) for i, m in enumerate(METHODS)}

def parse(val):
    return [] if val.strip() in ("none", "") else [m.strip() for m in val.split(" | ")]

rows = load_rows()
year_method = {m: Counter() for m in METHODS}
for r in rows:
    if r["year"].strip().isdigit():
        y = int(r["year"])
        for m in parse(r.get("evidence_computation", "none")):
            if m in year_method:
                year_method[m][y] += 1

fracs = {m: [] for m in METHODS}
for y in YEARS:
    counts = {m: year_method[m].get(y, 0) for m in METHODS}
    total  = sum(counts.values())
    for m in METHODS:
        fracs[m].append(counts[m] / total if total > 0 else 0)

fig, ax = plt.subplots(figsize=(11, 5))
for m in METHODS:
    ax.plot(YEARS, fracs[m], label=m, color=COLORS[m], linewidth=1.5)

ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("Portion of computation tags", fontsize=11)
ax.set_title("Fig. 2.9_3 – Yearly Portion by Computational Evidence", fontsize=13, fontweight="bold")
ax.set_xlim(YEARS[0], YEARS[-1])
ax.set_ylim(0, 1)
ax.legend(fontsize=7.5, loc="upper right", ncol=1, framealpha=0.75)
ax.grid(alpha=0.3, linewidth=0.5)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / "fig2_9_3.png", dpi=150, bbox_inches="tight")
print("Saved → fig2_9_3.png")
plt.close()
