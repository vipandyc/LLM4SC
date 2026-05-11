#!/usr/bin/env python3
"""Fig. 2.3 – Theoretical Evidence distribution (horizontal bar, multi-label)."""
from fig_common import *

rows = load_rows()

def _explode_theory(rows):
    for r in rows:
        ev = r["evidence_theory"].strip()
        if ev and ev != "none":
            for cat in ev.split(" | "):
                cat = cat.strip()
                if cat:
                    yield cat, r

ev_counts   = Counter(cat for cat, _ in _explode_theory(rows))
none_count  = sum(1 for r in rows if r["evidence_theory"].strip() == "none")
sorted_evid = sorted(EVIDENCE_CATS, key=lambda e: ev_counts.get(e, 0))
vals   = [ev_counts.get(e, 0) for e in sorted_evid]
colors = [EVID_COLORS[e] for e in sorted_evid]
labels = [EVID_SHORT[e] for e in sorted_evid]

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.barh(labels, vals, color=colors, edgecolor="white", linewidth=0.5, height=0.72)
for bar, v in zip(bars, vals):
    if v > 0:
        ax.text(v + max(vals) * 0.01, bar.get_y() + bar.get_height() / 2,
                str(v), va="center", ha="left", fontsize=9)
ax.set_xlabel("Papers with tag (multi-label)", fontsize=11)
ax.set_title(
    f"Fig. 2.3 – Theoretical Evidence\n(no-theory papers: {none_count})",
    fontsize=13, fontweight="bold",
)
ax.set_xlim(0, max(vals) * 1.16)
ax.grid(axis="x", alpha=0.3, linewidth=0.5)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / "fig2_3_1.png", dpi=150, bbox_inches="tight")
print("Saved → fig2_3_1.png")
plt.close()
