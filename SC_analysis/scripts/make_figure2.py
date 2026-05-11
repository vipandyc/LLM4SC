#!/usr/bin/env python3
"""
Figure 2 – Data statistics for SC_final_data_5k.csv
Sub-panels 2.1 – 2.6  (2 rows × 3 cols)

  2.1  Family distribution (bar)
  2.2  Mechanism distribution (bar)
  2.3  Evidence distribution (exploded, bar)
  2.4  Publication timeline stacked by family
  2.5  Publication timeline stacked by mechanism
  2.6  Publication timeline stacked by evidence
"""

import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import Counter
from pathlib import Path

# ── paths ─────────────────────────────────────────────────────────────────────
CSV_PATH = Path(__file__).parent.parent / "SC_final_data_5k.csv"
OUT_PATH = Path(__file__).parent.parent / "output" / "figures" / "figure2.png"
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# ── canonical orders ──────────────────────────────────────────────────────────
FAMILY_ORDER = [
    "cuprate", "iron-based", "heavy-fermion", "nickelate",
    "hydrogen", "kagome", "ruthenate", "elemental", "MgB2", "2D",
    "organic", "A15", "alloy", "fulleride", "oxide", "carbide/nitride",
    "general-theory", "other", "unknown",
]
MECH_ORDER = [
    "pure el-ph coupling", "bipolaron el-ph coupling",
    "AFM fluctuation", "FM fluctuation", "charge density wave",
    "nematic fluctuation", "plasmon fluctuation",
    "pure el correlation", "spin liquid el correlation",
]
EVIDENCE_CATS = [
    "Phenomenological SC", "Microscopic pairing", "Field theory & RG",
    "Response & transport", "Topological", "Junction & interface",
    "Many-body & correlation", "Quantum circuits & info", "Other methods",
]
# display families for per-family breakdown (exclude catch-all buckets)
TOP_FAMS = [
    "cuprate", "iron-based", "heavy-fermion", "nickelate",
    "hydrogen", "kagome", "ruthenate", "elemental", "MgB2", "2D",
    "organic", "A15", "alloy", "fulleride", "oxide", "carbide/nitride",
]
MECH_SHORT = {
    "pure el-ph coupling":      "El-ph",
    "bipolaron el-ph coupling": "Bipolaron",
    "AFM fluctuation":          "AFM",
    "FM fluctuation":           "FM",
    "charge density wave":      "CDW",
    "nematic fluctuation":      "Nematic",
    "plasmon fluctuation":      "Plasmon",
    "pure el correlation":      "El-corr",
    "spin liquid el correlation":"Spin liq",
}
EVID_SHORT = {
    "Phenomenological SC":      "Phenom. SC",
    "Microscopic pairing":      "Micro. pair",
    "Field theory & RG":        "FT & RG",
    "Response & transport":     "Resp. & Trans.",
    "Topological":              "Topol.",
    "Junction & interface":     "Junction",
    "Many-body & correlation":  "Many-body",
    "Quantum circuits & info":  "Quantum",
    "Other methods":            "Other",
}

# ── colour maps ───────────────────────────────────────────────────────────────
FAM_COLORS  = {f: plt.cm.tab20(i / max(len(FAMILY_ORDER) - 1, 1)) for i, f in enumerate(FAMILY_ORDER)}
MECH_COLORS = {m: plt.cm.Set2(i / (len(MECH_ORDER)-1)) for i, m in enumerate(MECH_ORDER)}
EVID_COLORS = {e: plt.cm.Set3(i / (len(EVIDENCE_CATS)-1)) for i, e in enumerate(EVIDENCE_CATS)}

# ── load data ─────────────────────────────────────────────────────────────────
with open(CSV_PATH, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))


def explode_evidence(rows):
    """Yield (category, row) for every evidence tag (multi-label)."""
    for r in rows:
        ev = r["evidence"].strip()
        if ev and ev != "none":
            for cat in ev.split(" | "):
                cat = cat.strip()
                if cat:
                    yield cat, r


# ── figure layout ─────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(19, 12))
fig.suptitle(
    "Figure 2 – Data Statistics: Family · Mechanism · Evidence",
    fontsize=15, fontweight="bold", y=0.995,
)
plt.subplots_adjust(hspace=0.40, wspace=0.40)


