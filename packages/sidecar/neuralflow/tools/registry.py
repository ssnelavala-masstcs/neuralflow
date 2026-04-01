"""Global tool registry — all built-in tools registered here."""
from neuralflow.tools.base import BaseTool
from neuralflow.tools.calculator import CalculatorTool
from neuralflow.tools.file_ops import FileListTool, FileReadTool, FileWriteTool
from neuralflow.tools.http_request import HttpRequestTool
from neuralflow.tools.web_search import WebSearchTool

_REGISTRY: dict[str, BaseTool] = {}


def _register(*tools: BaseTool) -> None:
    for t in tools:
        _REGISTRY[t.name] = t


_register(
    WebSearchTool(),
    FileReadTool(),
    FileWriteTool(),
    FileListTool(),
    HttpRequestTool(),
    CalculatorTool(),
)


def get_tool(name: str) -> BaseTool | None:
    return _REGISTRY.get(name)


def list_tools() -> list[dict]:
    return [
        {
            "name": t.name,
            "description": t.description,
            "input_schema": t.input_schema,
        }
        for t in _REGISTRY.values()
    ]
