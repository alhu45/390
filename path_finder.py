import pandas as pd
import math
import heapq
import networkx as nx
import matplotlib.pyplot as plt
from PIL import Image

# Load the data
df = pd.read_csv("intersections.txt", sep='\t')

# Create a graph
G = nx.Graph()
for _, row in df.iterrows():
    node_name = f"{row['Horizontal']} & {row['Vertical']}"
    G.add_node(node_name, pos=(row['X'], row['Y']))

# Add horizontal edges
for _, group in df.groupby("Horizontal"):
    group = group.sort_values("X")
    for i in range(len(group) - 1):
        n1 = f"{group.iloc[i]['Horizontal']} & {group.iloc[i]['Vertical']}"
        n2 = f"{group.iloc[i + 1]['Horizontal']} & {group.iloc[i + 1]['Vertical']}"
        dist = math.dist((group.iloc[i]['X'], group.iloc[i]['Y']),
                         (group.iloc[i + 1]['X'], group.iloc[i + 1]['Y']))
        G.add_edge(n1, n2, weight=dist)

# Add vertical edges
for _, group in df.groupby("Vertical"):
    group = group.sort_values("Y")
    for i in range(len(group) - 1):
        n1 = f"{group.iloc[i]['Horizontal']} & {group.iloc[i]['Vertical']}"
        n2 = f"{group.iloc[i + 1]['Horizontal']} & {group.iloc[i + 1]['Vertical']}"
        dist = math.dist((group.iloc[i]['X'], group.iloc[i]['Y']),
                         (group.iloc[i + 1]['X'], group.iloc[i + 1]['Y']))
        G.add_edge(n1, n2, weight=dist)

# The Circle Edges 
circle_nodes = df[df["Horizontal"] == "The Circle"].copy()
circle_names = [f"{row['Horizontal']} & {row['Vertical']}" for _, row in circle_nodes.iterrows()]
center_x = circle_nodes["X"].mean()
center_y = circle_nodes["Y"].mean()

# Sort by angle around the center
circle_nodes["angle"] = circle_nodes.apply(lambda row: math.atan2(row["Y"] - center_y, row["X"] - center_x), axis=1)
circle_nodes = circle_nodes.sort_values("angle")
circle_names = [f"{row['Horizontal']} & {row['Vertical']}" for _, row in circle_nodes.iterrows()]

for i in range(len(circle_names)):
    n1 = circle_names[i]
    n2 = circle_names[(i + 1) % len(circle_names)]
    p1 = G.nodes[n1]["pos"]
    p2 = G.nodes[n2]["pos"]
    dist = math.dist(p1, p2)
    G.add_edge(n1, n2, weight=dist)

proximity_threshold = 60  
all_nodes = list(G.nodes(data=True))
for i in range(len(all_nodes)):
    for j in range(i + 1, len(all_nodes)):
        node1, data1 = all_nodes[i]
        node2, data2 = all_nodes[j]
        pos1 = data1["pos"]
        pos2 = data2["pos"]
        dist = math.dist(pos1, pos2)

        # Parse street names
        h1, v1 = node1.split(" & ")
        h2, v2 = node2.split(" & ")

        # Only connect if they don’t already share a common street
        if dist < proximity_threshold and not G.has_edge(node1, node2):
            if h1 != h2 and v1 != v2:
                G.add_edge(node1, node2, weight=dist)

# Manually adding edges
node_a = "Pondside Ave. & Quack St."
node_b = "Breadcrumb Ave. & Waddle Way"
pos_a = G.nodes[node_a]["pos"]
pos_b = G.nodes[node_b]["pos"]
dist = math.dist(pos_a, pos_b)
G.add_edge(node_a, node_b, weight=dist)

node_c = "Migration Ave. & Quack St."
node_d = "Aquatic Ave. & Waddle Way"
pos_c = G.nodes[node_c]["pos"]
pos_d = G.nodes[node_d]["pos"]
dist = math.dist(pos_c, pos_d)
G.add_edge(node_c, node_d, weight=dist)

node_e = "Migration Ave. & Mallard St."
node_f = "Aquatic Ave. & Beak St."
pos_e = G.nodes[node_e]["pos"]
pos_f = G.nodes[node_f]["pos"]
dist = math.dist(pos_e, pos_f)
G.add_edge(node_e, node_f, weight=dist)

node_g = "Breadcrumb Ave. & The Circle"
node_h = "The Circle & Waterfoul Way"
pos_g = G.nodes[node_g]["pos"]
pos_h = G.nodes[node_h]["pos"]
dist = math.dist(pos_g, pos_h)
G.add_edge(node_g, node_h, weight=dist)

# Nearest node by coordinates
def nearest_node(x, y):
    min_dist = float('inf')
    nearest = None
    for _, row in df.iterrows():
        dist = math.dist((x, y), (row['X'], row['Y']))
        if dist < min_dist:
            min_dist = dist
            nearest = f"{row['Horizontal']} & {row['Vertical']}"
    return nearest

# Dijkstra's algorithm
def dijkstra(graph, start, end):
    queue = [(0, start)]
    distances = {node: float('inf') for node in graph.nodes}
    distances[start] = 0
    previous = {node: None for node in graph.nodes}

    while queue:
        current_dist, current_node = heapq.heappop(queue)
        if current_node == end:
            break
        for neighbor in graph.neighbors(current_node):
            weight = graph[current_node][neighbor]['weight']
            distance = current_dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))

    path = []
    while end:
        path.insert(0, end)
        end = previous[end]
    return path, distances[path[-1]]

# INPUT COORDINATES (Hard Coded)
start_coords = (300, 130)
end_coords = (450, 470)

start_node = nearest_node(*start_coords)
end_node = nearest_node(*end_coords)

# Run Dijkstra
path, total_distance = dijkstra(G, start_node, end_node)

# Print path info
print(f"\n Closest start node: {start_node}")
print(f"Closest end node: {end_node}")
print(f"Direction of Shortest Path ({round(total_distance, 2)} units):")
for i, node in enumerate(path):
    print(f"{i+1}. {node}")

# Map Drawing
pos = nx.get_node_attributes(G, 'pos')
fig, ax = plt.subplots(figsize=(12, 8))

# Optional background image
# try:
#     img = Image.open("map")
#     ax.imshow(img, extent=[0, 640, 0, 480])
# except:
#     pass  

# Draw all nodes and edges
nx.draw_networkx_nodes(G, pos, ax=ax, node_size=50, node_color='lightgray')
nx.draw_networkx_edges(G, pos, ax=ax, width=0.5, edge_color='gray')

# Add labels to nodes
nx.draw_networkx_labels(G, pos, ax=ax, font_size=6)

# Draw path
path_edges = list(zip(path, path[1:]))
nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=path, node_size=70, node_color='orange')
nx.draw_networkx_edges(G, pos, ax=ax, edgelist=path_edges, width=2.5, edge_color='red')

plt.title("Shortest Path on Duckville Map", fontsize=14)
plt.axis("off")
plt.tight_layout()
plt.show()

