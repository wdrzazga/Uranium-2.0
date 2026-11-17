import io
import keyword
import tokenize
from dataclasses import dataclass

from uranium.errors import UraniumSyntaxError


@dataclass
class Assignment:
    name: str
    code: object
    line: int


@dataclass
class Evaluation:
    code: object
    line: int


class StatementParser:
    def __init__(self):
        self.filename = "<uranium>"
        self.forbidden_name_fragment = "__"
        self.ignored_token_types = {
            tokenize.COMMENT,
            tokenize.NL,
            tokenize.NEWLINE,
            tokenize.INDENT,
            tokenize.DEDENT,
            tokenize.ENDMARKER,
        }

    def parse(self, text, line_number):
        source = text.strip()
        tokens = self.significant_tokens(source, line_number)
        if not tokens:
            return None
        self.reject_hidden_names(tokens, line_number)
        code_text = source[:tokens[-1].end[1]]
        if self.is_assignment(tokens):
            value_tokens = tokens[2:]
            if not value_tokens:
                raise UraniumSyntaxError(f"missing value after '{tokens[0].string} ='", line_number)
            code = self.compile_expression(code_text, value_tokens, line_number)
            return Assignment(tokens[0].string, code, line_number)
        return Evaluation(self.compile_expression(code_text, tokens, line_number), line_number)

    def significant_tokens(self, source, line_number):
        try:
            all_tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
        except (tokenize.TokenError, SyntaxError) as error:
            message = error.msg if isinstance(error, SyntaxError) else error.args[0]
            raise UraniumSyntaxError(message, line_number) from None
        return [token for token in all_tokens if token.type not in self.ignored_token_types]

    def reject_hidden_names(self, tokens, line_number):
        for token in tokens:
            if token.type == tokenize.NAME and self.forbidden_name_fragment in token.string:
                raise UraniumSyntaxError(f"names containing '__' are not allowed: '{token.string}'", line_number)

    def is_plain_name(self, token):
        return token.type == tokenize.NAME and not keyword.iskeyword(token.string)

    def is_assignment(self, tokens):
        return len(tokens) > 1 and self.is_plain_name(tokens[0]) and tokens[1].string == "="

    def compile_expression(self, code_text, tokens, line_number):
        expression_text = code_text[tokens[0].start[1]:]
        try:
            return compile(expression_text, self.filename, "eval")
        except SyntaxError as error:
            command_code = self.compile_command(code_text, tokens)
            if command_code is None:
                raise UraniumSyntaxError(error.msg, line_number) from None
            return command_code

    def compile_command(self, code_text, tokens):
        if len(tokens) < 2 or not self.is_plain_name(tokens[0]):
            return None
        command_name = tokens[0].string
        arguments_text = code_text[tokens[0].end[1]:]
        try:
            return compile(f"{command_name}({arguments_text})", self.filename, "eval")
        except SyntaxError:
            return None
