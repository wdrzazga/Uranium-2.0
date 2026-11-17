import sys

from uranium.errors import UraniumError


class Console:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.banner = "Uranium 2.0 console - type 'exit' to quit"
        self.prompt = "U> "
        self.exit_commands = {"exit", "quit"}
        self.line_number = 0

    def run(self):
        print(self.banner)
        while True:
            text = self.read_line()
            if text is None or text.strip() in self.exit_commands:
                return 0
            self.line_number += 1
            self.execute(text)

    def read_line(self):
        try:
            return input(self.prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            return None

    def execute(self, text):
        try:
            result = self.interpreter.run_line(text, self.line_number)
        except UraniumError as error:
            print(f"Error: {error.message}", file=sys.stderr)
            return
        if result is not None:
            print(repr(result))
