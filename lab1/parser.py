from errors import ParseError
from lexer import Lexer
from tree import Node, terminal_node


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current = lexer.getNextToken()

    def error(self, message):
        raise ParseError(message, self.current.pos, self.lexer.text)

    def match(self, expected_value):
        if self.current.value == expected_value:
            node = Node(f"'{expected_value}'")
            self.current = self.lexer.getNextToken()
            return node
        self.error(f"Ожидалось: '{expected_value}'")

    def match_type(self, expected_type):
        if self.current.type == expected_type:
            node = terminal_node(self.current)
            self.current = self.lexer.getNextToken()
            return node
        self.error(f"Ожидалось: {expected_type}")

    def parseS(self):
        node = Node("S")
        node.add(self.parseE())
        return node

    def parseE(self):
        node = Node("E")
        node.add(self.parseT())
        node.add(self.parseEPrime())
        return node

    def parseEPrime(self):
        node = Node("E'")
        if self.current.value in ("+", "-"):
            op = self.current
            self.current = self.lexer.getNextToken()
            node.add(terminal_node(op))
            node.add(self.parseT())
            node.add(self.parseEPrime())
        else:
            node.add(Node("ε"))
        return node

    def parseT(self):
        node = Node("T")
        node.add(self.parseF())
        node.add(self.parseTPrime())
        return node

    def parseTPrime(self):
        node = Node("T'")
        if self.current.value in ("*", "/"):
            op = self.current
            self.current = self.lexer.getNextToken()
            node.add(terminal_node(op))
            node.add(self.parseF())
            node.add(self.parseTPrime())
        else:
            node.add(Node("ε"))
        return node

    def parseF(self):
        node = Node("F")
        if self.current.value == "(":
            node.add(self.match("("))
            node.add(self.parseS())
            node.add(self.match(")"))
        elif self.current.type in ("NUMBER", "ID"):
            node.add(self.match_type(self.current.type))
        else:
            self.error("Ожидалось: number, id или '('")
        return node

    def parse(self):
        tree = self.parseS()
        if self.current.type != "EOF":
            self.error("Ожидалось: конец выражения")
        return tree


def parse(text):
    return Parser(Lexer(text)).parse()
