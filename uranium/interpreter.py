from uranium.errors import UraniumError, UraniumRuntimeError
from uranium.statement_parser import Assignment, Evaluation, StatementParser


class Interpreter:
    def __init__(self, builtins):
        self.statement_parser = StatementParser()
        self.global_namespace = {"__builtins__": {}, **builtins}
        self.variables = {}
        self.statement_runners = {
            Assignment: self.run_assignment,
            Evaluation: self.run_evaluation,
        }

    def run_source(self, source):
        for line_number, text in enumerate(source.splitlines(), start=1):
            self.run_line(text, line_number)

    def run_line(self, text, line_number):
        statement = self.statement_parser.parse(text, line_number)
        if statement is None:
            return None
        return self.statement_runners[type(statement)](statement)

    def run_assignment(self, statement):
        self.variables[statement.name] = self.evaluate(statement.code, statement.line)
        return None

    def run_evaluation(self, statement):
        return self.evaluate(statement.code, statement.line)

    def evaluate(self, code, line_number):
        try:
            return eval(code, self.global_namespace, self.variables)
        except UraniumError:
            raise
        except NameError as error:
            raise UraniumRuntimeError(f"unknown name '{error.name}'", line_number) from None
        except ZeroDivisionError:
            raise UraniumRuntimeError("division by zero", line_number) from None
        except Exception as error:
            raise UraniumRuntimeError(str(error), line_number) from error
