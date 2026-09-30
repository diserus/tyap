import sys

from errors import ParseError
from parser import parse
from tree import render_tree


def analyze(text):
    try:
        tree = parse(text)
    except ParseError as error:
        print(error)
        position = min(error.pos, len(error.text))
        print(error.text)
        print(" " * position + "^")
        return False
    print("Выражение корректно.")
    print(render_tree(tree))
    return True


def repl():
    while True:
        try:
            text = input("Выражение: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if text == "" or text.lower() == "exit":
            return
        analyze(text)


def main():
    arguments = sys.argv[1:]
    if arguments:
        analyze(" ".join(arguments))
    else:
        repl()


if __name__ == "__main__":
    main()
