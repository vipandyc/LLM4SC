#!/usr/bin/env python3
"""Chord / ribbon diagram of mechanism → mechanism internal citations.

Builds a K×K matrix M where M[i, j] = number of internal citation edges
whose source paper has mechanism i and whose target paper has mechanism j.
Draws it as a polar chord diagram using only matplotlib primitives
(no extra deps).
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
from fig_common import MECH_ORDER, MECH_COLORS, MECH_SHORT, CSV_PATH

OUT_DIR = Path(__file__).parent.parent / "output" / "figures_4"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_cites(s: str) -> list[str]:
    if not isinstance(s, str) or not s.strip():
        return []
    try:
        return list(json.loads(s))
    except Exception:
        return []


def build_matrix() -> tuple[np.ndarray, list[str]]:
    df = pd.read_csv(CSV_PATH)
    mech = {pid: m for pid, m in zip(df["id"], df["mechanism"])}

    K = len(MECH_ORDER)
    idx = {m: i for i, m in enumerate(MECH_ORDER)}
    M = np.zeros((K, K), dtype=float)
    for pid, cites in zip(df["id"], df["outgoing_internal_citing_papers"].map(parse_cites)):
        ms = mech.get(pid)
        if ms not in idx:
            continue
        i = idx[ms]
        for t in cites:
            mt = mech.get(t)
            if mt not in idx:
                continue
            M[i, idx[mt]] += 1
    return M, MECH_ORDER


def bezier_ribbon(ax, theta0a, theta0b, theta1a, theta1b, r, color, alpha):
    """Quadratic bezier ribbon between two arcs at radius r."""
    # control points pull toward origin to bend ribbons
    p0 = np.array([r * np.cos(theta0a), r * np.sin(theta0a)])
    p1 = np.array([r * np.cos(theta0b), r * np.sin(theta0b)])
    p2 = np.array([r * np.cos(theta1a), r * np.sin(theta1a)])
    p3 = np.array([r * np.cos(theta1b), r * np.sin(theta1b)])
    c0 = np.array([0.0, 0.0])  # quadratic control point -> bend toward center
    verts = [
        tuple(p1),            # start of outgoing arc end
        tuple(c0), tuple(p2), # quad curve to start of incoming arc
        tuple(p3),            # along incoming arc (straight)
        tuple(c0), tuple(p0), # quad curve back
        tuple(p1),
    ]
    codes = [
        mpath.Path.MOVETO,
        mpath.Path.CURVE3, mpath.Path.CURVE3,
        mpath.Path.LINETO,
        mpath.Path.CURVE3, mpath.Path.CURVE3,
        mpath.Path.CLOSEPOLY,
    ]
    path = mpath.Path(verts, codes)
    patch = mpatches.PathPatch(path, facecolor=color, edgecolor="none",
                               alpha=alpha, linewidth=0)
    ax.add_patch(patch)


def main() -> None:
    M, order = build_matrix()
    K = len(order)
    total = M.sum()
    if total == 0:
        raise SystemExit("no edges")

    # row / col totals (outgoing / incoming for each mechanism) and
    # each mechanism's arc width = its total involvement (out+in).
    out = M.sum(axis=1)
    inc = M.sum(axis=0)
    deg = out + inc  # each edge counted twice globally

    GAP = np.deg2rad(2.0)   # gap between sectors
    total_gap = GAP * K
    total_arc = 2 * np.pi - total_gap
    widths = deg / deg.sum() * total_arc

    # sector start angles
    starts = np.zeros(K)
    cur = np.pi / 2  # start at top
    for i in range(K):
        starts[i] = cur
        cur -= widths[i] + GAP  # go clockwise

    R_OUT = 1.00
    R_RIB = 0.92   # inner radius where ribbons meet

    # layout sub-arcs on each sector: for each mechanism, split its arc into
    # slots proportional to edges going to each other mechanism (and itself)
    sub_start = {}  # (i, 'out', j) -> start angle ; (i, 'in', j) -> start angle
    sub_end = {}
    for i in range(K):
        # order within the sector: first half outgoing, second half incoming
        # outgoing slots (to j), ordered by MECH_ORDER
        out_total = out[i]
        inc_total = inc[i]
        inner_arc = widths[i]
        # split sector into out-part and in-part proportional to out/inc
        out_arc = inner_arc * (out_total / (out_total + inc_total)) if (out_total + inc_total) else 0
        in_arc = inner_arc - out_arc

        a = starts[i]
        # outgoing slots (clockwise)
        for j in range(K):
            frac = M[i, j] / out_total if out_total else 0
            w = out_arc * frac
            sub_start[(i, "out", j)] = a
            sub_end[(i, "out", j)] = a - w
            a -= w
        # incoming slots (clockwise) — note arc is continuous
        for j in range(K):
            frac = M[j, i] / inc_total if inc_total else 0
            w = in_arc * frac
            sub_start[(i, "in", j)] = a
            sub_end[(i, "in", j)] = a - w
            a -= w

    # --- draw -----------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(11, 11), dpi=160)
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-1.35, 1.35)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.set_facecolor("white")

    # sector arcs
    for i, m in enumerate(order):
        theta1 = np.rad2deg(starts[i] - widths[i])  # end (smaller)
        theta2 = np.rad2deg(starts[i])              # start (larger)
        wedge = mpatches.Wedge(
            (0, 0), R_OUT, theta1, theta2, width=0.06,
            facecolor=MECH_COLORS[m], edgecolor="white", linewidth=0.8,
            zorder=3,
        )
        ax.add_patch(wedge)
        # label
        mid = starts[i] - widths[i] / 2
        lr = 1.10
        ha = "left" if np.cos(mid) > 0 else "right"
        rot = np.rad2deg(mid)
        if np.cos(mid) < 0:
            rot += 180
        ax.text(lr * np.cos(mid), lr * np.sin(mid),
                f"{MECH_SHORT.get(m, m)}\nout {int(out[i])} / in {int(inc[i])}",
                ha=ha, va="center", fontsize=9, rotation=rot,
                rotation_mode="anchor", color="#0b1220")

    # ribbons -- alpha proportional to flow magnitude
    order_edges = [(i, j, M[i, j]) for i in range(K) for j in range(K) if M[i, j] > 0]
    order_edges.sort(key=lambda x: x[2])  # small first => big on top
    m_max = max(v for _, _, v in order_edges)
    for i, j, v in order_edges:
        if v <= 0:
            continue
        a0 = sub_start[(i, "out", j)]
        a1 = sub_end[(i, "out", j)]
        b0 = sub_start[(j, "in", i)]
        b1 = sub_end[(j, "in", i)]
        color = MECH_COLORS[order[i]]
        alpha = 0.12 + 0.55 * (v / m_max)
        if i == j:
            alpha = min(0.80, alpha + 0.15)
        bezier_ribbon(ax, a0, a1, b0, b1, R_RIB, color, alpha)

    ax.set_title(
        f"Mechanism → mechanism internal citations "
        f"(total edges: {int(total):,})\n"
        f"ribbon colour = citing mechanism;  arc length ∝ total involvement",
        fontsize=12, pad=14,
    )

    out_path = OUT_DIR / "fig4_mechanism_chord.png"
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print("wrote", out_path)

    # also dump the raw matrix for reference
    with open(OUT_DIR / "fig4_mechanism_chord_matrix.csv", "w") as f:
        f.write("src_mechanism," + ",".join(order) + "\n")
        for i, m in enumerate(order):
            f.write(m + "," + ",".join(str(int(v)) for v in M[i]) + "\n")


if __name__ == "__main__":
    main()
