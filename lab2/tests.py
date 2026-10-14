import itertools
import unittest

from automaton import DFA, NFA, minimize_dfa, nfa_to_dfa, parse_automaton


def words(alphabet, max_len):
    for length in range(max_len + 1):
        for letters in itertools.product(sorted(alphabet), repeat=length):
            yield "".join(letters)


BOOK_NFA_TEXT = """
    states p q r
    alphabet 0 1
    start p
    accepting r
    transitions
    p 0 p
    p 1 p q
    q 1 r
"""

BOOK_DFA_TEXT = """
    states q0 q1 q2 q3 q4 q5
    alphabet 0 1
    start q0
    accepting q4 q5
    transitions
    q0 0 q1
    q0 1 q2
    q1 0 q4
    q1 1 q2
    q2 0 q3
    q2 1 q0
    q3 0 q5
    q3 1 q2
    q4 0 q5
    q4 1 q5
    q5 0 q4
    q5 1 q4
"""


def nfa_ends_with_abb():
    return NFA(
        states={"q0", "q1", "q2", "q3"},
        alphabet={"a", "b"},
        transitions={
            "q0": {"a": {"q0", "q1"}, "b": {"q0"}},
            "q1": {"b": {"q2"}},
            "q2": {"b": {"q3"}},
        },
        start="q0",
        accepting={"q3"},
    )


class AutomatonTests(unittest.TestCase):
    def test_nfa_accepts(self):
        nfa = nfa_ends_with_abb()
        self.assertTrue(nfa.accepts("abb"))
        self.assertTrue(nfa.accepts("aabb"))
        self.assertFalse(nfa.accepts("ab"))
        self.assertFalse(nfa.accepts("abba"))

    def test_conversion_preserves_language(self):
        nfa = nfa_ends_with_abb()
        dfa, _ = nfa_to_dfa(nfa)
        for word in words("ab", 7):
            self.assertEqual(nfa.accepts(word), dfa.accepts(word), word)

    def test_conversion_book_example(self):
        nfa = parse_automaton(BOOK_NFA_TEXT)
        dfa, subsets = nfa_to_dfa(nfa)
        self.assertEqual(
            subsets,
            [frozenset({"p"}), frozenset({"p", "q"}), frozenset({"p", "q", "r"})],
        )
        self.assertEqual(dfa.delta(0, "0"), 0)
        self.assertEqual(dfa.delta(0, "1"), 1)
        self.assertEqual(dfa.delta(1, "1"), 2)
        self.assertEqual(dfa.delta(2, "1"), 2)
        self.assertEqual(dfa.accepting, {2})

    def test_conversion_is_deterministic(self):
        dfa, _ = nfa_to_dfa(nfa_ends_with_abb())
        for state in dfa.states:
            for symbol in dfa.alphabet:
                self.assertIn(symbol, dfa.transitions[state])

    def test_minimization_merges_states(self):
        dfa = DFA(
            states={"A", "B", "C", "D"},
            alphabet={"0", "1"},
            transitions={
                "A": {"0": "B", "1": "C"},
                "B": {"0": "A", "1": "D"},
                "C": {"0": "D", "1": "A"},
                "D": {"0": "C", "1": "B"},
            },
            start="A",
            accepting={"A", "C"},
        )
        minimal, blocks = minimize_dfa(dfa)
        self.assertEqual(len(minimal.states), 2)
        self.assertEqual(
            {frozenset(block) for block in blocks},
            {frozenset({"A", "C"}), frozenset({"B", "D"})},
        )
        for word in words("01", 7):
            self.assertEqual(dfa.accepts(word), minimal.accepts(word), word)

    def test_minimization_book_example(self):
        dfa = parse_automaton(BOOK_DFA_TEXT)
        minimal, blocks = minimize_dfa(dfa)
        self.assertEqual(len(minimal.states), 3)
        self.assertEqual(
            {frozenset(block) for block in blocks},
            {
                frozenset({"q4", "q5"}),
                frozenset({"q0", "q2"}),
                frozenset({"q1", "q3"}),
            },
        )

    def test_minimization_removes_unreachable(self):
        dfa = DFA(
            states={"A", "B", "C"},
            alphabet={"a"},
            transitions={"A": {"a": "B"}, "B": {"a": "A"}, "C": {"a": "C"}},
            start="A",
            accepting={"B"},
        )
        minimal, _ = minimize_dfa(dfa)
        self.assertEqual(len(minimal.states), 2)

    def test_universal_language(self):
        dfa = DFA({"A"}, {"a"}, {"A": {"a": "A"}}, "A", {"A"})
        minimal, _ = minimize_dfa(dfa)
        self.assertEqual(len(minimal.states), 1)

    def test_partial_dfa_is_completed(self):
        dfa = DFA(
            states={"A", "B"},
            alphabet={"a", "b"},
            transitions={"A": {"a": "B"}, "B": {"a": "B", "b": "B"}},
            start="A",
            accepting={"B"},
        )
        minimal, _ = minimize_dfa(dfa)
        self.assertEqual(len(minimal.states), 3)
        for word in words("ab", 6):
            self.assertEqual(dfa.accepts(word), minimal.accepts(word), word)

    def test_empty_accepting_rejected(self):
        with self.assertRaises(ValueError):
            DFA({"A"}, {"a"}, {"A": {"a": "A"}}, "A", set())


class ParsingTests(unittest.TestCase):
    def test_parse_nfa(self):
        machine = parse_automaton(BOOK_NFA_TEXT)
        self.assertIsInstance(machine, NFA)
        self.assertTrue(machine.accepts("011"))
        self.assertFalse(machine.accepts("010"))

    def test_parse_dfa(self):
        text = """
            states s0 s1
            alphabet 0 1
            start s0
            accepting s1
            transitions
            s0 0 s0
            s0 1 s1
            s1 0 s0
            s1 1 s1
        """
        machine = parse_automaton(text)
        self.assertIsInstance(machine, DFA)
        self.assertTrue(machine.accepts("1"))
        self.assertFalse(machine.accepts("0"))

    def test_unknown_state_rejected(self):
        text = """
            states p
            alphabet a
            start p
            accepting p
            transitions
            p a z
        """
        with self.assertRaises(ValueError):
            parse_automaton(text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
