"""Hexa-Script runner implementation using a simple bytecode interpreter."""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from typing import Final, Self, TypeAlias, cast

VariableValue: TypeAlias = int | str


@dataclass(frozen=True)
class VariableRef:
    """Reference to a variable stored in the execution context."""

    name: str


@dataclass(frozen=True)
class BinaryExpression:
    """Binary arithmetic expression."""

    left: Expression
    operator: str
    right: Expression


Expression: TypeAlias = VariableValue | VariableRef | BinaryExpression


@dataclass(frozen=True)
class SetInstruction:
    name: str
    expression: Expression


@dataclass(frozen=True)
class ActionInstruction:
    name: str
    arguments: tuple[Expression, ...]


@dataclass(frozen=True)
class GotoInstruction:
    label: str


@dataclass(frozen=True)
class IfGotoInstruction:
    left: Expression
    operator: str
    right: Expression
    label: str


@dataclass(frozen=True)
class IfThenInstruction:
    left: Expression
    operator: str
    right: Expression
    inline_instruction: InlineInstruction


@dataclass(frozen=True)
class EndInstruction:
    pass


InlineInstruction: TypeAlias = SetInstruction | ActionInstruction | GotoInstruction
Instruction: TypeAlias = InlineInstruction | IfGotoInstruction | IfThenInstruction | EndInstruction
Token: TypeAlias = tuple[str, tuple[str, ...]]
ActionRecord: TypeAlias = tuple[str, tuple[VariableValue, ...]]

_OPERATOR_FUNCTIONS: Final[dict[str, Callable[[int, int], int]]] = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a // b,
}

_EQUALITY_OPERATORS: Final[set[str]] = {"==", "!="}
_COMPARISON_OPERATORS: Final[set[str]] = {"<", "<=", ">", ">="}


class ScriptParseError(ValueError):
    """Raised when Hexa-Script source cannot be parsed."""


class ScriptRuntimeError(RuntimeError):
    """Raised when Hexa-Script execution fails."""


@dataclass
class ScriptProgram:
    instructions: list[Instruction]
    labels: dict[str, int]


@dataclass
class ExecutionContext:
    variables: dict[str, VariableValue]
    actions: list[ActionRecord]


TOKEN_PATTERN: Final[re.Pattern[str]] = re.compile(r'"[^"]*"|\(|\)|\S+')


