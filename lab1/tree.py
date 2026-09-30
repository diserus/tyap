class Node:
    __slots__ = ("label", "children")

    def __init__(self, label, children=None):
        self.label = label
        self.children = children or []

    def add(self, child):
        self.children.append(child)
        return child

    def __repr__(self):
        return f"Node({self.label!r}, {self.children!r})"


def terminal_node(token):
    if token.type == "NUMBER":
        return Node(f"number: {token.value}")
    if token.type == "ID":
        return Node(f"id: {token.value}")
    if token.type == "EOF":
        return Node("EOF")
    return Node(f"'{token.value}'")


def render_tree(node):
    lines = []

    def walk(n, prefix, is_last, is_root):
        if is_root:
            lines.append(n.label)
            child_prefix = prefix
        else:
            lines.append(prefix + ("└── " if is_last else "├── ") + n.label)
            child_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(n.children):
            walk(child, child_prefix, i == len(n.children) - 1, False)

    walk(node, "", True, True)
    return "\n".join(lines)
