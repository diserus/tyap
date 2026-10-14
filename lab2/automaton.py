from collections import deque


class Automaton:
    def __init__(self, states, alphabet, start, accepting):
        self.states = set(states)
        self.alphabet = set(alphabet)
        self.start = start
        self.accepting = set(accepting)
        if not self.states:
            raise ValueError("Множество состояний Q не может быть пустым")
        if not self.accepting:
            raise ValueError("Множество конечных состояний F не может быть пустым")
        if self.start not in self.states:
            raise ValueError(f"Начальное состояние {self.start!r} отсутствует в Q")
        if not self.accepting <= self.states:
            raise ValueError("Конечные состояния должны входить в Q")


class NFA(Automaton):
    def __init__(self, states, alphabet, transitions, start, accepting):
        super().__init__(states, alphabet, start, accepting)
        self.transitions = {state: {} for state in self.states}
        for state, by_symbol in transitions.items():
            for symbol, targets in by_symbol.items():
                if symbol not in self.alphabet:
                    raise ValueError(f"Символ {symbol!r} отсутствует в алфавите V")
                targets = set(targets)
                if not targets <= self.states:
                    raise ValueError("Переход в неизвестное состояние")
                self.transitions[state][symbol] = targets

    def move(self, states, symbol):
        result = set()
        for state in states:
            result |= self.transitions.get(state, {}).get(symbol, set())
        return result

    def accepts(self, word):
        current = {self.start}
        for symbol in word:
            current = self.move(current, symbol)
            if not current:
                return False
        return bool(current & self.accepting)


class DFA(Automaton):
    def __init__(self, states, alphabet, transitions, start, accepting):
        super().__init__(states, alphabet, start, accepting)
        self.transitions = {state: {} for state in self.states}
        for state, by_symbol in transitions.items():
            for symbol, target in by_symbol.items():
                if symbol not in self.alphabet:
                    raise ValueError(f"Символ {symbol!r} отсутствует в алфавите V")
                if target not in self.states:
                    raise ValueError("Переход в неизвестное состояние")
                self.transitions[state][symbol] = target

    def delta(self, state, symbol):
        return self.transitions.get(state, {}).get(symbol)

    def accepts(self, word):
        state = self.start
        for symbol in word:
            state = self.delta(state, symbol)
            if state is None:
                return False
        return state in self.accepting


def nfa_to_dfa(nfa):
    start = frozenset({nfa.start})
    subsets = [start]
    index = {start: 0}
    transitions = {}
    queue = deque([start])

    while queue:
        current = queue.popleft()
        for symbol in sorted(nfa.alphabet):
            target = frozenset(nfa.move(current, symbol))
            if not target:
                continue
            if target not in index:
                index[target] = len(subsets)
                subsets.append(target)
                queue.append(target)
            transitions.setdefault(index[current], {})[symbol] = index[target]

    accepting = {i for i, subset in enumerate(subsets) if subset & nfa.accepting}
    dfa = DFA(
        set(range(len(subsets))),
        nfa.alphabet,
        transitions,
        index[start],
        accepting,
    )
    return dfa, subsets


def minimize_dfa(dfa):
    states = _reachable(dfa)

    dead = "__dead__"
    while dead in states:
        dead += "_"
    transitions = {state: {} for state in states}
    need_dead = False
    for state in states:
        for symbol in dfa.alphabet:
            target = dfa.delta(state, symbol)
            if target is None:
                target = dead
                need_dead = True
            transitions[state][symbol] = target
    if need_dead:
        states.add(dead)
        transitions[dead] = {symbol: dead for symbol in dfa.alphabet}
    accepting = dfa.accepting & states

    blocks = []
    if accepting:
        blocks.append(set(accepting))
    if states - accepting:
        blocks.append(states - accepting)

    alphabet = sorted(dfa.alphabet)
    while True:
        number = {state: i for i, block in enumerate(blocks) for state in block}
        refined = []
        for block in blocks:
            parts = {}
            for state in block:
                key = tuple(number[transitions[state][c]] for c in alphabet)
                parts.setdefault(key, set()).add(state)
            refined.extend(parts.values())
        if len(refined) == len(blocks):
            break
        blocks = refined

    number = {state: i for i, block in enumerate(blocks) for state in block}
    result_transitions = {}
    for i, block in enumerate(blocks):
        representative = next(iter(block))
        result_transitions[i] = {
            c: number[transitions[representative][c]] for c in alphabet
        }

    result = DFA(
        set(range(len(blocks))),
        dfa.alphabet,
        result_transitions,
        number[dfa.start],
        {number[state] for state in accepting},
    )
    return result, blocks


def _reachable(dfa):
    seen = {dfa.start}
    queue = deque([dfa.start])
    while queue:
        state = queue.popleft()
        for symbol in dfa.alphabet:
            target = dfa.delta(state, symbol)
            if target is not None and target not in seen:
                seen.add(target)
                queue.append(target)
    return seen


def parse_automaton(text):
    states = alphabet = start = None
    accepting = set()
    raw_transitions = {}
    in_transitions = False

    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        key = parts[0].lower()
        if key == "states":
            states = parts[1:]
        elif key == "alphabet":
            alphabet = parts[1:]
        elif key == "start":
            start = parts[1]
        elif key == "accepting":
            accepting.update(parts[1:])
        elif key == "transitions":
            in_transitions = True
        elif in_transitions:
            if len(parts) < 3:
                raise ValueError(f"Строка {lineno}: нужен формат 's символ t…'")
            raw_transitions.setdefault((parts[0], parts[1]), set()).update(parts[2:])
        else:
            raise ValueError(f"Строка {lineno}: неизвестная директива {parts[0]!r}")

    if states is None or alphabet is None or start is None:
        raise ValueError("Обязательны директивы states, alphabet и start")

    nested = {state: {} for state in states}
    for (source, symbol), targets in raw_transitions.items():
        nested.setdefault(source, {}).setdefault(symbol, set()).update(targets)

    nondeterministic = any(len(targets) > 1 for targets in raw_transitions.values())
    if nondeterministic:
        return NFA(states, alphabet, nested, start, accepting)

    deterministic = {
        state: {symbol: next(iter(targets)) for symbol, targets in by.items()}
        for state, by in nested.items()
    }
    return DFA(states, alphabet, deterministic, start, accepting)


def format_automaton(automaton, composition=None):
    lines = [
        f"  Состояния:   {', '.join(str(s) for s in sorted(automaton.states, key=str))}",
        f"  Алфавит:     {', '.join(sorted(automaton.alphabet))}",
        f"  Начальное:   {automaton.start}",
        f"  Конечные:    {', '.join(str(s) for s in sorted(automaton.accepting, key=str))}",
        "  Переходы:",
    ]
    for state in sorted(automaton.states, key=str):
        for symbol in sorted(automaton.transitions.get(state, {})):
            if isinstance(automaton, NFA):
                targets = automaton.transitions[state][symbol]
                target = "{" + ", ".join(str(t) for t in sorted(targets, key=str)) + "}"
            else:
                target = str(automaton.transitions[state][symbol])
            lines.append(f"    {state} --{symbol}--> {target}")
    if composition:
        lines.append("  Состав состояний:")
        for state in sorted(composition, key=str):
            members = ", ".join(str(m) for m in sorted(composition[state], key=str))
            lines.append(f"    {state} = {{{members}}}")
    return "\n".join(lines)
