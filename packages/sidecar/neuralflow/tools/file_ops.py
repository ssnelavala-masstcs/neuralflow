import os
from pathlib import Path
from typing import Any

from neuralflow.tools.base import BaseTool

# Sandboxed to user home / neuralflow workspace
_ALLOWED_BASE = Path.home() / "neuralflow-files"


def _safe_path(path_str: str) -> Path:
    _ALLOWED_BASE.mkdir(parents=True, exist_ok=True)
    p = (_ALLOWED_BASE / path_str).resolve()
    if not str(p).startswith(str(_ALLOWED_BASE.resolve())):
        raise PermissionError(f"Access outside sandbox denied: {path_str}")
    return p


class FileReadTool(BaseTool):
    name = "file_read"
    description = "Read the contents of a file from the NeuralFlow sandbox directory."
    input_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Relative path within the sandbox"},
        },
        "required": ["path"],
    }

    async def execute(self, input_data: dict[str, Any]) -> Any:
        p = _safe_path(input_data["path"])
        if not p.exists():
            raise FileNotFoundError(f"File not found: {input_data['path']}")
        return {"content": p.read_text(encoding="utf-8"), "path": str(p)}


class FileWriteTool(BaseTool):
    name = "file_write"
    description = "Write content to a file in the NeuralFlow sandbox directory."
    input_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Relative path within the sandbox"},
            "content": {"type": "string", "description": "Text content to write"},
            "append": {"type": "boolean", "description": "Append instead of overwrite", "default": False},
        },
        "required": ["path", "content"],
    }

    async def execute(self, input_data: dict[str, Any]) -> Any:
        p = _safe_path(input_data["path"])
        p.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if input_data.get("append") else "w"
        p.write_text(input_data["content"], encoding="utf-8") if mode == "w" else open(p, "a").write(input_data["content"])
        return {"ok": True, "path": str(p), "bytes_written": len(input_data["content"])}


class FileListTool(BaseTool):
    name = "file_list"
    description = "List files in the NeuralFlow sandbox directory."
    input_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Relative path to list (default: root)", "default": "."},
        },
    }

    async def execute(self, input_data: dict[str, Any]) -> Any:
        p = _safe_path(input_data.get("path", "."))
        if not p.is_dir():
            raise NotADirectoryError(f"Not a directory: {input_data.get('path')}")
        entries = [
            {"name": entry.name, "type": "dir" if entry.is_dir() else "file", "size": entry.stat().st_size if entry.is_file() else None}
            for entry in sorted(p.iterdir())
        ]
        return {"entries": entries, "path": str(p)}
