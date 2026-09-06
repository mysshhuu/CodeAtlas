import ast


# ============================================================
# PARSE PYTHON CODE
# ============================================================

def parse_python_code(source_code: str):
    """
    Parse Python source code using Python's built-in AST parser.
    """

    return ast.parse(
        source_code
    )


# ============================================================
# EXTRACT FUNCTIONS AND CLASSES
# ============================================================

def extract_functions(
    source_code: str,
):
    """
    Extract functions and classes from Python source code.

    Each result contains:

    - type
    - name
    - start_line
    - end_line
    """

    tree = parse_python_code(
        source_code
    )

    results = []

    for node in ast.walk(tree):

        # ----------------------------------------------------
        # NORMAL FUNCTION
        # ----------------------------------------------------

        if isinstance(
            node,
            ast.FunctionDef,
        ):

            results.append(
                {
                    "type": "function",
                    "name": node.name,
                    "start_line": node.lineno,
                    "end_line": (
                        getattr(
                            node,
                            "end_lineno",
                            node.lineno,
                        )
                    ),
                }
            )

        # ----------------------------------------------------
        # ASYNC FUNCTION
        # ----------------------------------------------------

        elif isinstance(
            node,
            ast.AsyncFunctionDef,
        ):

            results.append(
                {
                    "type": "function",
                    "name": node.name,
                    "start_line": node.lineno,
                    "end_line": (
                        getattr(
                            node,
                            "end_lineno",
                            node.lineno,
                        )
                    ),
                }
            )

        # ----------------------------------------------------
        # CLASS
        # ----------------------------------------------------

        elif isinstance(
            node,
            ast.ClassDef,
        ):

            results.append(
                {
                    "type": "class",
                    "name": node.name,
                    "start_line": node.lineno,
                    "end_line": (
                        getattr(
                            node,
                            "end_lineno",
                            node.lineno,
                        )
                    ),
                }
            )

    return results


# ============================================================
# GET CALL TARGET NAME
# ============================================================

def get_call_name(
    node,
) -> str:
    """
    Convert an AST call target into a readable name.

    Examples:

        print()
            -> print

        db.insert()
            -> db.insert

        super().method()
            -> super().method

        foo.bar.baz()
            -> foo.bar.baz
    """

    # --------------------------------------------------------
    # Simple name
    # --------------------------------------------------------

    if isinstance(
        node,
        ast.Name,
    ):

        return node.id

    # --------------------------------------------------------
    # Attribute access
    # --------------------------------------------------------

    if isinstance(
        node,
        ast.Attribute,
    ):

        parent = get_call_name(
            node.value
        )

        if parent:
            return (
                f"{parent}.{node.attr}"
            )

        return node.attr

    # --------------------------------------------------------
    # super()
    # --------------------------------------------------------

    if isinstance(
        node,
        ast.Call,
    ):

        if isinstance(
            node.func,
            ast.Name,
        ):

            return node.func.id

        return get_call_name(
            node.func
        )

    return ""


# ============================================================
# EXTRACT FUNCTION CALLS
# ============================================================

def extract_calls(
    source_code: str,
):
    """
    Extract function calls from Python source code.

    Each call contains:

    - source
    - target
    - relationship
    - start_line
    - end_line
    """

    tree = parse_python_code(
        source_code
    )

    calls = []

    # --------------------------------------------------------
    # Walk functions separately.
    #
    # This gives every call its containing function.
    # --------------------------------------------------------

    def process_function(
        function_node,
        function_name,
    ):

        for node in ast.walk(
            function_node
        ):

            # Don't accidentally treat a nested function's
            # calls as belonging to the outer function.
            if (
                node is not function_node
                and isinstance(
                    node,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef,
                    ),
                )
            ):
                continue

            if isinstance(
                node,
                ast.Call,
            ):

                target = get_call_name(
                    node.func
                )

                if not target:
                    continue

                calls.append(
                    {
                        "source": function_name,
                        "target": target,
                        "relationship": "calls",
                        "start_line": node.lineno,
                        "end_line": (
                            getattr(
                                node,
                                "end_lineno",
                                node.lineno,
                            )
                        ),
                    }
                )

    # --------------------------------------------------------
    # Find every function in the file
    # --------------------------------------------------------

    for node in ast.walk(tree):

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):

            process_function(
                node,
                node.name,
            )

    return calls