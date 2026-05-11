import matplotlib.pyplot as plt
import networkx as nx

# load the full graph
G = nx.read_gexf("superconduct_opinion_graph.gexf")

# find opinion nodes
opinion_nodes = [n for n, d in G.nodes(data=True) if d.get("is_opinion_node") == True]

# collect opinion nodes and their 1-hop neighbors (capped at 100 each)
sub_nodes = set(opinion_nodes)
for node in opinion_nodes:
    neighbors = list(G.successors(node)) + list(G.predecessors(node))
    sub_nodes.update(neighbors[:100])  # limit to 100 neighbors per node

# build subgraph
H = G.subgraph(sub_nodes).copy()

# color opinion nodes red, others gray
colors = ['red' if H.nodes[n].get("is_opinion_node") else 'gray' for n in H.nodes()]

# draw
plt.figure(figsize=(12, 12))
pos = nx.spring_layout(H, k=0.2, iterations=50)
nx.draw(H, pos, node_size=25, node_color=colors, edge_color="lightgray", with_labels=False)
plt.title("Trimmed Citation Subgraph (Opinion Nodes + 1-hop Neighbors)")
plt.axis("off")
plt.tight_layout()
plt.show()
