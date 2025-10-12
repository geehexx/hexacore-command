"""Hexa-Script runner implementation using a simple bytecode interpreter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Self

Token = tuple[str, list[str]]
Instruction = tuple[str, tuple[Any, ...]]


@dataclass
class ScriptProgram:
    instructions: list[Instruction]
    labels: dict[str, int]


class ScriptParseError(ValueError):
    """Raised when Hexa-Script source cannot be parsed."""


class ScriptRuntimeError(RuntimeError):
    """Raised when Hexa-Script execution fails."""


class ScriptRunner:
    """Hexa-Script execution engine supporting a minimal instruction set."""

    def __init__(self: Self) -> None:
        self._program: ScriptProgram | None = None

    def load(self: Self, source: str) -> None:
        """Compile Hexa-Script source into an internal instruction list."""

        tokens = self._tokenize(source)
        self._program = self._compile(tokens)

    def execute(self: Self, context: dict[str, Any]) -> None:
        """Execute the loaded program against the provided context."""

        if self._program is None:
            raise ScriptRuntimeError("No script loaded")

        variables = context.setdefault("variables", {})
        actions = context.setdefault("actions", [])
        if not isinstance(variables, dict):
            raise ScriptRuntimeError("Context 'variables' must be a dictionary")
        if not isinstance(actions, list):
            raise ScriptRuntimeError("Context 'actions' must be a list")

        pc = 0
        program = self._program.instructions
        labels = self._program.labels

        while pc < len(program):
            opcode, operands = program[pc]
            if opcode == "SET":
                name, expr = operands
                variables[name] = self._evaluate(expr, variables)
                pc += 1
            elif opcode == "GOTO":
                label = operands[0]
                if label not in labels:
                    msg = f"Label '{label}' not defined"
                    raise ScriptRuntimeError(msg)
                pc = labels[label]
            elif opcode == "IF_GOTO":
                left, op, right, label = operands
                if self._evaluate_condition(left, op, right, variables):
                    if label not in labels:
                        msg = f"Label '{label}' not defined"
                        raise ScriptRuntimeError(msg)
                    pc = labels[label]
                else:
                    pc += 1
            elif opcode == "IF_THEN":
                left, op, right, next_instruction = operands
                if self._evaluate_condition(left, op, right, variables):
                    opcode, more_operands = next_instruction
                    if opcode == "SET":
                        name, expr = more_operands
                        variables[name] = self._evaluate(expr, variables)
                        pc += 1
                    elif opcode == "ACTION":
                        action_name, args = more_operands
                        actions.append((action_name, tuple(self._evaluate(arg, variables) for arg in args)))
                        pc += 1
                    elif opcode == "GOTO":
                        label = more_operands[0]
                        if label not in labels:
                            msg = f"Label '{label}' not defined"
                            raise ScriptRuntimeError(msg)
                        pc = labels[label]
                    else:
                        msg = f"Unsupported inline THEN command '{opcode}'"
                        raise ScriptRuntimeError(msg)
                else:
                    pc += 1
            elif opcode == "ACTION":
                name, args = operands
                actions.append((name, tuple(self._evaluate(arg, variables) for arg in args)))
                pc += 1
            elif opcode == "END":
                break
            else:  # pragma: no cover - defensive guard
                msg = f"Unknown opcode '{opcode}'"
                raise ScriptRuntimeError(msg)

    # -- Compilation helpers -------------------------------------------------

    def _tokenize(self: Self, source: str) -> list[Token]:
        tokens: list[Token] = []
        for raw_line in source.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            current: list[str] = []
            buffer = ""
            in_quote = False
            i = 0
            while i < len(line):
                char = line[i]
                if char == '"':
                    if in_quote:
                        current.append(f'"{buffer}"')
                        buffer = ""
                    in_quote = not in_quote
                    i += 1
                    continue
                if in_quote:
                    buffer += char
                    i += 1
                    continue
                if char.isspace():
                    if buffer:
                        current.append(buffer)
                        buffer = ""
                    i += 1
                    continue
                if char in "()":
                    if buffer:
                        current.append(buffer)
                        buffer = ""
                    current.append(char)
                    i += 1
                    continue
                buffer += char
                i += 1
            if buffer:
                current.append(buffer)
            if not current:
                continue
            keyword = current[0].upper()
            tokens.append((keyword, current[1:]))
        return tokens

    def _compile(self: Self, tokens: list[Token]) -> ScriptProgram:
        instructions: list[Instruction] = []
        labels: dict[str, int] = {}

        for keyword, args in tokens:
            if keyword == "LABEL":
                label_name = self._expect_string(args, 0)
                labels[label_name] = len(instructions)
            elif keyword == "SET":
                name = self._expect_string(args, 0)
                expression = self._parse_expression(args[1:])
                instructions.append(("SET", (name, expression)))
            elif keyword == "GOTO":
                label_name = self._expect_string(args, 0)
                instructions.append(("GOTO", (label_name,)))
            elif keyword == "IF":
                condition_tokens, remainder = self._split_condition(args)
                left, op, right = self._parse_condition(condition_tokens)
                if remainder and remainder[0].upper() == "THEN":
                    inline_tokens = remainder[1:]
                    if inline_tokens and inline_tokens[0].upper() == "GOTO":
                        label_name = self._expect_string(inline_tokens, 1)
                        instructions.append(("IF_GOTO", (left, op, right, label_name)))
                    else:
                        inline_instruction = self._parse_inline(inline_tokens)
                        instructions.append(("IF_THEN", (left, op, right, inline_instruction)))
                elif remainder and remainder[0].upper() == "GOTO":
                    label_name = self._expect_string(remainder, 1)
                    instructions.append(("IF_GOTO", (left, op, right, label_name)))
                else:
                    msg = "IF statement must be followed by THEN or GOTO"
                    raise ScriptParseError(msg)
            elif keyword == "ACTION":
                name = self._expect_string(args, 0)
                action_args = [self._parse_value(arg) for arg in args[1:]]
                instructions.append(("ACTION", (name, tuple(action_args))))
            elif keyword == "END":
                instructions.append(("END", tuple()))
            else:
                msg = f"Unknown keyword '{keyword}'"
                raise ScriptParseError(msg)

        instructions.append(("END", tuple()))
        return ScriptProgram(instructions=instructions, labels=labels)

    def _parse_expression(self: Self, tokens: list[str]) -> Any:
        if not tokens:
            msg = "Expression expected"
            raise ScriptParseError(msg)
        if tokens[0] == "(":
            if tokens[-1] != ")" or len(tokens) < 4:
                msg = "Malformed expression"
                raise ScriptParseError(msg)
            left = self._parse_value(tokens[1])
            op = tokens[2]
            right = self._parse_value(tokens[3])
            return ("EXPR", left, op, right)
        if len(tokens) != 1:
            msg = "Unexpected tokens in expression"
            raise ScriptParseError(msg)
        return self._parse_value(tokens[0])

    def _parse_value(self: Self, token: str) -> Any:
        stripped = self._strip_quotes(token)
        if stripped is not None:
            return stripped
        if token.isdigit():
            return int(token)
        if token.replace("-", "", 1).isdigit():
            return int(token)
        return ("VAR", token)

    def _split_condition(self: Self, tokens: list[str]) -> tuple[list[str], list[str]]:
        for index, token in enumerate(tokens):
            if token.upper() in {"THEN", "GOTO"}:
                return tokens[:index], tokens[index:]
        return tokens, []

    def _parse_condition(self: Self, tokens: list[str]) -> tuple[Any, str, Any]:
        if len(tokens) < 3:
            msg = "Incomplete condition"
            raise ScriptParseError(msg)
        left = self._parse_value(tokens[0])
        op = tokens[1]
        right = self._parse_value(tokens[2])
        return left, op, right

    def _parse_inline(self: Self, tokens: list[str]) -> Instruction:
        if not tokens:
            msg = "Inline command missing"
            raise ScriptParseError(msg)
        keyword = tokens[0].upper()
        if keyword == "SET":
            name = self._expect_string(tokens, 1)
            expression = self._parse_expression(tokens[2:])
            return ("SET", (name, expression))
        if keyword == "ACTION":
            name = self._expect_string(tokens, 1)
            args = [self._parse_value(token) for token in tokens[2:]]
            return ("ACTION", (name, tuple(args)))
        if keyword == "GOTO":
            label_name = self._expect_string(tokens, 1)
            return ("GOTO", (label_name,))
        msg = f"Unsupported inline THEN command '{keyword}'"
        raise ScriptParseError(msg)

    def _expect_string(self: Self, tokens: list[str], index: int) -> str:
        try:
            value = tokens[index]
        except IndexError as exc:  # pragma: no cover - defensive guard
            raise ScriptParseError("Missing argument") from exc
        stripped = self._strip_quotes(value)
        return stripped if stripped is not None else value

    def _strip_quotes(self: Self, token: str) -> str | None:
        if len(token) >= 2 and token[0] == '"' and token[-1] == '"':
            return token[1:-1]
        return None

    # -- Evaluation helpers --------------------------------------------------

    def _evaluate(self: Self, value: Any, variables: dict[str, Any]) -> Any:
        if isinstance(value, tuple) and value:
            tag = value[0]
            if tag == "VAR":
                name = value[1]
                return variables.get(name, 0)
            if tag == "EXPR":
                _, left, op, right = value
                left_value = self._evaluate(left, variables)
                right_value = self._evaluate(right, variables)
                return self._apply_operator(op, left_value, right_value)
        return value

    def _evaluate_condition(self: Self, left: Any, op: str, right: Any, variables: dict[str, Any]) -> bool:
        left_value = self._evaluate(left, variables)
        right_value = self._evaluate(right, variables)
        return self._apply_comparison(op, left_value, right_value)

    def _apply_operator(self: Self, op: str, left: Any, right: Any) -> Any:
        operators: dict[str, Callable[[Any, Any], Any]] = {
            "+": lambda a, b: a + b,
            "-": lambda a, b: a - b,
            "*": lambda a, b: a * b,
            "/": lambda a, b: a // b,
        }
        if op not in operators:
            msg = f"Unsupported operator '{op}'"
            raise ScriptRuntimeError(msg)
        return operators[op](left, right)

    def _apply_comparison(self: Self, op: str, left: Any, right: Any) -> bool:
        comparisons: dict[str, Callable[[Any, Any], bool]] = {
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            ">": lambda a, b: a > b,
            "<": lambda a, b: a < b,
            ">=": lambda a, b: a >= b,
            "<=": lambda a, b: a <= b,
        }
        if op not in comparisons:
            msg = f"Unsupported comparison '{op}'"
            raise ScriptRuntimeError(msg)
        return comparisons[op](left, right)
