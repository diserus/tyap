import sys

from errors import ParseError
from parser import format_tree, parse


def analyze(text, show_tree=True):
    try:
        tree = parse(text)
    except ParseError as error:
        print(error)
        position = min(error.pos, len(error.text))
        print(error.text)
        print(" " * position + "^")
        return False
    print("Выражение корректно.")
    if show_tree:
        print()
        print(format_tree(tree))
    return True


def repl(show_tree=True):
    while True:
        try:
            text = input("Выражение: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if text == "" or text.lower() == "exit":
            return
        analyze(text, show_tree)


def main():
    arguments = sys.argv[1:]
    show_tree = True
    if "--no-tree" in arguments:
        arguments.remove("--no-tree")
        show_tree = False
    if arguments:
        analyze(" ".join(arguments), show_tree)
    else:
        repl(show_tree)


if __name__ == "__main__":
    main()
