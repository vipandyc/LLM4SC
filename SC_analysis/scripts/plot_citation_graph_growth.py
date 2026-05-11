#!/usr/bin/env python3
"""Create a year-by-year citation-network growth animation (GIF)."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot internal citation graph growth as a GIF.")
    parser.add_argument(
        "--edges-path",
        default="superconductivity/citation_edges_internal.csv",
        help="Path to internal citation edges CSV.",
    )
    parser.add_argument(
        "--growth-path",
        default="superconductivity/citation_growth_over_time.csv",
        help="Path to cumulative citation-over-time CSV.",
    )
    parser.add_argument(
        "--metadata-path",
        default="data/SC_related_cites_010_GPT_processed.csv",
        help="Path to metadata CSV with id/year.",
    )
    parser.add_argument(
        "--frames-dir",
        default="SC_analysis/citation_graph_frames",
        help="Directory to store frame PNGs.",
    )
    parser.add_argument(
        "--output-gif",
        default="SC_analysis/citation_graph_growth.gif",
        help="Output GIF path.",
    )
    parser.add_argument("--year-start", type=int, default=None, help="First year in animation.")
    parser.add_argument("--year-end", type=int, default=None, help="Last year in animation.")
    parser.add_argument("--year-step", type=int, default=1, help="Step size in years (default: 1).")
    parser.add_argument("--fps", type=int, default=4, help="GIF frames per second.")
    parser.add_argument("--fig-width", type=float, default=12.0, help="Figure width in inches.")
    parser.add_argument("--fig-height", type=float, default=10.0, help="Figure height in inches.")
    parser.add_argument("--dpi", type=int, default=150, help="PNG DPI.")
    parser.add_argument(
        "--layout-iterations",
        type=int,
        default=60,
        help="Spring-layout iterations (higher is slower, default: 60).",
    )
    parser.add_argument("--layout-seed", type=int, default=42, help="Layout random seed.")
    parser.add_argument(
        "--layout-k",
        type=float,
        default=None,
        help="Spring-layout k value; default auto-scales with node count.",
    )
    return parser.parse_args()


def build_growth_lookup(growth_df: pd.DataFrame) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    lookup: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for pid, chunk in growth_df.groupby("id", sort=False):
        chunk_sorted = chunk.sort_values("year")
        years = chunk_sorted["year"].to_numpy(dtype=np.int32)
        counts = chunk_sorted["cumulative_citations"].to_numpy(dtype=np.int32)
        lookup[str(pid)] = (years, counts)
    return lookup


def citation_at_year(lookup: dict[str, tuple[np.ndarray, np.ndarray]], pid: str, year: int) -> int:
    pair = lookup.get(pid)
    if pair is None:
        return 0
    years, counts = pair
    idx = np.searchsorted(years, year, side="right") - 1
    if idx < 0:
        return 0
    return int(counts[idx])


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]

    edges_path = repo_root / args.edges_path
    growth_path = repo_root / args.growth_path
    metadata_path = repo_root / args.metadata_path
    frames_dir = repo_root / args.frames_dir
    output_gif = repo_root / args.output_gif

    frames_dir.mkdir(parents=True, exist_ok=True)
    output_gif.parent.mkdir(parents=True, exist_ok=True)

    edges_df = pd.read_csv(edges_path, usecols=["source", "target"]).dropna()
    edges_df["source"] = edges_df["source"].astype(str)
    edges_df["target"] = edges_df["target"].astype(str)

    meta = pd.read_csv(metadata_path, usecols=["id", "year"]).dropna(subset=["id"])
    id2year = {
        str(pid): int(year)
        for pid, year in meta[["id", "year"]].itertuples(index=False, name=None)
        if not pd.isna(year)
    }

    growth_df = pd.read_csv(growth_path, usecols=["id", "year", "cumulative_citations"]).dropna()
    growth_df["id"] = growth_df["id"].astype(str)
    growth_df["year"] = growth_df["year"].astype(int)
    growth_df["cumulative_citations"] = growth_df["cumulative_citations"].astype(int)
    growth_lookup = build_growth_lookup(growth_df)

    sources = edges_df["source"].tolist()
    targets = edges_df["target"].tolist()
    edge_list = list(zip(sources, targets))

    node_set = set(sources) | set(targets)
    node_list = sorted(node_set)
    node_year = {n: id2year.get(n) for n in node_list}

    known_years = [y for y in node_year.values() if y is not None]
    if not known_years:
        raise ValueError("No publication years available for citation-graph nodes.")

    min_pub_year = min(known_years)
    max_pub_year = max(known_years)
    max_growth_year = int(growth_df["year"].max()) if not growth_df.empty else max_pub_year

    year_start = args.year_start if args.year_start is not None else min_pub_year
    year_end = args.year_end if args.year_end is not None else max(max_pub_year, max_growth_year)
    years = list(range(year_start, year_end + 1, max(1, args.year_step)))

    # Build graph and stable layout once.
    g = nx.DiGraph()
    g.add_nodes_from(node_list)
    g.add_edges_from(edge_list)
    layout_k = args.layout_k if args.layout_k is not None else (2.2 / np.sqrt(max(1, len(node_list))))
    pos = nx.spring_layout(
        g.to_undirected(),
        seed=args.layout_seed,
        iterations=args.layout_iterations,
        k=layout_k,
    )

    # Final max for shared color normalization.
    final_cites_max = 0
    for pid in node_list:
        c = citation_at_year(growth_lookup, pid, year_end)
        if c > final_cites_max:
            final_cites_max = c
    final_cites_max = max(1, final_cites_max)
    norm = mcolors.Normalize(vmin=0, vmax=final_cites_max)
    cmap = plt.get_cmap("coolwarm")

    # Missing publication years: show from first frame.
    default_year = year_start
    src_years = np.array([node_year.get(s, default_year) or default_year for s in sources], dtype=np.int32)
    tgt_years = np.array([node_year.get(t, default_year) or default_year for t in targets], dtype=np.int32)
    x_vals = np.array([pos[n][0] for n in node_list], dtype=float)
    y_vals = np.array([pos[n][1] for n in node_list], dtype=float)
    x_pad = max(0.05, 0.05 * (x_vals.max() - x_vals.min()))
    y_pad = max(0.05, 0.05 * (y_vals.max() - y_vals.min()))
    xlim = (x_vals.min() - x_pad, x_vals.max() + x_pad)
    ylim = (y_vals.min() - y_pad, y_vals.max() + y_pad)

    frame_paths: list[Path] = []

    for y in years:
        active_nodes = [n for n in node_list if (node_year.get(n) or default_year) <= y]

        active_edge_mask = (src_years <= y) & (tgt_years <= y)
        active_edges = [edge_list[i] for i, ok in enumerate(active_edge_mask) if ok]
        new_edge_mask = active_edge_mask & (src_years == y)
        new_edges = [edge_list[i] for i, ok in enumerate(new_edge_mask) if ok]

        node_cites = np.array([citation_at_year(growth_lookup, n, y) for n in active_nodes], dtype=np.int32)
        node_colors = node_cites
        node_sizes = 9 + 1.7 * np.sqrt(node_cites + 1)

        fig = plt.figure(figsize=(args.fig_width, args.fig_height), dpi=args.dpi, facecolor="white")
        ax = fig.add_axes([0.04, 0.06, 0.82, 0.88])
        cax = fig.add_axes([0.88, 0.18, 0.025, 0.64])
        ax.set_facecolor("#f8fafc")
        ax.set_axis_off()
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.set_title(
            "Internal Citation Graph Growth\n"
            f"Year: {y} | Nodes: {len(active_nodes):,} | Edges: {len(active_edges):,}",
            fontsize=13,
        )

        # DiGraph semantics are source -> target (source cites target).
        nx.draw_networkx_edges(
            g,
            pos,
            edgelist=active_edges,
            ax=ax,
            edge_color="#64748b",
            width=0.32,
            alpha=0.22,
            arrows=False,
        )
        nx.draw_networkx_edges(
            g,
            pos,
            edgelist=new_edges,
            ax=ax,
            edge_color="#0f172a",
            width=0.6,
            alpha=0.38,
            arrows=False,
        )
        nx.draw_networkx_nodes(
            g,
            pos,
            nodelist=active_nodes,
            ax=ax,
            node_size=node_sizes,
            node_color=node_colors,
            cmap=cmap,
            vmin=0,
            vmax=final_cites_max,
            linewidths=0.12,
            edgecolors="#0b1220",
            alpha=0.92,
        )

        sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
        sm.set_array([])
        cbar = fig.colorbar(sm, cax=cax)
        cbar.set_label("Cumulative received internal citations", fontsize=9)

        ax.text(
            0.01,
            0.01,
            "Edge direction in data: source -> target (A cites B)",
            transform=ax.transAxes,
            fontsize=8,
            color="#1f2937",
            ha="left",
            va="bottom",
        )

        frame_path = frames_dir / f"citation_graph_{y}.png"
        fig.savefig(frame_path)
        plt.close(fig)
        frame_paths.append(frame_path)
        print(f"Saved frame: {frame_path}")

    if not frame_paths:
        raise ValueError("No frames were created.")

    images = [Image.open(p) for p in frame_paths]
    duration_ms = int(1000 / max(1, args.fps))
    images[0].save(
        output_gif,
        save_all=True,
        append_images=images[1:],
        duration=duration_ms,
        loop=0,
        optimize=False,
    )
    for img in images:
        img.close()

    print(f"Wrote GIF: {output_gif}")
    print(f"Total frames: {len(frame_paths)}")
    print(f"Year range: {years[0]} -> {years[-1]} (step={args.year_step})")


if __name__ == "__main__":
    main()