# ─────────────────────────────────────────────────────────────────────────────
# 2.1  Family distribution
# ─────────────────────────────────────────────────────────────────────────────
ax = axes[0, 0]
fam_counts = Counter(r["family"] for r in rows)
sorted_fams = sorted(FAMILY_ORDER, key=lambda f: fam_counts.get(f, 0))
vals   = [fam_counts.get(f, 0) for f in sorted_fams]
colors = [FAM_COLORS[f]        for f in sorted_fams]

bars = ax.barh(sorted_fams, vals, color=colors, edgecolor="white", linewidth=0.5, height=0.72)
for bar, v in zip(bars, vals):
    if v > 0:
        ax.text(v + max(vals) * 0.01, bar.get_y() + bar.get_height() / 2,
                str(v), va="center", ha="left", fontsize=8.5)
ax.set_xlabel("Number of papers", fontsize=9)
ax.set_title("Fig. 2.1 – Superconductor Family", fontsize=10, fontweight="bold")
ax.set_xlim(0, max(vals) * 1.16)
ax.grid(axis="x", alpha=0.3, linewidth=0.5)
ax.spines[["top", "right"]].set_visible(False)


# ─────────────────────────────────────────────────────────────────────────────
# 2.2  Mechanism distribution
# ─────────────────────────────────────────────────────────────────────────────
ax = axes[0, 1]
mech_counts  = Counter(r["mechanism"] for r in rows)
sorted_mechs = sorted(MECH_ORDER, key=lambda m: mech_counts.get(m, 0))
mvals   = [mech_counts.get(m, 0)   for m in sorted_mechs]
mcolors = [MECH_COLORS[m]          for m in sorted_mechs]
mlabels = [MECH_SHORT[m]           for m in sorted_mechs]

mbars = ax.barh(mlabels, mvals, color=mcolors, edgecolor="white", linewidth=0.5, height=0.72)
for bar, v in zip(mbars, mvals):
    if v > 0:
        ax.text(v + max(mvals) * 0.01, bar.get_y() + bar.get_height() / 2,
                str(v), va="center", ha="left", fontsize=8.5)
ax.set_xlabel("Number of papers", fontsize=9)
ax.set_title("Fig. 2.2 – Mechanism (top score)", fontsize=10, fontweight="bold")
ax.set_xlim(0, max(mvals) * 1.16)
ax.grid(axis="x", alpha=0.3, linewidth=0.5)
ax.spines[["top", "right"]].set_visible(False)


# ─────────────────────────────────────────────────────────────────────────────
# 2.3  Evidence distribution (exploded, multi-label)
# ─────────────────────────────────────────────────────────────────────────────
ax = axes[0, 2]
ev_counts   = Counter(cat for cat, _ in explode_evidence(rows))
none_count  = sum(1 for r in rows if r["evidence"].strip() == "none")
sorted_evid = sorted(EVIDENCE_CATS, key=lambda e: ev_counts.get(e, 0))
evals   = [ev_counts.get(e, 0) for e in sorted_evid]
ecolors = [EVID_COLORS[e]      for e in sorted_evid]
elabels = [EVID_SHORT[e]       for e in sorted_evid]

ebars = ax.barh(elabels, evals, color=ecolors, edgecolor="white", linewidth=0.5, height=0.72)
for bar, v in zip(ebars, evals):
    if v > 0:
        ax.text(v + max(evals) * 0.01, bar.get_y() + bar.get_height() / 2,
                str(v), va="center", ha="left", fontsize=8.5)
ax.set_xlabel("Papers with tag (multi-label)", fontsize=9)
ax.set_title(
    f"Fig. 2.3 – Theoretical Evidence\n(no-theory papers: {none_count})",
    fontsize=10, fontweight="bold",
)
ax.set_xlim(0, max(evals) * 1.16)
ax.grid(axis="x", alpha=0.3, linewidth=0.5)
ax.spines[["top", "right"]].set_visible(False)


# ─────────────────────────────────────────────────────────────────────────────
# 2.4  Publication timeline stacked by family
# ─────────────────────────────────────────────────────────────────────────────
ax = axes[1, 0]
STACK_FAMS = [
    "cuprate", "iron-based", "heavy-fermion", "nickelate",
    "kagome", "hydrogen", "ruthenate", "elemental", "MgB2", "2D", "organic",
]
years = list(range(1956, 2025))
year_fam   = {f: Counter() for f in STACK_FAMS}
year_total = Counter()
for r in rows:
    if r["year"].strip().isdigit():
        y = int(r["year"])
        year_total[y] += 1
        f = r["family"]
        if f in STACK_FAMS:
            year_fam[f][y] += 1

