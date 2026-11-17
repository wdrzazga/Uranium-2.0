class UraniumError(Exception):
    def __init__(self, message, line):
        super().__init__(f"line {line}: {message}")
        self.message = message
        self.line = line


class UraniumSyntaxError(UraniumError):
    pass


class UraniumRuntimeError(UraniumError):
    pass
