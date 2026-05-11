#!/usr/bin/env python3
"""Chord / ribbon diagram of method-category → method-category internal citations.

For every internal citation edge A → B we spread one unit of citation across
the (cat_A, cat_B) pairs using

    p(cat | paper) = #methods_paper_in_cat / #methods_paper_total

so ``M[i, j] += p(cat_i | A) * p(cat_j | B)``.  The resulting K×K matrix is the
expected number of category-level citations if we randomly sampled one method
from each paper.  Drawn as a polar chord using only matplotlib.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.path as mpath
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from fig_common import CSV_PATH

OUT_DIR = Path(__file__).parent.parent / "output" / "figures_4"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ── shared method categorisation (kept in sync with make_fig4_method_cooccurrence) ──
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
CAT_ORDER = [
    "computation", "theory", "spectroscopy", "microscopy/diffraction",
    "transport/magnetics", "conditions/devices", "synthesis",
]
CAT_SHORT = {
    "computation":           "Computation",
    "theory":                "Theory",
    "spectroscopy":          "Spectroscopy",
    "microscopy/diffraction":"Micro/Diff",
    "transport/magnetics":   "Transport/Mag",
    "conditions/devices":    "Cond/Devices",
    "synthesis":             "Synthesis",
}
CAT_COLOR = {
    "computation":           "#4c78a8",
    "theory":                "#e45756",
    "spectroscopy":          "#54a24b",
    "microscopy/diffraction":"#72b7b2",
    "transport/magnetics":   "#f58518",
    "conditions/devices":    "#b279a2",
    "synthesis":             "#9d755d",
}


def parse_cites(s):
    if not isinstance(s, str) or not s.strip():
        return []
    try:
        return list(json.loads(s))
    except Exception:
        return []


def bezier_ribbon(ax, theta0a, theta0b, theta1a, theta1b, r, color, alpha):
    p0 = np.array([r * np.cos(theta0a), r * np.sin(theta0a)])
    p1 = np.array([r * np.cos(theta0b), r * np.sin(theta0b)])
    p2 = np.array([r * np.cos(theta1a), r * np.sin(theta1a)])
    p3 = np.array([r * np.cos(theta1b), r * np.sin(theta1b)])
    c0 = np.array([0.0, 0.0])
    verts = [tuple(p1), tuple(c0), tuple(p2), tuple(p3),
             tuple(c0), tuple(p0), tuple(p1)]
    codes = [
        mpath.Path.MOVETO,
        mpath.Path.CURVE3, mpath.Path.CURVE3,
        mpath.Path.LINETO,
        mpath.Path.CURVE3, mpath.Path.CURVE3,
        mpath.Path.CLOSEPOLY,
    ]
    path = mpath.Path(verts, codes)
    ax.add_patch(mpatches.PathPatch(path, facecolor=color, edgecolor="none",
                                    alpha=alpha, linewidth=0))


def build_matrix():
    df = pd.read_csv(CSV_PATH)
    cols = list(df.columns)
    method_cols = cols[cols.index("DFT"):cols.index("other")]

    # per-paper distribution over categories
    K = len(CAT_ORDER)
    cat_idx = {c: i for i, c in enumerate(CAT_ORDER)}
    # method -> cat index (None if "other")
    meth_to_cat = {}
    for m in method_cols:
        for c, members in CATEGORY.items():
            if m in members:
                meth_to_cat[m] = cat_idx[c]
                break

    # build p[paper, cat]
    X = df[method_cols].fillna(0).astype(int).to_numpy()
    P = np.zeros((len(df), K), dtype=float)
    for j, m in enumerate(method_cols):
        c = meth_to_cat.get(m)
        if c is None:
            continue
        P[:, c] += X[:, j]
    # normalise rows; papers with zero categorised methods contribute nothing
    row_sum = P.sum(axis=1, keepdims=True)
    P_norm = np.divide(P, row_sum, out=np.zeros_like(P), where=row_sum > 0)

    id_to_row = {pid: i for i, pid in enumerate(df["id"])}

    # aggregate citation flows
    M = np.zeros((K, K), dtype=float)
    total_edges = 0
    for i, cites in enumerate(df["outgoing_internal_citing_papers"].map(parse_cites)):
        pa = P_norm[i]
        if pa.sum() == 0:
            continue
        for tgt in cites:
            j = id_to_row.get(tgt)
            if j is None:
                continue
            pb = P_norm[j]
            if pb.sum() == 0:
                continue
            M += np.outer(pa, pb)
            total_edges += 1
    return M, CAT_ORDER, total_edges


def main() -> None:
    M, order, total_edges = build_matrix()
    K = len(order)

    out = M.sum(axis=1)
    inc = M.sum(axis=0)
    deg = out + inc

    GAP = np.deg2rad(2.5)
    total_gap = GAP * K
    total_arc = 2 * np.pi - total_gap
    widths = deg / deg.sum() * total_arc

    starts = np.zeros(K)
    cur = np.pi / 2
    for i in range(K):
        starts[i] = cur
        cur -= widths[i] + GAP

    R_OUT = 1.00
    R_RIB = 0.92

    sub_start, sub_end = {}, {}
    for i in range(K):
        out_total = out[i]
        inc_total = inc[i]
        inner_arc = widths[i]
        out_arc = inner_arc * (out_total / (out_total + inc_total)) if (out_total + inc_total) else 0
        in_arc = inner_arc - out_arc

        a = starts[i]
        for j in range(K):
            frac = M[i, j] / out_total if out_total else 0
            w = out_arc * frac
            sub_start[(i, "out", j)] = a
            sub_end[(i, "out", j)] = a - w
            a -= w
        for j in range(K):
            frac = M[j, i] / inc_total if inc_total else 0
            w = in_arc * frac
            sub_start[(i, "in", j)] = a
            sub_end[(i, "in", j)] = a - w
            a -= w

    fig, ax = plt.subplots(figsize=(11, 11), dpi=160)
    ax.set_xlim(-1.40, 1.40)
    ax.set_ylim(-1.40, 1.40)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.set_facecolor("white")

    for i, c in enumerate(order):
        theta1 = np.rad2deg(starts[i] - widths[i])
        theta2 = np.rad2deg(starts[i])
        wedge = mpatches.Wedge(
            (0, 0), R_OUT, theta1, theta2, width=0.06,
            facecolor=CAT_COLOR[c], edgecolor="white", linewidth=0.8, zorder=3,
        )
        ax.add_patch(wedge)
        mid = starts[i] - widths[i] / 2
        lr = 1.10
        ha = "left" if np.cos(mid) > 0 else "right"
        rot = np.rad2deg(mid)
        if np.cos(mid) < 0:
            rot += 180
        ax.text(lr * np.cos(mid), lr * np.sin(mid),
                f"{CAT_SHORT[c]}\nout {out[i]:.0f} / in {inc[i]:.0f}",
                ha=ha, va="center", fontsize=9, rotation=rot,
                rotation_mode="anchor", color="#0b1220")

    order_edges = [(i, j, M[i, j]) for i in range(K) for j in range(K) if M[i, j] > 0]
    order_edges.sort(key=lambda x: x[2])
    m_max = max(v for _, _, v in order_edges)
    for i, j, v in order_edges:
        a0 = sub_start[(i, "out", j)]
        a1 = sub_end[(i, "out", j)]
        b0 = sub_start[(j, "in", i)]
        b1 = sub_end[(j, "in", i)]
        color = CAT_COLOR[order[i]]
        alpha = 0.12 + 0.55 * (v / m_max)
        if i == j:
            alpha = min(0.80, alpha + 0.15)
        bezier_ribbon(ax, a0, a1, b0, b1, R_RIB, color, alpha)

    ax.set_title(
        f"Method-category → method-category internal citations "
        f"(weighted by p(cat|paper);  {total_edges:,} edges aggregated)\n"
        f"ribbon colour = citing category;  arc length ∝ total involvement",
        fontsize=12, pad=14,
    )

    out_path = OUT_DIR / "fig4_method_chord.png"
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print("wrote", out_path)

    with open(OUT_DIR / "fig4_method_chord_matrix.csv", "w") as f:
        f.write("src_category," + ",".join(order) + "\n")
        for i, c in enumerate(order):
            f.write(c + "," + ",".join(f"{v:.3f}" for v in M[i]) + "\n")


if __name__ == "__main__":
    main()
