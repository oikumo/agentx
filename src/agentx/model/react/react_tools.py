"""Built-in tools for the ReAct agent.

These are simple, dependency-free tools that demonstrate the ReAct pattern
(reason → act → observe) without requiring external services.
"""

from __future__ import annotations

import ast
import operator
from datetime import datetime

from langchain.tools import tool

# ── Safe calculator ────────────────────────────────────────────────────────────

# Whitelist of allowed binary operators for safe evaluation.
_BIN_OPS: dict[type, object] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

# Whitelist of allowed unary operators.
_UNARY_OPS: dict[type, object] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _safe_eval_node(node: ast.AST) -> float | int:
    """Recursively evaluate an AST node using the operator whitelist."""
    if isinstance(node, ast.Expression):
        return _safe_eval_node(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant: {type(node.value).__name__}")
    if isinstance(node, ast.BinOp):
        op_func = _BIN_OPS.get(type(node.op))
        if op_func is None:
            raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
        left = _safe_eval_node(node.left)
        right = _safe_eval_node(node.right)
        return op_func(left, right)  # type: ignore[operator]
    if isinstance(node, ast.UnaryOp):
        op_func = _UNARY_OPS.get(type(node.op))
        if op_func is None:
            raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
        operand = _safe_eval_node(node.operand)
        return op_func(operand)  # type: ignore[operator]
    raise ValueError(f"Unsupported expression node: {type(node).__name__}")


def safe_calculate(expression: str) -> str:
    """Safely evaluate a math expression.

    Uses ``ast.literal_eval``-style parsing with a whitelist of allowed
    operators (+, -, *, /, //, %, **).  No function calls, attribute
    access, or name lookups are permitted.

    Args:
        expression: A math expression string (e.g. ``"2+2"``, ``"240*0.15"``).

    Returns:
        The result as a string, or an error message if the expression is
        invalid or unsafe.
    """
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval_node(tree)
        # Convert to int if the result is a whole number
        if isinstance(result, float) and result.is_integer():
            return str(int(result))
        return str(result)
    except (ValueError, SyntaxError) as exc:
        return f"Error: {exc}"
    except Exception as exc:  # pragma: no cover
        return f"Error: invalid expression"


@tool
def calculator(expression: str) -> str:
    """Evaluate a math expression and return the result.

    Supports addition (+), subtraction (-), multiplication (*),
    division (/), floor division (//), modulo (%), and power (**).

    Args:
        expression: A math expression (e.g. "2+2", "15*240/100", "2**10").

    Returns:
        The calculated result as a string.
    """
    return safe_calculate(expression)


# ── Get current time ───────────────────────────────────────────────────────────


@tool
def get_current_time() -> str:
    """Get the current date and time.

    Returns:
        The current date and time in ISO 8601 format.
    """
    return datetime.now().isoformat()
