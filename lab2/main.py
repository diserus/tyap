import sys

from automaton import NFA, format_automaton, minimize_dfa, nfa_to_dfa, parse_automaton


def show(title, automaton, composition=None):
    print(f"=== {title} ===")
    print(format_automaton(automaton, composition))


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as stream:
            text = stream.read()
    else:
        text = sys.stdin.read()

    try:
        machine = parse_automaton(text)
    except ValueError as error:
        print(f"Ошибка! {error}")
        return 1

    show("Исходный автомат", machine)

    subsets = None
    if isinstance(machine, NFA):
        machine, subsets = nfa_to_dfa(machine)
        composition = {i: subsets[i] for i in range(len(subsets))}
        print()
        show("ДКА после перевода (метод подмножеств)", machine, composition)

    machine, blocks = minimize_dfa(machine)
    if subsets is None:
        composition = {i: blocks[i] for i in range(len(blocks))}
    else:
        composition = {}
        for i, block in enumerate(blocks):
            members = set()
            for state in block:
                members |= set(subsets[state])
            composition[i] = members
    print()
    show("Минимальный ДКА", machine, composition)
    return 0


if __name__ == "__main__":
    sys.exit(main())
