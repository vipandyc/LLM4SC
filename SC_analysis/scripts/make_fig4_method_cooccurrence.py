#!/usr/bin/env python3
"""Method co-occurrence network (nodes = methods, edges = co-use in papers).

Uses VOSviewer-style **association strength** as edge weight:
    a_ij = c_ij / (c_i * c_j / (2 * E))
where c_i = #papers using method i and c_ij = #papers using both.
Nodes are sized by usage count, coloured by a hand-curated big-bucket category.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from fig_common import CSV_PATH

OUT_DIR = Path(__file__).parent.parent / "output" / "figures_4"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ── manual big-bucket categorisation of the 128 method columns ────────────────
CATEGORY = {
    "computation": {
        "DFT", "DFPT", "Electron-Phonon Coupling Calculations",
        "Band Structure Calculations", "Electronic Structure Calculations",
        "Phonon Calculations", "BCS / Eliashberg", "DMFT", "QMC",
        "Monte Carlo Simulations", "Exact Diagonalization", "DMRG", "NRG",
        "FEM", "Numerical Simulations", "Tight-Binding Model",
        "Fermi Surface Calculations",
    },
    "theory": {
        "Ginzburg-Landau Theory", "Mean-Field Theory", "Effective Field Theory",
        "Symmetry Analysis", "Linear / Nonlinear Response Theory",
        "Topological Band/Field Theory", "Scaling Analysis",
        "Model Hamiltonian Analysis", "Renormalization Group", "RPA",
        "Perturbation Theory", "Andreev Theory", "Josephson Junction Theory",
        "Phenomenological / Analytical Modeling", "BdG Theory", "Floquet Theory",
        "Bulk-Boundary Correspondence", "Luttinger Liquid Theory",
        "Bean Critical-State Model", "Proximity Effect Theory", "London Theory",
        "Percolation Theory", "Bosonization", "Linear Stability Analysis",
        "Effective Hamiltonian", "Phase Diagram Analysis",
        "AdS/CFT (Holographic Duality)", "RVB Theory", "Two-Fluid Model",
        "Collective Pinning Theory", "Fermi Liquid Theory", "Scattering Theory",
        "Collective Mode Analysis", "Input-Output Theory",
        "Linearized Gap Equation", "Asymptotic Analysis",
        "Green's Function Formalism", "Quantum Measurement Theory",
        "Nonlinear Sigma Model", "t-J Model", "Circuit Quantization",
        "Drude Model", "Anderson Localization Theory",
    },
    "spectroscopy": {
        "ARPES", "XPS", "XAS", "RIXS", "EELS", "FTIR",
        "Infrared / Optical Spectroscopy", "Microwave Spectroscopy",
        "Mossbauer Spectroscopy", "ESR/EPR", "Raman Spectroscopy", "NMR", "NQR",
        "muSR", "Point-Contact Spectroscopy", "Andreev Reflection Spectroscopy",
        "Temperature-Dependent Spectroscopy",
    },
    "microscopy/diffraction": {
        "TEM", "STM/STS", "XRD", "SEM", "Electron Microscopy (General)",
        "Electron Diffraction", "RHEED", "AFM", "MFM",
        "Scanning SQUID Microscopy", "Magneto-Optical Imaging", "EDX",
        "Electron Microprobe Analysis",
    },
    "transport/magnetics": {
        "Electrical Resistivity / Transport", "SQUID Magnetometry",
        "Magnetic Susceptibility / Magnetization", "Neutron Scattering",
        "Specific Heat / Heat Capacity", "Tc Measurement", "Hc2 Measurement",
        "Jc Measurement", "Magnetoresistance / Magnetotransport", "Hall Effect",
        "Quantum Oscillations", "Thermal Conductivity", "Thermal Expansion",
        "Thermoelectric / Seebeck", "I-V Measurements",
        "Electrical Resistivity Under Pressure",
    },
    "conditions/devices": {
        "Temperature-Dependent Measurements", "Pressure-Dependent Measurements",
        "Magnetic-Field-Dependent Measurements",
        "Magnetic-Field-Dependent Transport", "Low-Temperature Measurements",
        "Josephson Junction Measurements", "Circuit QED / Superconducting Qubits",
        "SNSPD", "Device Fabrication", "AC Loss Measurements", "MEG", "MRI",
        "DLS", "Electrostatic Gating", "Cryogenic Testing",
    },
    "synthesis": {
        "PLD", "MBE", "CVD", "Epitaxial Thin Film Growth",
        "Sample Synthesis / Characterization", "TGA", "DTA",
    },
}
CAT_COLOR = {
    "computation":          "#4c78a8",
    "theory":               "#e45756",
    "spectroscopy":         "#54a24b",
    "microscopy/diffraction":"#72b7b2",
    "transport/magnetics":  "#f58518",
    "conditions/devices":   "#b279a2",
    "synthesis":            "#9d755d",
    "other":                "#bab0ac",
}


def cat_of(method: str) -> str:
    for c, members in CATEGORY.items():
        if method in members:
            return c
    return "other"


def main() -> None:
    df = pd.read_csv(CSV_PATH)
    cols = list(df.columns)
    method_cols = cols[cols.index("DFT"):cols.index("other")]
    X = df[method_cols].fillna(0).astype(int).to_numpy()
    n_papers, n_methods = X.shape
    counts = X.sum(axis=0)

    # co-occurrence matrix (methods × methods)
    co = X.T @ X
    np.fill_diagonal(co, 0)

    # association strength
    E = co.sum() / 2  # total co-occ pairs
    denom = np.outer(counts, counts) / (2 * E + 1e-9)
    denom[denom == 0] = np.nan
    assoc = co / denom
    assoc = np.nan_to_num(assoc, nan=0.0)

    # --- filter nodes & edges -------------------------------------------------
    MIN_USE = 40          # node must appear in >= N papers
    MIN_ASSOC = 2.0       # association strength >= 2 means "2x more than expected"
    MIN_CO = 15           # and they must actually co-occur >= N times
    TOP_EDGES_PER_NODE = 4  # backbone: keep only the strongest K edges per node
    keep = np.where(counts >= MIN_USE)[0]
    names = [method_cols[i] for i in keep]
    sub_assoc = assoc[np.ix_(keep, keep)]
    sub_co = co[np.ix_(keep, keep)]
    sub_cnt = counts[keep]

    # candidate edges pass assoc + co thresholds
    cand = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if sub_assoc[i, j] >= MIN_ASSOC and sub_co[i, j] >= MIN_CO:
                cand.append((i, j, float(sub_assoc[i, j]), int(sub_co[i, j])))

    # disparity-style backbone: for each node, keep its top-K strongest edges
    keep_edges: set[tuple[int, int]] = set()
    adj_by_node: dict[int, list[tuple[int, float]]] = {i: [] for i in range(len(names))}
    for i, j, w, c in cand:
        adj_by_node[i].append((j, w))
        adj_by_node[j].append((i, w))
    for i, lst in adj_by_node.items():
        lst.sort(key=lambda x: -x[1])
        for j, _ in lst[:TOP_EDGES_PER_NODE]:
            a, b = (i, j) if i < j else (j, i)
            keep_edges.add((a, b))

    g = nx.Graph()
    for i, m in enumerate(names):
        g.add_node(m, cat=cat_of(m), count=int(sub_cnt[i]))
    for i, j, w, c in cand:
        a, b = (i, j) if i < j else (j, i)
        if (a, b) in keep_edges:
            g.add_edge(names[i], names[j], weight=w, raw=c)

    # drop isolates
    iso = [n for n in g.nodes() if g.degree(n) == 0]
    g.remove_nodes_from(iso)
    print(f"kept {g.number_of_nodes()} methods, {g.number_of_edges()} edges "
          f"(from {n_methods} methods; use>={MIN_USE}, assoc>={MIN_ASSOC}, "
          f"co>={MIN_CO}, top-{TOP_EDGES_PER_NODE} backbone)")

    # layout -- force directed with weight
    k = 1.0 / np.sqrt(max(1, g.number_of_nodes()))
    pos = nx.spring_layout(g, k=k, iterations=200, seed=3,
                           weight="weight")

    # draw
    fig = plt.figure(figsize=(15, 12), dpi=160, facecolor="white")
    ax = fig.add_axes([0.02, 0.03, 0.78, 0.94])
    ax.set_facecolor("#f7f8fb")
    ax.set_axis_off()

    # edges: width ∝ log(assoc), alpha ∝ assoc
    max_w = max((d["weight"] for _, _, d in g.edges(data=True)), default=1.0)
    for u, v, d in g.edges(data=True):
        w = d["weight"]
        lw = 0.35 + 1.8 * (np.log1p(w) / np.log1p(max_w))
        ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]],
                color="#9aa3b2", lw=lw, alpha=min(0.75, 0.25 + 0.45 * w / max_w),
                zorder=1)

    # nodes -- size ∝ sqrt(count)
    for cat, color in CAT_COLOR.items():
        nodes = [n for n in g.nodes() if g.nodes[n]["cat"] == cat]
        if not nodes:
            continue
        sizes = [40 + 55 * np.sqrt(g.nodes[n]["count"]) for n in nodes]
        xs = [pos[n][0] for n in nodes]
        ys = [pos[n][1] for n in nodes]
        ax.scatter(xs, ys, s=sizes, c=color, edgecolors="#0b1220",
                   linewidths=0.5, alpha=0.92, zorder=2, label=cat)

    # label every surviving node
    for n in g.nodes():
        ax.text(pos[n][0], pos[n][1], n, fontsize=6.8, ha="center", va="center",
                zorder=3, color="#0b1220",
                bbox=dict(boxstyle="round,pad=0.10", fc="white",
                          ec="none", alpha=0.80))

    ax.legend(loc="center left", bbox_to_anchor=(1.00, 0.5), frameon=False,
              fontsize=10, title="Method category", title_fontsize=11)
    ax.set_title(
        f"Method co-occurrence backbone "
        f"({g.number_of_nodes()} methods used in ≥{MIN_USE} papers;  "
        f"edges: top-{TOP_EDGES_PER_NODE} per node, assoc ≥ {MIN_ASSOC:g}, co-occ ≥ {MIN_CO})\n"
        f"edge width / opacity ∝ log(association strength);  "
        f"node size ∝ √(usage count);  colour = method category",
        fontsize=12,
    )

    out = OUT_DIR / "fig4_method_cooccurrence.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


if __name__ == "__main__":
    main()
