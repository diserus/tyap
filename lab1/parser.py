from errors import ParseError
from lexer import Lexer


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current = lexer.getNextToken()

    def error(self, message):
        raise ParseError(message, self.current.pos, self.lexer.text)

    def match(self, expected_value):
        if self.current.value == expected_value:
            self.current = self.lexer.getNextToken()
            return
        self.error(f"Ожидалось: '{expected_value}'")

    def match_type(self, expected_type):
        if self.current.type == expected_type:
            self.current = self.lexer.getNextToken()
            return
        self.error(f"Ожидалось: {expected_type}")

    def parseS(self):
        self.parseE()

    def parseE(self):
        self.parseT()
        self.parseEPrime()

    def parseEPrime(self):
        if self.current.value in ("+", "-"):
            self.current = self.lexer.getNextToken()
            self.parseT()
            self.parseEPrime()

    def parseT(self):
        self.parseF()
        self.parseTPrime()

    def parseTPrime(self):
        if self.current.value in ("*", "/"):
            self.current = self.lexer.getNextToken()
            self.parseF()
            self.parseTPrime()

    def parseF(self):
        if self.current.value == "(":
            self.match("(")
            self.parseS()
            self.match(")")
        elif self.current.type in ("NUMBER", "ID"):
            self.match_type(self.current.type)
        else:
            self.error("Ожидалось: number, id или '('")

    def parse(self):
        self.parseS()
        if self.current.type != "EOF":
            self.error("Ожидалось: конец выражения")


def parse(text):
    Parser(Lexer(text)).parse()
