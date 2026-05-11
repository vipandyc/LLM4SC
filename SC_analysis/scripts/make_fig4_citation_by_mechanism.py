#!/usr/bin/env python3
"""Static citation network, nodes colored by mechanism.

Reads SC_final_data_5k.csv.  Each paper is a node; edges are internal
citations parsed from ``outgoing_internal_citing_papers``.  Nodes are coloured
by ``mechanism``; intra-mechanism edges are light, cross-mechanism edges are
darker so the cross-community citation structure is visible.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
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


def main() -> None:
    df = pd.read_csv(CSV_PATH)
    df["mech"] = df["mechanism"].where(df["mechanism"].isin(MECH_ORDER), "other")

    # --- build graph ----------------------------------------------------------
    g = nx.DiGraph()
    mech_of = dict(zip(df["id"], df["mech"]))
    for pid, mech in mech_of.items():
        g.add_node(pid, mech=mech)
    for pid, cites in zip(df["id"], df["outgoing_internal_citing_papers"].map(parse_cites)):
        for t in cites:
            if t in mech_of:
                g.add_edge(pid, t)

    print(f"full: nodes={g.number_of_nodes()}  edges={g.number_of_edges()}")

    # --- prune: keep only well-connected papers -------------------------------
    MIN_DEG = 20
    deg = {n: g.in_degree(n) + g.out_degree(n) for n in g.nodes()}
    keep = {n for n, d in deg.items() if d >= MIN_DEG}
    # drop nodes with unknown / "other" mechanism from the visualization
    keep = {n for n in keep if g.nodes[n]["mech"] in MECH_ORDER}
    g = g.subgraph(keep).copy()
    print(f"pruned (deg>={MIN_DEG}, mechanism in MECH_ORDER): "
          f"nodes={g.number_of_nodes()}  edges={g.number_of_edges()}")

    # --- layout: seed by mechanism so communities separate --------------------
    # place each mechanism's group center on a circle, then spring-layout around.
    n_m = len(MECH_ORDER)
    group_center = {
        m: np.array([np.cos(2 * np.pi * i / n_m), np.sin(2 * np.pi * i / n_m)]) * 1.2
        for i, m in enumerate(MECH_ORDER)
    }
    rng = np.random.default_rng(11)
    initial = {
        n: group_center[g.nodes[n]["mech"]] + rng.normal(scale=0.25, size=2)
        for n in g.nodes()
    }
    u = g.to_undirected()
    k = 1.1 / np.sqrt(u.number_of_nodes())
    pos = nx.spring_layout(u, pos=initial, k=k, iterations=60, seed=7)

    # --- classify edges -------------------------------------------------------
    intra, inter_by_src = [], {m: [] for m in MECH_ORDER}
    for s, t in g.edges():
        ms = g.nodes[s]["mech"]
        mt = g.nodes[t]["mech"]
        if ms not in MECH_ORDER or mt not in MECH_ORDER:
            continue
        (intra if ms == mt else inter_by_src.setdefault(ms, [])).append((s, t))

    # --- node sizing by in-degree (received internal citations) ---------------
    in_deg = dict(g.in_degree())
    size_arr = {n: 6 + 2.4 * np.sqrt(in_deg.get(n, 0) + 1) for n in g.nodes()}

    # --- draw -----------------------------------------------------------------
    fig = plt.figure(figsize=(14, 12), dpi=160, facecolor="white")
    ax = fig.add_axes([0.02, 0.04, 0.78, 0.92])
    ax.set_facecolor("#f7f8fb")
    ax.set_axis_off()

    # intra edges first, very light
    nx.draw_networkx_edges(
        g, pos, edgelist=intra, ax=ax,
        edge_color="#c8cdd6", width=0.12, alpha=0.10, arrows=False,
    )
    # inter edges coloured by source mechanism
    for m, elist in inter_by_src.items():
        if not elist:
            continue
        nx.draw_networkx_edges(
            g, pos, edgelist=elist, ax=ax,
            edge_color=[MECH_COLORS[m]] * len(elist),
            width=0.22, alpha=0.22, arrows=False,
        )
    # nodes per mechanism so the legend is clean
    for m in MECH_ORDER:
        nodes = [n for n in g.nodes() if g.nodes[n]["mech"] == m]
        if not nodes:
            continue
        nx.draw_networkx_nodes(
            g, pos, nodelist=nodes, ax=ax,
            node_size=[size_arr[n] for n in nodes],
            node_color=[MECH_COLORS[m]],
            linewidths=0.15, edgecolors="#0b1220", alpha=0.92,
            label=MECH_SHORT.get(m, m),
        )

    # legend
    handles = [plt.Line2D([0], [0], marker="o", linestyle="",
                          markerfacecolor=MECH_COLORS[m], markeredgecolor="#0b1220",
                          markersize=8, label=MECH_SHORT.get(m, m))
               for m in MECH_ORDER]
    ax.legend(handles=handles, loc="center left", bbox_to_anchor=(1.00, 0.5),
              frameon=False, fontsize=10, title="Mechanism",
              title_fontsize=11)

    ax.set_title(
        f"Internal citation network coloured by mechanism "
        f"(papers with total degree ≥ {MIN_DEG})\n"
        f"nodes = {g.number_of_nodes():,} papers  •  "
        f"edges = {g.number_of_edges():,} internal citations  •  "
        f"group-seeded spring layout;  intra-mechanism edges light grey, "
        f"cross-mechanism edges coloured by citing mechanism",
        fontsize=12,
    )

    out = OUT_DIR / "fig4_citation_by_mechanism.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


if __name__ == "__main__":
    main()
