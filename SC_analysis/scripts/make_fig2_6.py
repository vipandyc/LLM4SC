#!/usr/bin/env python3
"""Fig. 2.6 – Publication timeline stacked by evidence (multi-label)."""
from fig_common import *
import numpy as np

rows = load_rows()
year_evid = {e: Counter() for e in EVIDENCE_CATS}
for cat, r in explode_evidence(rows):
    if r["year"].strip().isdigit() and cat in EVIDENCE_CATS:
        year_evid[cat][int(r["year"])] += 1

bottoms = np.zeros(len(YEARS))

fig, ax = plt.subplots(figsize=(11, 5))
for evid in EVIDENCE_CATS:
    evals = np.array([year_evid[evid].get(y, 0) for y in YEARS], dtype=float)
    ax.bar(YEARS, evals, bottom=bottoms, color=EVID_COLORS[evid],
           label=EVID_SHORT[evid], width=1.0, edgecolor="none")
    bottoms += evals

ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("Papers with tag (multi-label)", fontsize=11)
ax.set_title("Fig. 2.6 – Publication Timeline by Evidence", fontsize=13, fontweight="bold")
ax.legend(fontsize=7.5, loc="upper left", ncol=2, framealpha=0.75)
ax.set_xlim(1955, 2025)
ax.grid(axis="y", alpha=0.3, linewidth=0.5)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / "fig2_6.png", dpi=150, bbox_inches="tight")
print("Saved → fig2_6.png")
plt.close()
