from app.analysis.parser import extract_functions


code = """
def create_user(name):
    return db.insert(name)


def delete_user(user_id):
    return db.delete(user_id)
"""


functions = extract_functions(code)


print()
print("=" * 60)
print("CODEATLAS TREE-SITTER TEST")
print("=" * 60)

for function in functions:

    print()
    print(f"Type: {function['type']}")
    print(f"Name: {function['name']}")
    print(
        f"Lines: "
        f"{function['start_line']}"
        f"-"
        f"{function['end_line']}"
    )

print()
print("=" * 60)