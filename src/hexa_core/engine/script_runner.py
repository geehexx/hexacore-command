"""Hexa-Script runner implementation using a simple bytecode interpreter."""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Mapping, Sequence
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
            pc = self._execute_instruction(instruction, pc, exec_context, labels)

    def _execute_instruction(
        self: Self,
        instruction: Instruction,
        pc: int,
        context: ExecutionContext,
        labels: Mapping[str, int],
    ) -> int:
        match instruction:
            case SetInstruction(name=name, expression=expression):
                context.variables[name] = self._evaluate(expression, context.variables)
                return pc + 1
            case GotoInstruction(label=label):
                return self._jump_to(label, labels)
            case IfGotoInstruction(left=left, operator=op, right=right, label=label):
                return self._execute_if_goto(left, op, right, label, pc, context.variables, labels)
            case IfThenInstruction(left=left, operator=op, right=right, inline_instruction=inline_instr):
                return self._execute_if_then(left, op, right, inline_instr, pc, context, labels)
            case ActionInstruction(name=name, arguments=arguments):
                result = tuple(self._evaluate(arg, context.variables) for arg in arguments)
                context.actions.append((name, result))
                return pc + 1
            case EndInstruction():
                return len(self._program.instructions) if self._program is not None else pc
        msg = f"Unknown instruction '{instruction}'"
        raise ScriptRuntimeError(msg)

    def _execute_if_goto(
        self: Self,
        left: Expression,
        operator: str,
        right: Expression,
        label: str,
        pc: int,
        variables: dict[str, VariableValue],
        labels: Mapping[str, int],
    ) -> int:
        if self._evaluate_condition(left, operator, right, variables):
            return self._jump_to(label, labels)
        return pc + 1

    def _execute_if_then(
        self: Self,
        left: Expression,
        operator: str,
        right: Expression,
        inline_instruction: InlineInstruction,
        pc: int,
        context: ExecutionContext,
        labels: Mapping[str, int],
    ) -> int:
        if self._evaluate_condition(left, operator, right, context.variables):
            return self._execute_inline(inline_instruction, pc, context, labels)
        return pc + 1

    # -- Context helpers -------------------------------------------------

    def _normalize_context(self: Self, context: dict[str, object]) -> ExecutionContext:
        variables = self._coerce_variables(context)
        actions = self._coerce_actions(context)
        return ExecutionContext(variables=variables, actions=actions)

    def _coerce_variables(self: Self, context: dict[str, object]) -> dict[str, VariableValue]:
        variables_obj = context.setdefault("variables", {})
        if not isinstance(variables_obj, dict):
            raise ScriptRuntimeError("Context 'variables' must be a dictionary")
        for key, value in variables_obj.items():
            self._validate_variable_entry(key, value)
        return cast(dict[str, VariableValue], variables_obj)

    @staticmethod
    def _validate_variable_entry(key: object, value: object) -> None:
        if not isinstance(key, str):
            raise ScriptRuntimeError("Variable names must be strings")
        if not isinstance(value, int | str):
            raise ScriptRuntimeError("Variable values must be ints or strings")

    def _coerce_actions(self: Self, context: dict[str, object]) -> list[ActionRecord]:
        actions_obj = context.setdefault("actions", [])
        if not isinstance(actions_obj, list):
            raise ScriptRuntimeError("Context 'actions' must be a list")
        for action in actions_obj:
            self._validate_action_record(action)
        return cast(list[ActionRecord], actions_obj)

    @staticmethod
    def _validate_action_record(action: object) -> None:
        if not (isinstance(action, tuple) and len(action) == 2):
            raise ScriptRuntimeError("Recorded actions must be tuples of name and argument tuple")
        name, args = action
        if not isinstance(name, str) or not isinstance(args, tuple):
            raise ScriptRuntimeError("Action entries must be (name, arguments) tuples")
        for argument in args:
            if not isinstance(argument, int | str):
                raise ScriptRuntimeError("Action arguments must be ints or strings")

    def _execute_inline(
        self: Self,
        instruction: InlineInstruction,
        pc: int,
        context: ExecutionContext,
        labels: Mapping[str, int],
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

    def _jump_to(self: Self, label: str, labels: Mapping[str, int]) -> int:
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
        dispatch: dict[str, Callable[[Sequence[str], dict[str, int]], list[Instruction]]] = {
            "SET": self._compile_set,
            "GOTO": self._compile_goto,
            "IF": self._compile_if,
            "ACTION": self._compile_action,
            "END": self._compile_end,
        }
        handler = dispatch.get(keyword)
        if handler is None:
            raise ScriptParseError(f"Unknown keyword '{keyword}'")
        return handler(arguments, labels)

    def _compile_set(
        self: Self,
        arguments: Sequence[str],
        labels: dict[str, int],
    ) -> list[Instruction]:  # pragma: no cover - direct execution covered via public API
        name = self._expect_string(arguments, 0)
        expression = self._parse_expression(arguments[1:])
        return [SetInstruction(name=name, expression=expression)]

    def _compile_goto(
        self: Self,
        arguments: Sequence[str],
        labels: dict[str, int],
    ) -> list[Instruction]:  # pragma: no cover - direct execution covered via public API
        label_name = self._expect_string(arguments, 0)
        return [GotoInstruction(label=label_name)]

    def _compile_if(
        self: Self,
        arguments: Sequence[str],
        labels: dict[str, int],
    ) -> list[Instruction]:
        condition_tokens, remainder = self._split_condition(arguments)
        left, operator, right = self._parse_condition(condition_tokens)
        if not remainder:
            raise ScriptParseError("IF statement must be followed by THEN or GOTO")
        directive = remainder[0].upper()
        if directive == "THEN":
            return [self._compile_if_then(left, operator, right, remainder[1:], labels)]
        if directive == "GOTO":
            label_name = self._expect_string(remainder, 1)
            return [IfGotoInstruction(left=left, operator=operator, right=right, label=label_name)]
        raise ScriptParseError("IF statement must be followed by THEN or GOTO")

    def _compile_if_then(
        self: Self,
        left: Expression,
        operator: str,
        right: Expression,
        inline_tokens: Sequence[str],
        labels: dict[str, int],
    ) -> IfThenInstruction:
        if inline_tokens and inline_tokens[0].upper() == "GOTO":
            label_name = self._expect_string(inline_tokens, 1)
            return IfThenInstruction(
                left=left,
                operator=operator,
                right=right,
                inline_instruction=GotoInstruction(label=label_name),
            )
        inline_instruction = self._parse_inline(inline_tokens)
        return IfThenInstruction(
            left=left,
            operator=operator,
            right=right,
            inline_instruction=inline_instruction,
        )

    def _compile_action(
        self: Self,
        arguments: Sequence[str],
        labels: dict[str, int],
    ) -> list[Instruction]:  # pragma: no cover - direct execution covered via public API
        name = self._expect_string(arguments, 0)
        action_args = tuple(self._parse_value(arg) for arg in arguments[1:])
        return [ActionInstruction(name=name, arguments=action_args)]

    def _compile_end(
        self: Self,
        arguments: Sequence[str],
        labels: dict[str, int],
    ) -> list[Instruction]:  # pragma: no cover - direct execution covered via public API
        if arguments:
            raise ScriptParseError("END does not take arguments")
        return [EndInstruction()]

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
