# step6_build_graph.py

import pandas as pd
import networkx as nx

# === FILES ===
PAPER_CSV = "superconduct_top10percent.csv"
EDGES_CSV = "citation_edges_outgoing.csv"
OUTPUT_GEXF = "citation_graph.gexf"

# === opinion node paper IDs (from step 5) ===
OPINION_NODE_IDS = {
    "pub.1060839416",  # Hubbard/Mott
    "pub.1018103421",  # electron-phonon coupling
    "pub.1045115933",  # topological superconductors
    "pub.1011817307",  # quantum critical point
    "pub.1085993311",  # charge density wave
    "pub.1026064321",  # spin fluctuations
    "pub.1101336540",  # unconventional superconductivity
}

# === load data ===
print("loading papers...")
df_papers = pd.read_csv(PAPER_CSV)
df_papers["id"] = df_papers["id"].astype(str)

print("loading edges...")
df_edges = pd.read_csv(EDGES_CSV)
df_edges["source"] = df_edges["source"].astype(str)
df_edges["target"] = df_edges["target"].astype(str)

# === create graph ===
print("building graph...")
G = nx.DiGraph()

# add nodes
for _, row in df_papers.iterrows():
    pid = row["id"]
    G.add_node(pid, 
               title=row.get("title", ""),
               year=int(row.get("year", 0)),
               times_cited=int(row.get("times_cited", 0)),
               is_opinion_node=pid in OPINION_NODE_IDS)

# add edges (only if both ends are in the graph)
for _, row in df_edges.iterrows():
    src, tgt = row["source"], row["target"]
    if src in G and tgt in G:
        G.add_edge(src, tgt)

# === save graph ===
nx.write_gexf(G, OUTPUT_GEXF)
print(f"done. graph saved to: {OUTPUT_GEXF}")
print(f"nodes: {G.number_of_nodes()}, edges: {G.number_of_edges()}")
