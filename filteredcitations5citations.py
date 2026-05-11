import networkx as nx
import matplotlib.pyplot as plt

# load the citation graph
G = nx.read_edgelist("/Users/ericzhang/Desktop/Python_Projects/citation_graph.edgelist", create_using=nx.DiGraph())

# filter nodes with at least 5 citations
citation_threshold = 3
filtered_nodes = [n for n in G.nodes if G.in_degree(n) >= citation_threshold]

# get the subgraph of only these cited-enough nodes
H = G.subgraph(filtered_nodes).copy()

# compute in-degrees again for color mapping
in_degrees = dict(H.in_degree())
max_in = max(in_degrees.values()) if in_degrees else 1
node_colors = [in_degrees[n] / max_in for n in H.nodes]

# draw
plt.figure(figsize=(10, 10))
pos = nx.spring_layout(H, seed=42)
nx.draw(
    H,
    pos,
    node_color=node_colors,
    cmap=plt.cm.viridis_r,
    with_labels=False,
    node_size=50,
    edge_color='gray',
    arrows=True
)
plt.title("Citation Graph: Nodes with ≥5 Citations (Darker = More Cited)")
plt.show()
