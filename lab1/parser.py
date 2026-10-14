from errors import ParseError
from lexer import Lexer


EPSILON = "ε"


class Node:
    def __init__(self, label, children=None):
        self.label = label
        self.children = list(children) if children else []

    def __repr__(self):
        return f"Node({self.label!r}, {self.children!r})"

    def __eq__(self, other):
        return (
            isinstance(other, Node)
            and self.label == other.label
            and self.children == other.children
        )


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current = lexer.getNextToken()

    def error(self, message):
        raise ParseError(message, self.current.pos, self.lexer.text)

    def match(self, expected_value):
        if self.current.value == expected_value:
            token = self.current
            self.current = self.lexer.getNextToken()
            return token
        self.error(f"Ожидалось: '{expected_value}'")

    def match_type(self, expected_type):
        if self.current.type == expected_type:
            token = self.current
            self.current = self.lexer.getNextToken()
            return token
        self.error(f"Ожидалось: {expected_type}")

    def parseS(self):
        return Node("S", [self.parseE()])

    def parseE(self):
        return Node("E", [self.parseT(), self.parseEPrime()])

    def parseEPrime(self):
        if self.current.value in ("+", "-"):
            operator = Node(self.current.value)
            self.current = self.lexer.getNextToken()
            return Node("E'", [operator, self.parseT(), self.parseEPrime()])
        return Node("E'", [Node(EPSILON)])

    def parseT(self):
        return Node("T", [self.parseF(), self.parseTPrime()])

    def parseTPrime(self):
        if self.current.value in ("*", "/"):
            operator = Node(self.current.value)
            self.current = self.lexer.getNextToken()
            return Node("T'", [operator, self.parseF(), self.parseTPrime()])
        return Node("T'", [Node(EPSILON)])

    def parseF(self):
        if self.current.value == "(":
            self.match("(")
            inner = self.parseS()
            self.match(")")
            return Node("F", [Node("("), inner, Node(")")])
        if self.current.type in ("NUMBER", "ID"):
            token = self.current
            self.match_type(token.type)
            return Node("F", [Node(f"{token.type.lower()}:{token.value}")])
        self.error("Ожидалось: number, id или '('")

    def parse(self):
        tree = self.parseS()
        if self.current.type != "EOF":
            self.error("Ожидалось: конец выражения")
        return tree


def parse(text):
    return Parser(Lexer(text)).parse()


def format_tree(node):
    lines = [node.label]
    _format_children(node, "", lines)
    return "\n".join(lines)


def _format_children(node, prefix, lines):
    last_index = len(node.children) - 1
    for index, child in enumerate(node.children):
        is_last = index == last_index
        branch = "└── " if is_last else "├── "
        lines.append(prefix + branch + child.label)
        next_prefix = prefix + ("    " if is_last else "│   ")
        _format_children(child, next_prefix, lines)
