import unittest

from errors import ParseError
from parser import Node, format_tree, parse


class TestValid(unittest.TestCase):
    def assert_ok(self, text):
        try:
            parse(text)
        except ParseError as e:
            self.fail(f"Ожидалось, что {text!r} корректно, но получено: {e}")

    def test_numbers(self):
        for text in ["1", "42", "3.14", "  7  "]:
            self.assert_ok(text)

    def test_ids(self):
        for text in ["a", "x1", "_tmp", "abc_def"]:
            self.assert_ok(text)

    def test_operators(self):
        for text in [
            "2 + 3 * 4",
            "a * (b - 10)",
            "1 + 2 - 3 + 4",
            "2 * 3 / 4 * 5",
            "(1 + 2) * (3 - 4)",
            "((((5))))",
            "a / b / c",
            "x * (y + z) - 1",
        ]:
            self.assert_ok(text)


class TestInvalid(unittest.TestCase):
    def assert_err(self, text, fragment):
        try:
            parse(text)
        except ParseError as e:
            self.assertIn(fragment, str(e), f"для {text!r}: {e}")
        else:
            self.fail(f"Ожидалась ошибка для {text!r}")

    def test_double_operator(self):
        self.assert_err("5 + + 3", "number, id или '('")

    def test_unclosed_paren(self):
        self.assert_err("(7 * 2", "')'")

    def test_empty(self):
        self.assert_err("", "number, id или '('")

    def test_trailing_token(self):
        self.assert_err("1 2", "конец выражения")

    def test_bad_char(self):
        self.assert_err("2 @ 3", "Недопустимый символ")

    def test_missing_operand(self):
        self.assert_err("1 *", "number, id или '('")

    def test_extra_paren(self):
        self.assert_err("1 + 2)", "конец выражения")


class TestTree(unittest.TestCase):
    def test_root(self):
        tree = parse("1")
        self.assertIsInstance(tree, Node)
        self.assertEqual(tree.label, "S")

    def test_leaf_values(self):
        number = parse("3.14").children[0].children[0].children[0]
        self.assertEqual(number.label, "F")
        self.assertEqual(number.children[0].label, "number:3.14")
        identifier = parse("abc").children[0].children[0].children[0]
        self.assertEqual(identifier.children[0].label, "id:abc")

    def test_precedence(self):
        tree = parse("2 + 3 * 4")
        expression = tree.children[0]
        self.assertEqual(expression.label, "E")
        term, tail = expression.children
        self.assertEqual(term.label, "T")
        self.assertEqual(tail.label, "E'")
        operator, right_term, rest = tail.children
        self.assertEqual(operator.label, "+")
        self.assertEqual(right_term.label, "T")
        self.assertEqual(rest.label, "E'")
        right_term_tail = right_term.children[1]
        self.assertEqual(right_term_tail.children[0].label, "*")

    def test_parentheses(self):
        tree = parse("(1)")
        factor = tree.children[0].children[0].children[0]
        self.assertEqual(factor.label, "F")
        self.assertEqual([child.label for child in factor.children], ["(", "S", ")"])

    def test_format_tree(self):
        tree = parse("a")
        expected = "\n".join(
            [
                "S",
                "└── E",
                "    ├── T",
                "    │   ├── F",
                "    │   │   └── id:a",
                "    │   └── T'",
                "    │       └── ε",
                "    └── E'",
                "        └── ε",
            ]
        )
        self.assertEqual(format_tree(tree), expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
