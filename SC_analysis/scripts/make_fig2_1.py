#!/usr/bin/env python3
"""Fig. 2.1 – Superconductor Family distribution (horizontal bar)."""
from fig_common import *

rows = load_rows()
fam_counts  = Counter(r["family"] for r in rows)
sorted_fams = sorted(FAMILY_ORDER, key=lambda f: fam_counts.get(f, 0))
vals   = [fam_counts.get(f, 0) for f in sorted_fams]
colors = [FAM_COLORS[f] for f in sorted_fams]

fig, ax = plt.subplots(figsize=(8, 7))
bars = ax.barh(sorted_fams, vals, color=colors, edgecolor="white", linewidth=0.5, height=0.72)
for bar, v in zip(bars, vals):
    if v > 0:
        ax.text(v + max(vals) * 0.01, bar.get_y() + bar.get_height() / 2,
                str(v), va="center", ha="left", fontsize=9)
ax.set_xlabel("Number of papers", fontsize=11)
ax.set_title("Fig. 2.1 – Superconductor Family", fontsize=13, fontweight="bold")
ax.set_xlim(0, max(vals) * 1.16)
ax.grid(axis="x", alpha=0.3, linewidth=0.5)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / "fig2_1.png", dpi=150, bbox_inches="tight")
print("Saved → fig2_1.png")
plt.close()
