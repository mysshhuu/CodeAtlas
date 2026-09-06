from app.analysis.parser import extract_functions, extract_calls

from app.analysis.graph import (
    create_graph,
    add_parser_results,
    add_parser_calls,
)


# Small example codebase
source_code = """
def get_data():
    return "data"


def process_data():
    data = get_data()
    return data
"""


file_path = "example.py"


# Extract functions
parsed_items = extract_functions(
    source_code
)


# Extract function calls
calls = extract_calls(
    source_code
)


# Create graph
graph = create_graph()


# Add function nodes
add_parser_results(
    graph,
    parsed_items,
    file_path,
)


# Add function relationships
add_parser_calls(
    graph,
    calls,
)


print("=" * 60)
print("CODEATLAS GRAPH TEST")
print("=" * 60)


print("\nNODES")
print("-" * 60)

for node in graph.nodes:
    print(
        f"{node.node_type}: "
        f"{node.name} "
        f"({node.file_path}:"
        f"{node.start_line}-"
        f"{node.end_line})"
    )


print("\nEDGES")
print("-" * 60)

for edge in graph.edges:
    print(
        f"{edge.source} "
        f"--[{edge.relationship}]--> "
        f"{edge.target}"
    )


print("\nTOTAL NODES:", len(graph.nodes))
print("TOTAL EDGES:", len(graph.edges))


print("=" * 60)
print("GRAPH TEST PASSED")
print("=" * 60)