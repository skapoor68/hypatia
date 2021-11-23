import networkx as nx

G = nx.Graph()

for i in range(10):
    G.add_node(i)

print(list(G.nodes))
for i in range(20):
    G.add_node(i)

print(list(G.nodes))

# G.add_edge("a", "b", weight=0.6)
# G.add_edge("a", "c", weight=0.2)
# G.add_edge("c", "d", weight=0.1)
# G.add_edge("c", "e", weight=0.7)
# G.add_edge("c", "f", weight=0.9)
# G.add_edge("a", "d", weight=0.3)

# path=dict(nx.all_pairs_shortest_path(G))
# print(path)
# print(nx.is_weighted(G))

# a = None
# print(nx.classes.function.path_weight(G, a, "weight"))

# print(path[0][0])
# pdict = {p[0]:p[1] for p in path}

# print(pdict)