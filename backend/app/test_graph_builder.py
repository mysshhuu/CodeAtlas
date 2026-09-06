from app.analysis.graph_builder import build_repository_graph


print("=" * 60)
print("CODEATLAS REPOSITORY GRAPH TEST")
print("=" * 60)

repository_path = "data/repos/fastapi/fastapi"

print()
print("Building graph...")
print()

graph = build_repository_graph(repository_path)

print()
print("=" * 60)
print("GRAPH RESULTS")
print("=" * 60)

print()
print("TOTAL NODES:", len(graph.nodes))
print("TOTAL EDGES:", len(graph.edges))

print()
print("SAMPLE NODES:")

for node in graph.nodes[:10]:
    print(
        f"{node.node_type}: "
        f"{node.name} "
        f"({node.file_path}:{node.start_line}-{node.end_line})"
    )

print()
print("SAMPLE EDGES:")

for edge in graph.edges[:10]:
    print(
        f"{edge.source} "
        f"--{edge.relationship}--> "
        f"{edge.target}"
    )

print()
print("=" * 60)
print("GRAPH BUILDER TEST PASSED")
print("=" * 60)