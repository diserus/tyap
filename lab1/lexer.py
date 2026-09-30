import re

from errors import ParseError

TOKEN_RE = re.compile(
    r"""
      (?P<SKIP>    \s+ )
    | (?P<NUMBER>  \d+(?:\.\d+)? )
    | (?P<ID>      [A-Za-z_][A-Za-z0-9_]* )
    | (?P<PLUS>    \+ )
    | (?P<MINUS>   -  )
    | (?P<STAR>    \* )
    | (?P<SLASH>   /  )
    | (?P<LPAREN>  \( )
    | (?P<RPAREN>  \) )
    | (?P<MISMATCH> . )
    """,
    re.VERBOSE,
)

SYMBOL_TYPES = {
    "PLUS": "+",
    "MINUS": "-",
    "STAR": "*",
    "SLASH": "/",
    "LPAREN": "(",
    "RPAREN": ")",
}


class Token:
    __slots__ = ("type", "value", "pos")

    def __init__(self, type_, value, pos):
        self.type = type_
        self.value = value
        self.pos = pos

    def __repr__(self):
        return f"Token({self.type!r}, {self.value!r}, pos={self.pos})"


class Lexer:
    def __init__(self, text):
        self.text = text
        self.tokens = self._tokenize()
        self.tokens.append(Token("EOF", None, len(text)))
        self.index = 0

    def _tokenize(self):
        tokens = []
        for m in TOKEN_RE.finditer(self.text):
            kind = m.lastgroup
            value = m.group()

            if kind == "SKIP":
                continue
            if kind == "MISMATCH":
                raise ParseError(
                    f"Недопустимый символ: '{value}'", m.start(), self.text
                )
            if kind in ("NUMBER", "ID"):
                tokens.append(Token(kind, value, m.start()))
            else:
                tokens.append(Token("SYMBOL", SYMBOL_TYPES[kind], m.start()))
        return tokens

    def getNextToken(self):
        tok = self.tokens[self.index]
        if tok.type != "EOF":
            self.index += 1
        return tok

    def peek(self):
        return self.tokens[self.index]
