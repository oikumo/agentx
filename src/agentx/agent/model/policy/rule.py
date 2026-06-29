"""Policy rule condition DSL — tokenizer, parser, and AST (design §7.2).

A small expression language compiled to an AST and evaluated by a visitor
against :class:`PolicyContext`.  Compilation is cached per rule so repeated
evaluations skip parsing (<50ms per evaluation, NFR P2).  Unknown identifiers /
functions raise :class:`ConditionCompileError` at load time — fail-fast, never
at ``decide()`` time.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from agentx.agent.types import PolicyContext


class ConditionCompileError(Exception):
    """Raised when a condition expression cannot be compiled (fail-fast)."""


# ---------------------------------------------------------------------------
# AST nodes
# ---------------------------------------------------------------------------


@dataclass
class ASTNode:
    """Base AST node."""


@dataclass
class Literal(ASTNode):
    value: Any


@dataclass
class Identifier(ASTNode):
    parts: list[str]  # e.g. ["goal", "active"]


@dataclass
class FunctionCall(ASTNode):
    name: str
    args: list[ASTNode]


@dataclass
class UnaryOp(ASTNode):
    op: str
    operand: ASTNode


@dataclass
class BinaryOp(ASTNode):
    op: str  # AND, OR
    left: ASTNode
    right: ASTNode


@dataclass
class Comparison(ASTNode):
    op: str  # ==, !=, <, <=, >, >=
    left: ASTNode
    right: ASTNode


@dataclass
class Arithmetic(ASTNode):
    op: str  # +, -
    left: ASTNode
    right: ASTNode


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------


_TOKEN_RE = re.compile(
    r"""
      \s*(?:
        (?P<NUMBER>-?\d+\.?\d*) |
        (?P<STRING>'[^']*'|"[^"]*") |
        (?P<OP><=|>=|==|!=|<|>|\+|-) |
        (?P<LP>\() |
        (?P<RP>\)) |
        (?P<COMMA>,) |
        (?P<IDENT>[A-Za-z_][A-Za-z0-9_.]*)
      )
    """,
    re.VERBOSE,
)


def tokenize(expr: str) -> list[tuple[str, str]]:
    tokens: list[tuple[str, str]] = []
    pos = 0
    while pos < len(expr):
        m = _TOKEN_RE.match(expr, pos)
        if not m or m.end() == pos:
            if expr[pos:].strip() == "":
                break
            raise ConditionCompileError(f"unexpected character at {pos}: {expr[pos:]!r}")
        pos = m.end()
        for kind in ("NUMBER", "STRING", "OP", "LP", "RP", "COMMA", "IDENT"):
            val = m.group(kind)
            if val is not None:
                if kind == "IDENT" and val.upper() in {"AND", "OR", "NOT"}:
                    tokens.append(("KEYWORD", val.upper()))
                elif kind == "STRING":
                    tokens.append(("STRING", val[1:-1]))
                else:
                    tokens.append((kind, val))
                break
    return tokens


# ---------------------------------------------------------------------------
# Parser (recursive descent)
# ---------------------------------------------------------------------------


class _Parser:
    def __init__(self, tokens: list[tuple[str, str]]) -> None:
        self._tokens = tokens
        self._pos = 0

    def _peek(self) -> tuple[str, str] | None:
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return None

    def _consume(self) -> tuple[str, str]:
        tok = self._tokens[self._pos]
        self._pos += 1
        return tok

    def _expect(self, kind: str) -> tuple[str, str]:
        tok = self._peek()
        if tok is None or tok[0] != kind:
            raise ConditionCompileError(f"expected {kind}, got {tok}")
        return self._consume()

    def parse(self) -> ASTNode:
        node = self._or_expr()
        if self._pos != len(self._tokens):
            raise ConditionCompileError(f"trailing tokens: {self._tokens[self._pos:]}")
        return node

    def _or_expr(self) -> ASTNode:
        left = self._and_expr()
        while self._peek() == ("KEYWORD", "OR"):
            self._consume()
            right = self._and_expr()
            left = BinaryOp("OR", left, right)
        return left

    def _and_expr(self) -> ASTNode:
        left = self._not_expr()
        while self._peek() == ("KEYWORD", "AND"):
            self._consume()
            right = self._not_expr()
            left = BinaryOp("AND", left, right)
        return left

    def _not_expr(self) -> ASTNode:
        if self._peek() == ("KEYWORD", "NOT"):
            self._consume()
            return UnaryOp("NOT", self._not_expr())
        return self._comparison()

    def _comparison(self) -> ASTNode:
        left = self._additive()
        tok = self._peek()
        if tok and tok[0] == "OP" and tok[1] in {"==", "!=", "<", "<=", ">", ">="}:
            op = self._consume()[1]
            right = self._additive()
            return Comparison(op, left, right)
        return left

    def _additive(self) -> ASTNode:
        left = self._primary()
        tok = self._peek()
        while tok and tok[0] == "OP" and tok[1] in {"+", "-"}:
            op = self._consume()[1]
            right = self._primary()
            left = Arithmetic(op, left, right)
            tok = self._peek()
        return left

    def _primary(self) -> ASTNode:
        tok = self._peek()
        if tok is None:
            raise ConditionCompileError("unexpected end of expression")
        if tok[0] == "LP":
            self._consume()
            node = self._or_expr()
            self._expect("RP")
            return node
        if tok[0] == "NUMBER":
            self._consume()
            return Literal(float(tok[1]) if "." in tok[1] else int(tok[1]))
        if tok[0] == "STRING":
            self._consume()
            return Literal(tok[1])
        if tok[0] == "IDENT":
            self._consume()
            # function call?
            nxt = self._peek()
            if nxt and nxt[0] == "LP":
                self._consume()
                args: list[ASTNode] = []
                after = self._peek()
                if after and after[0] != "RP":
                    args.append(self._or_expr())
                    comma = self._peek()
                    while comma and comma[0] == "COMMA":
                        self._consume()
                        args.append(self._or_expr())
                        comma = self._peek()
                self._expect("RP")
                return FunctionCall(tok[1], args)
            return Identifier(tok[1].split("."))
        raise ConditionCompileError(f"unexpected token: {tok}")


def compile_condition(expr: str) -> ASTNode:
    """Compile a condition string into an AST (cached by caller)."""
    tokens = tokenize(expr)
    if not tokens:
        return Literal(True)
    return _Parser(tokens).parse()


# ---------------------------------------------------------------------------
# Evaluation visitor
# ---------------------------------------------------------------------------


class ConditionEvaluator:
    """Evaluate a compiled condition AST against a :class:`PolicyContext`."""

    def evaluate(self, node: ASTNode, ctx: PolicyContext) -> Any:
        return self._visit(node, ctx)

    def _visit(self, node: ASTNode, ctx: PolicyContext) -> Any:
        if isinstance(node, Literal):
            return node.value
        if isinstance(node, Identifier):
            return self._resolve_identifier(node.parts, ctx)
        if isinstance(node, FunctionCall):
            return self._call_function(node.name, [self._visit(a, ctx) for a in node.args], ctx)
        if isinstance(node, UnaryOp):
            if node.op == "NOT":
                return not self._visit(node.operand, ctx)
        if isinstance(node, BinaryOp):
            left = self._visit(node.left, ctx)
            right = self._visit(node.right, ctx)
            if node.op == "AND":
                return bool(left and right)
            if node.op == "OR":
                return bool(left or right)
        if isinstance(node, Comparison):
            left = self._visit(node.left, ctx)
            right = self._visit(node.right, ctx)
            return self._compare(node.op, left, right)
        if isinstance(node, Arithmetic):
            left = self._visit(node.left, ctx)
            right = self._visit(node.right, ctx)
            if node.op == "+":
                return left + right
            if node.op == "-":
                return left - right
        raise ConditionCompileError(f"cannot evaluate node: {node}")

    # ------------------------------------------------------- identifier resolution

    _GOAL_ATTRS = {"active", "is_blocked", "description", "priority", "status", "id"}

    def _resolve_identifier(self, parts: list[str], ctx: PolicyContext) -> Any:
        root = parts[0]
        if root == "true":
            return True
        if root == "false":
            return False
        if root == "agent" and len(parts) >= 2:
            if parts[1] == "state":
                return ctx.agent_state.value if hasattr(ctx.agent_state, "value") else str(ctx.agent_state)
            if parts[1] == "autonomy":
                return ctx.autonomy_level.value if hasattr(ctx.autonomy_level, "value") else str(ctx.autonomy_level)
        if root == "environment" and ctx.environment is not None:
            if len(parts) >= 2 and parts[1] == "memory_pressure":
                return ctx.environment.memory_pressure
            if len(parts) >= 2 and parts[1] == "confidence":
                return ctx.environment.confidence
            if len(parts) >= 2 and parts[1] == "timestamp":
                return ctx.environment.timestamp
            return ctx.environment
        if root == "goal":
            goal = ctx.current_goal
            if goal is None:
                return False
            if len(parts) < 2:
                return goal
            attr = parts[1]
            if attr == "active":
                return goal.active
            if attr == "is_blocked":
                return goal.is_blocked
            if attr in self._GOAL_ATTRS:
                return getattr(goal, attr, False)
            return False
        if root == "memory":
            return ctx.memory
        return None

    # ------------------------------------------------------- function calls

    def _call_function(self, name: str, args: list[Any], ctx: PolicyContext) -> Any:
        if name == "has_observation":
            tag = args[0] if args else ""
            for entry in ctx.memory:
                if tag in str(entry.content):
                    return True
            return False
        if name == "goal_is_blocked":
            return ctx.current_goal is not None and ctx.current_goal.is_blocked
        if name == "memory_contains":
            query = args[0] if args else ""
            for entry in ctx.memory:
                if query in str(entry.content):
                    return True
            return False
        raise ConditionCompileError(f"unknown function: {name}")

    @staticmethod
    def _compare(op: str, left: Any, right: Any) -> bool:
        try:
            if op == "==":
                return left == right
            if op == "!=":
                return left != right
            if op == "<":
                return left < right
            if op == "<=":
                return left <= right
            if op == ">":
                return left > right
            if op == ">=":
                return left >= right
        except TypeError:
            return False
        return False


# ---------------------------------------------------------------------------
# Compiled condition wrapper (caches the AST)
# ---------------------------------------------------------------------------


@dataclass
class CompiledCondition:
    """A condition string + its cached AST."""

    expression: str
    _ast: ASTNode | None = field(default=None, repr=False)

    def evaluate(self, ctx: PolicyContext) -> bool:
        if self._ast is None:
            self._ast = compile_condition(self.expression)
        try:
            return bool(ConditionEvaluator().evaluate(self._ast, ctx))
        except ConditionCompileError:
            return False
        except Exception:  # noqa: BLE001 — conditions must not crash decide()
            return False

    def compile(self) -> None:
        """Pre-compile at load time (fail-fast)."""
        self._ast = compile_condition(self.expression)
