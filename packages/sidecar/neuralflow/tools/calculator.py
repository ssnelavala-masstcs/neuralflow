import ast
import operator
from typing import Any

from neuralflow.tools.base import BaseTool

# Allowed operators for safe eval
_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval(expr: str) -> float:
    def _eval(node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.BinOp):
            op = _OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operator: {node.op}")
            return op(_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):
            op = _OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operator: {node.op}")
            return op(_eval(node.operand))
        raise ValueError(f"Unsupported expression: {type(node)}")

    tree = ast.parse(expr, mode="eval")
    return float(_eval(tree.body))


class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Evaluate a mathematical expression and return the result."
    input_schema = {
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "Math expression to evaluate, e.g. '2 + 3 * 4'"},
        },
        "required": ["expression"],
    }

    async def execute(self, input_data: dict[str, Any]) -> Any:
        expr = input_data["expression"]
        result = _safe_eval(expr)
        return {"expression": expr, "result": result}
