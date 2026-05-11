#!/usr/bin/env python3
"""Fig. 2.2 – Mechanism distribution (horizontal bar, top score per paper)."""
from fig_common import *

rows = load_rows()
mech_counts  = Counter(r["mechanism"] for r in rows)
sorted_mechs = sorted(MECH_ORDER, key=lambda m: mech_counts.get(m, 0))
vals   = [mech_counts.get(m, 0) for m in sorted_mechs]
colors = [MECH_COLORS[m] for m in sorted_mechs]
labels = [MECH_SHORT[m] for m in sorted_mechs]

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.barh(labels, vals, color=colors, edgecolor="white", linewidth=0.5, height=0.72)
for bar, v in zip(bars, vals):
    if v > 0:
        ax.text(v + max(vals) * 0.01, bar.get_y() + bar.get_height() / 2,
                str(v), va="center", ha="left", fontsize=9)
ax.set_xlabel("Number of papers", fontsize=11)
ax.set_title("Fig. 2.2 – Mechanism (top score)", fontsize=13, fontweight="bold")
ax.set_xlim(0, max(vals) * 1.16)
ax.grid(axis="x", alpha=0.3, linewidth=0.5)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / "fig2_2.png", dpi=150, bbox_inches="tight")
print("Saved → fig2_2.png")
plt.close()