class ScriptRunner:
    """Hexa-Script execution engine supporting a minimal instruction set."""

    def __init__(self: Self) -> None:
        self._program: ScriptProgram | None = None

    def load(self: Self, source: str) -> None:
        """Compile Hexa-Script source into an internal instruction list."""

        tokens = self._tokenize(source)
        self._program = self._compile(tokens)

    def execute(self: Self, context: dict[str, object]) -> None:
        """Execute the loaded program against the provided context."""

        if self._program is None:
            raise ScriptRuntimeError("No script loaded")

        exec_context = self._normalize_context(context)
        instructions = self._program.instructions
        labels = self._program.labels

        pc = 0
        while pc < len(instructions):
            instruction = instructions[pc]
            match instruction:
                case SetInstruction(name=name, expression=expression):
                    exec_context.variables[name] = self._evaluate(expression, exec_context.variables)
                    pc += 1
                case GotoInstruction(label=label):
                    pc = self._jump_to(label, labels)
                case IfGotoInstruction(left=left, operator=op, right=right, label=label):
                    if self._evaluate_condition(left, op, right, exec_context.variables):
                        pc = self._jump_to(label, labels)
                    else:
                        pc += 1
                case IfThenInstruction(left=left, operator=op, right=right, inline_instruction=inline_instr):
                    if self._evaluate_condition(left, op, right, exec_context.variables):
                        pc = self._execute_inline(inline_instr, pc, exec_context, labels)
                    else:
                        pc += 1
                case ActionInstruction(name=name, arguments=arguments):
                    result = tuple(self._evaluate(arg, exec_context.variables) for arg in arguments)
                    exec_context.actions.append((name, result))
                    pc += 1
                case EndInstruction():
                    break
                case _:
                    msg = f"Unknown instruction '{instruction}'"
                    raise ScriptRuntimeError(msg)

    # -- Context helpers -------------------------------------------------

    def _normalize_context(self: Self, context: dict[str, object]) -> ExecutionContext:
        variables_obj = context.setdefault("variables", {})
        if not isinstance(variables_obj, dict):
            raise ScriptRuntimeError("Context 'variables' must be a dictionary")
        for key, value in variables_obj.items():
            if not isinstance(key, str):
                raise ScriptRuntimeError("Variable names must be strings")
            if not isinstance(value, int | str):
                raise ScriptRuntimeError("Variable values must be ints or strings")

        actions_obj = context.setdefault("actions", [])
        if not isinstance(actions_obj, list):
            raise ScriptRuntimeError("Context 'actions' must be a list")
        for action in actions_obj:
            if not (
                isinstance(action, tuple)
                and len(action) == 2
                and isinstance(action[0], str)
                and isinstance(action[1], tuple)
                and all(isinstance(arg, int | str) for arg in action[1])
            ):
                raise ScriptRuntimeError("Recorded actions must be tuples of name and argument tuple")

        return ExecutionContext(
            variables=cast(dict[str, VariableValue], variables_obj),
            actions=cast(list[ActionRecord], actions_obj),
        )

    def _execute_inline(
        self: Self,
        instruction: InlineInstruction,
        pc: int,
        context: ExecutionContext,
        labels: dict[str, int],
    ) -> int:
        match instruction:
            case SetInstruction(name=name, expression=expression):
                context.variables[name] = self._evaluate(expression, context.variables)
                return pc + 1
            case ActionInstruction(name=name, arguments=arguments):
                result = tuple(self._evaluate(arg, context.variables) for arg in arguments)
                context.actions.append((name, result))
                return pc + 1
            case GotoInstruction(label=label):
                return self._jump_to(label, labels)
        msg = f"Unsupported inline instruction '{instruction}'"
        raise ScriptRuntimeError(msg)

    def _jump_to(self: Self, label: str, labels: dict[str, int]) -> int:
        try:
            return labels[label]
        except KeyError as exc:
            raise ScriptRuntimeError(f"Label '{label}' not defined") from exc

    # -- Evaluation helpers -------------------------------------------------

    def _evaluate(self: Self, value: Expression, variables: dict[str, VariableValue]) -> VariableValue:
        if isinstance(value, VariableRef):
            return variables.get(value.name, 0)
        if isinstance(value, BinaryExpression):
            left_value = self._require_int(self._evaluate(value.left, variables))
            right_value = self._require_int(self._evaluate(value.right, variables))
            operator = value.operator
            if operator not in _OPERATOR_FUNCTIONS:
                msg = f"Unsupported operator '{operator}'"
                raise ScriptRuntimeError(msg)
            return _OPERATOR_FUNCTIONS[operator](left_value, right_value)
        return value

    def _evaluate_condition(
        self: Self,
        left: Expression,
        operator: str,
        right: Expression,
        variables: dict[str, VariableValue],
    ) -> bool:
        left_value = self._evaluate(left, variables)
        right_value = self._evaluate(right, variables)

        if operator in _EQUALITY_OPERATORS:
            if operator == "==":
                return left_value == right_value
            return left_value != right_value
        if operator in _COMPARISON_OPERATORS:
            left_int = self._require_int(left_value)
            right_int = self._require_int(right_value)
            if operator == "<":
                return left_int < right_int
            if operator == "<=":
                return left_int <= right_int
            if operator == ">":
                return left_int > right_int
            if operator == ">=":
                return left_int >= right_int
        msg = f"Unsupported comparison '{operator}'"
        raise ScriptRuntimeError(msg)

    def _require_int(self: Self, value: VariableValue) -> int:
        if not isinstance(value, int):
            msg = f"Expected integer value, received {value!r}"
            raise ScriptRuntimeError(msg)
        return value

    # -- Tokenization -------------------------------------------------

    def _tokenize(self: Self, source: str) -> list[Token]:
        tokens: list[Token] = []
        for raw_line in source.splitlines():
            token = self._tokenize_line(raw_line)
            if token is not None:
                tokens.append(token)
        return tokens

    def _tokenize_line(self: Self, raw_line: str) -> Token | None:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            return None

        parts = TOKEN_PATTERN.findall(line)
        if not parts:
            return None
        keyword, *args = parts
        return keyword.upper(), tuple(args)

    # -- Compilation -------------------------------------------------

    def _compile(self: Self, tokens: Iterable[Token]) -> ScriptProgram:
        instructions: list[Instruction] = []
        labels: dict[str, int] = {}

        for keyword, arguments in tokens:
            if keyword == "LABEL":
                label_name = self._expect_string(arguments, 0)
                labels[label_name] = len(instructions)
                continue
            instructions.extend(self._compile_token(keyword, arguments, labels))

        if not instructions or not isinstance(instructions[-1], EndInstruction):
            instructions.append(EndInstruction())
        return ScriptProgram(instructions=instructions, labels=labels)

    def _compile_token(
        self: Self,
        keyword: str,
        arguments: Sequence[str],
        labels: dict[str, int],
    ) -> list[Instruction]:
        if keyword == "SET":
            name = self._expect_string(arguments, 0)
            expression = self._parse_expression(arguments[1:])
            return [SetInstruction(name=name, expression=expression)]
        if keyword == "GOTO":
            label_name = self._expect_string(arguments, 0)
            return [GotoInstruction(label=label_name)]
        if keyword == "IF":
            condition_tokens, remainder = self._split_condition(arguments)
            left, operator, right = self._parse_condition(condition_tokens)
            if remainder and remainder[0].upper() == "THEN":
                inline_tokens = remainder[1:]
                if inline_tokens and inline_tokens[0].upper() == "GOTO":
                    label_name = self._expect_string(inline_tokens, 1)
                    return [IfGotoInstruction(left=left, operator=operator, right=right, label=label_name)]
                inline_instruction = self._parse_inline(inline_tokens)
                return [
                    IfThenInstruction(
                        left=left,
                        operator=operator,
                        right=right,
                        inline_instruction=inline_instruction,
                    )
                ]
            if remainder and remainder[0].upper() == "GOTO":
                label_name = self._expect_string(remainder, 1)
                return [IfGotoInstruction(left=left, operator=operator, right=right, label=label_name)]
            raise ScriptParseError("IF statement must be followed by THEN or GOTO")
        if keyword == "ACTION":
            name = self._expect_string(arguments, 0)
            action_args = tuple(self._parse_value(arg) for arg in arguments[1:])
            return [ActionInstruction(name=name, arguments=action_args)]
        if keyword == "END":
            return [EndInstruction()]
        raise ScriptParseError(f"Unknown keyword '{keyword}'")

    def _parse_expression(self: Self, tokens: Sequence[str]) -> Expression:
        if not tokens:
            raise ScriptParseError("Expression expected")
        if tokens[0] == "(":
            if tokens[-1] != ")" or len(tokens) < 4:
                raise ScriptParseError("Malformed expression")
            left = self._parse_value(tokens[1])
            operator = tokens[2]
            right = self._parse_value(tokens[3])
            return BinaryExpression(left=left, operator=operator, right=right)
        if len(tokens) != 1:
            raise ScriptParseError("Unexpected tokens in expression")
        return self._parse_value(tokens[0])

    def _parse_value(self: Self, token: str) -> Expression:
        stripped = self._strip_quotes(token)
        if stripped is not None:
            return stripped
        if token.replace("-", "", 1).isdigit():
            return int(token)
        return VariableRef(name=token)

    def _split_condition(self: Self, tokens: Sequence[str]) -> tuple[list[str], list[str]]:
        for index, token in enumerate(tokens):
            if token.upper() in {"THEN", "GOTO"}:
                return list(tokens[:index]), list(tokens[index:])
        return list(tokens), []

    def _parse_condition(self: Self, tokens: Sequence[str]) -> tuple[Expression, str, Expression]:
        if len(tokens) < 3:
            raise ScriptParseError("Incomplete condition")
        left = self._parse_value(tokens[0])
        operator = tokens[1]
        right = self._parse_value(tokens[2])
        return left, operator, right

    def _parse_inline(self: Self, tokens: Sequence[str]) -> InlineInstruction:
        if not tokens:
            raise ScriptParseError("Inline command missing")
        keyword = tokens[0].upper()
        if keyword == "SET":
            name = self._expect_string(tokens, 1)
            expression = self._parse_expression(tokens[2:])
            return SetInstruction(name=name, expression=expression)
        if keyword == "ACTION":
            name = self._expect_string(tokens, 1)
            args = tuple(self._parse_value(token) for token in tokens[2:])
            return ActionInstruction(name=name, arguments=args)
        if keyword == "GOTO":
            label_name = self._expect_string(tokens, 1)
            return GotoInstruction(label=label_name)
        raise ScriptParseError(f"Unsupported inline THEN command '{keyword}'")

    def _expect_string(self: Self, tokens: Sequence[str], index: int) -> str:
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