bottoms = np.zeros(len(years))
for fam in STACK_FAMS:
    fvals = np.array([year_fam[fam].get(y, 0) for y in years], dtype=float)
    ax.bar(years, fvals, bottom=bottoms, color=FAM_COLORS[fam],
           label=fam, width=1.0, edgecolor="none")
    bottoms += fvals

# remaining (other / unknown)
rest = np.array([max(year_total.get(y, 0) - bottoms[i], 0) for i, y in enumerate(years)])
ax.bar(years, rest, bottom=bottoms, color="#bbbbbb",
       label="other/unknown", width=1.0, edgecolor="none")

ax.set_xlabel("Year", fontsize=9)
ax.set_ylabel("Number of papers", fontsize=9)
ax.set_title("Fig. 2.4 – Publication Timeline by Family", fontsize=10, fontweight="bold")
ax.legend(fontsize=6.5, loc="upper left", ncol=2, framealpha=0.75)
ax.set_xlim(1955, 2025)
ax.grid(axis="y", alpha=0.3, linewidth=0.5)
ax.spines[["top", "right"]].set_visible(False)


# ─────────────────────────────────────────────────────────────────────────────
# 2.5  Publication timeline stacked by mechanism
# ─────────────────────────────────────────────────────────────────────────────
ax = axes[1, 1]
years = list(range(1956, 2025))
year_mech = {m: Counter() for m in MECH_ORDER}
for r in rows:
    if r["year"].strip().isdigit():
        y = int(r["year"])
        m = r["mechanism"]
        if m in MECH_ORDER:
            year_mech[m][y] += 1

bottoms_m = np.zeros(len(years))
for mech in MECH_ORDER:
    mvals = np.array([year_mech[mech].get(y, 0) for y in years], dtype=float)
    ax.bar(years, mvals, bottom=bottoms_m, color=MECH_COLORS[mech],
           label=MECH_SHORT[mech], width=1.0, edgecolor="none")
    bottoms_m += mvals

ax.set_xlabel("Year", fontsize=9)
ax.set_ylabel("Number of papers", fontsize=9)
ax.set_title("Fig. 2.5 – Publication Timeline by Mechanism", fontsize=10, fontweight="bold")
ax.legend(fontsize=6.5, loc="upper left", ncol=2, framealpha=0.75)
ax.set_xlim(1955, 2025)
ax.grid(axis="y", alpha=0.3, linewidth=0.5)
ax.spines[["top", "right"]].set_visible(False)


# ─────────────────────────────────────────────────────────────────────────────
# 2.6  Publication timeline stacked by evidence
# ─────────────────────────────────────────────────────────────────────────────
ax = axes[1, 2]
year_evid = {e: Counter() for e in EVIDENCE_CATS}
for cat, r in explode_evidence(rows):
    if r["year"].strip().isdigit() and cat in EVIDENCE_CATS:
        year_evid[cat][int(r["year"])] += 1

bottoms_e = np.zeros(len(years))
for evid in EVIDENCE_CATS:
    evals = np.array([year_evid[evid].get(y, 0) for y in years], dtype=float)
    ax.bar(years, evals, bottom=bottoms_e, color=EVID_COLORS[evid],
           label=EVID_SHORT[evid], width=1.0, edgecolor="none")
    bottoms_e += evals

ax.set_xlabel("Year", fontsize=9)
ax.set_ylabel("Papers with tag (multi-label)", fontsize=9)
ax.set_title("Fig. 2.6 – Publication Timeline by Evidence", fontsize=10, fontweight="bold")
ax.legend(fontsize=6.5, loc="upper left", ncol=2, framealpha=0.75)
ax.set_xlim(1955, 2025)
ax.grid(axis="y", alpha=0.3, linewidth=0.5)
ax.spines[["top", "right"]].set_visible(False)


# ── save ──────────────────────────────────────────────────────────────────────
plt.savefig(OUT_PATH, dpi=150, bbox_inches="tight")
print(f"Saved → {OUT_PATH}")
plt.close()
