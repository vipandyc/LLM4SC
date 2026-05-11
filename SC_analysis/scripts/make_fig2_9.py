#!/usr/bin/env python3
"""Fig. 2.9 – Yearly portion by evidence (line chart, multi-label).

For each year t: fraction_i(t) = tag_count_i(t) / sum_j tag_count_j(t)
"""
from fig_common import *
import numpy as np

rows = load_rows()

year_evid = {e: Counter() for e in EVIDENCE_CATS}
for cat, r in explode_evidence(rows):
    if r["year"].strip().isdigit() and cat in EVIDENCE_CATS:
        year_evid[cat][int(r["year"])] += 1

fracs = {e: [] for e in EVIDENCE_CATS}
for y in YEARS:
    counts = {e: year_evid[e].get(y, 0) for e in EVIDENCE_CATS}
    total  = sum(counts.values())
    for e in EVIDENCE_CATS:
        fracs[e].append(counts[e] / total if total > 0 else 0)

fig, ax = plt.subplots(figsize=(11, 5))
for e in EVIDENCE_CATS:
    ax.plot(YEARS, fracs[e], label=EVID_SHORT[e], color=EVID_COLORS[e], linewidth=1.5)

ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("Portion of evidence tags", fontsize=11)
ax.set_title("Fig. 2.9 – Yearly Portion by Evidence", fontsize=13, fontweight="bold")
ax.set_xlim(YEARS[0], YEARS[-1])
ax.set_ylim(0, 1)
ax.legend(fontsize=7.5, loc="upper right", ncol=2, framealpha=0.75)
ax.grid(alpha=0.3, linewidth=0.5)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / "fig2_9.png", dpi=150, bbox_inches="tight")
print("Saved → fig2_9.png")
plt.close()
