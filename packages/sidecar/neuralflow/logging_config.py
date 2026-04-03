"""Structured JSON logging configuration for NeuralFlow."""

import json
import logging
import re
import sys
from datetime import datetime, timezone
from typing import Any

# Patterns that indicate sensitive data which must never appear in logs
_SENSITIVE_PATTERNS = [
    re.compile(r"(?:api[_-]?key|token|secret|password|authorization)\s*[:=]\s*\S+", re.IGNORECASE),
    re.compile(r"Bearer\s+\S+", re.IGNORECASE),
    re.compile(r"nf_[a-f0-9]+", re.IGNORECASE),
]

# Characters to strip from log messages to prevent log injection
_NEWLINE_RE = re.compile(r"[\r\n]+")


def sanitize(value: str) -> str:
    """Remove newlines and redact sensitive-looking substrings."""
    value = _NEWLINE_RE.sub(" ", value)
    for pattern in _SENSITIVE_PATTERNS:
        value = pattern.sub("***REDACTED***", value)
    return value


class JSONFormatter(logging.Formatter):
    """Emit each log record as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        # Sanitize the message and any exception text
        message = sanitize(record.getMessage())

        log_entry: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": message,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info and record.exc_info[0] is not None:
            # Sanitize traceback lines individually
            tb_lines = self.formatException(record.exc_info).splitlines()
            log_entry["exception"] = [sanitize(line) for line in tb_lines]

        if hasattr(record, "extra"):
            extra = record.extra
            if isinstance(extra, dict):
                for k, v in extra.items():
                    if isinstance(v, str):
                        v = sanitize(v)
                    log_entry[k] = v

        return json.dumps(log_entry, default=str)


def setup_logging(level: str = "INFO") -> None:
    """Configure the root *neuralflow* logger with JSON output.

    Call this once at application startup (before creating the FastAPI app).
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    logger = logging.getLogger("neuralflow")
    logger.setLevel(log_level)
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False

    # Also silence noisy third-party loggers
    for noisy in ("uvicorn.access", "httpx", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the *neuralflow* namespace."""
    return logging.getLogger(f"neuralflow.{name}")


# Convenience loggers used throughout the application
logger = get_logger("app")
auth_logger = get_logger("auth")
workflow_logger = get_logger("workflow")
error_logger = get_logger("error")
