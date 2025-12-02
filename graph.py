import networkx as nx
import matplotlib.pyplot as plt

nodes = {
    0: {"name": "University", "type": "university"},
    1: {"name": "Beb El 7ouma", "type": "restaurant"},
    2: {"name": "Awled Afef", "type": "restaurant"},
    3: {"name": "Mlewi Djo", "type": "restaurant"},
    4: {"name": "Chappati Aissam", "type": "restaurant"},
    5: {"name": "And Amel", "type": "restaurant"},
    6: {"name": "Restaurant El Kbir", "type": "restaurant"},
    7: {"name": "Restaurant El Meken", "type": "restaurant"},
    8: {"name": "TBS Dining Hall", "type": "restaurant"},
}

edges = [
    (0, 1, 400),
    (0, 2, 80),
    (0, 3, 300),
    (0, 4, 60),
    (0, 5, 75),
    (0, 6, 310),
    (0, 7, 110),
    (0, 8, 220),
]

G = nx.Graph()
for node_id, data in nodes.items():
    G.add_node(node_id, label=data["name"], type=data["type"])

for frm, to, dist in edges:
    G.add_edge(frm, to, weight=dist)


pos = nx.spring_layout(G, seed=42)  
node_colors = ["lightblue" if data["type"]=="university" else "lightgreen" for data in nodes.values()]
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1000)
nx.draw_networkx_edges(G, pos)
labels = {n: data["name"] for n, data in nodes.items()}
nx.draw_networkx_labels(G, pos, labels, font_size=10)

edge_labels = {(frm, to): f"{dist}m" for frm, to, dist in edges}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

plt.title("University-Star Network")
plt.axis("off")
plt.show()
