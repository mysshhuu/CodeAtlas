from dataclasses import dataclass, field


@dataclass
class CodeNode:
    name: str
    node_type: str
    file_path: str
    start_line: int
    end_line: int


@dataclass
class CodeEdge:
    source: str
    target: str
    relationship: str


@dataclass
class CodeGraph:
    nodes: list[CodeNode] = field(default_factory=list)
    edges: list[CodeEdge] = field(default_factory=list)

    def add_node(self, node: CodeNode):
        self.nodes.append(node)

    def add_edge(self, edge: CodeEdge):
        self.edges.append(edge)


def create_graph() -> CodeGraph:
    """
    Create an empty CodeAtlas code graph.
    """
    return CodeGraph()


def add_parser_results(
    graph: CodeGraph,
    parsed_items: list[dict],
    file_path: str,
):
    """
    Add functions extracted by the parser
    to the CodeAtlas graph.
    """

    for item in parsed_items:
        graph.add_node(
            CodeNode(
                name=item["name"],
                node_type=item["type"],
                file_path=file_path,
                start_line=item["start_line"],
                end_line=item["end_line"],
            )
        )


def add_parser_calls(
    graph: CodeGraph,
    calls: list[dict],
):
    """
    Add function-call relationships to the graph.

    Each call is expected to contain:
        source
        target
        relationship
    """

    for call in calls:

        source = call.get("source")
        target = call.get("target")

        if not source or not target:
            continue

        graph.add_edge(
            CodeEdge(
                source=source,
                target=target,
                relationship=call.get(
                    "relationship",
                    "calls",
                ),
            )
        )