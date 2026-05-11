#!/usr/bin/env python3
"""Fig. 2.6_2 – Publication timeline stacked by experimental evidence (multi-label)."""
from fig_common import *
import numpy as np
import matplotlib.pyplot as plt

METHODS = [
    "Electrical Resistivity", "Magnetic Susceptibility", "Tc Measurement",
    "Magnetoresistance", "Microwave Spectroscopy", "Infrared / Optical Spectroscopy",
    "SQUID", "Specific Heat", "Neutron Scattering", "ARPES",
    "Josephson Junction", "STM/STS", "NMR", "Hall Effect", "Raman",
    "muSR", "Thermal Conductivity", "Quantum Oscillation", "XAS", "RIXS",
    "EELS", "RHEED",
]
COLORS = {m: plt.cm.tab20(i / (len(METHODS) - 1)) for i, m in enumerate(METHODS)}

def parse(val):
    return [] if val.strip() in ("none", "") else [m.strip() for m in val.split(" | ")]

rows = load_rows()
year_method = {m: Counter() for m in METHODS}
for r in rows:
    if r["year"].strip().isdigit():
        y = int(r["year"])
        for m in parse(r.get("evidence_experiment", "none")):
            if m in year_method:
                year_method[m][y] += 1

bottoms = np.zeros(len(YEARS))
fig, ax = plt.subplots(figsize=(11, 5))
for m in METHODS:
    vals = np.array([year_method[m].get(y, 0) for y in YEARS], dtype=float)
    ax.bar(YEARS, vals, bottom=bottoms, color=COLORS[m], label=m, width=1.0, edgecolor="none")
    bottoms += vals

ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("Papers with method (multi-label)", fontsize=11)
ax.set_title("Fig. 2.6_2 – Publication Timeline by Experimental Evidence", fontsize=13, fontweight="bold")
ax.legend(fontsize=6.5, loc="upper left", ncol=2, framealpha=0.75)
ax.set_xlim(1955, 2025)
ax.grid(axis="y", alpha=0.3, linewidth=0.5)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / "fig2_6_2.png", dpi=150, bbox_inches="tight")
print("Saved → fig2_6_2.png")
plt.close()
