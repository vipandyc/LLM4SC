#!/usr/bin/env python3
"""Fig. 2.3_3 – Computational evidence distribution (horizontal bar, multi-label)."""
from fig_common import *
import matplotlib.pyplot as plt

METHODS = ["DFT", "DFPT", "QMC", "DMFT", "ED", "DMRG"]
COLORS  = {m: plt.cm.Set2(i / (len(METHODS) - 1)) for i, m in enumerate(METHODS)}

def parse(val):
    return [] if val.strip() in ("none", "") else [m.strip() for m in val.split(" | ")]

rows = load_rows()
counts = Counter(m for r in rows for m in parse(r.get("evidence_computation", "none")))
none_count = sum(1 for r in rows if r.get("evidence_computation", "none").strip() == "none")

sorted_methods = sorted(METHODS, key=lambda m: counts.get(m, 0))
vals   = [counts.get(m, 0) for m in sorted_methods]
colors = [COLORS[m] for m in sorted_methods]

fig, ax = plt.subplots(figsize=(8, 4))
bars = ax.barh(sorted_methods, vals, color=colors, edgecolor="white", linewidth=0.5, height=0.72)
for bar, v in zip(bars, vals):
    if v > 0:
        ax.text(v + max(vals) * 0.01, bar.get_y() + bar.get_height() / 2,
                str(v), va="center", ha="left", fontsize=9)
ax.set_xlabel("Papers with method (multi-label)", fontsize=11)
ax.set_title(
    f"Fig. 2.3_3 – Computational Evidence\n(no-computation papers: {none_count})",
    fontsize=13, fontweight="bold",
)
ax.set_xlim(0, max(vals) * 1.16)
ax.grid(axis="x", alpha=0.3, linewidth=0.5)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / "fig2_3_3.png", dpi=150, bbox_inches="tight")
print("Saved → fig2_3_3.png")
plt.close()
