"""Notification service — in-app, desktop, and webhook notifications."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable

logger = logging.getLogger("neuralflow.notifier")


@dataclass
class Notification:
    id: str
    type: str  # run_completed, run_failed, hitl_waiting, cost_threshold, error, schedule_triggered
    title: str
    message: str
    severity: str = "info"  # info, warning, critical
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    read: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "message": self.message,
            "severity": self.severity,
            "data": self.data,
            "timestamp": self.timestamp,
            "read": self.read,
        }


class NotificationService:
    """Centralized notification service with multiple delivery channels."""

    def __init__(self) -> None:
        self._notifications: list[Notification] = []
        self._listeners: list[Callable[[Notification], None]] = []
        self._webhook_urls: list[str] = []
        self._max_history = 200

    def add_listener(self, callback: Callable[[Notification], None]) -> Callable[[], None]:
        """Register a listener. Returns an unsubscribe function."""
        self._listeners.append(callback)
        return lambda: self._listeners.remove(callback)

    def add_webhook(self, url: str) -> None:
        self._webhook_urls.append(url)

    def notify(
        self,
        type: str,
        title: str,
        message: str,
        severity: str = "info",
        data: dict[str, Any] | None = None,
    ) -> Notification:
        """Create and dispatch a notification."""
        import uuid
        notif = Notification(
            id=str(uuid.uuid4()),
            type=type,
            title=title,
            message=message,
            severity=severity,
            data=data or {},
        )
        self._notifications.append(notif)
        if len(self._notifications) > self._max_history:
            self._notifications = self._notifications[-self._max_history:]

        # Dispatch to listeners
        for listener in self._listeners:
            try:
                listener(notif)
            except Exception:
                logger.exception("Error dispatching notification to listener")

        logger.info("[%s] %s: %s", notif.type, notif.title, notif.message)
        return notif

    def get_all(self, unread_only: bool = False) -> list[dict[str, Any]]:
        notifs = self._notifications if not unread_only else [n for n in self._notifications if not n.read]
        return [n.to_dict() for n in reversed(notifs)]

    def mark_read(self, notification_id: str) -> None:
        for n in self._notifications:
            if n.id == notification_id:
                n.read = True
                break

    def mark_all_read(self) -> None:
        for n in self._notifications:
            n.read = True

    def clear(self) -> None:
        self._notifications.clear()

    @property
    def unread_count(self) -> int:
        return sum(1 for n in self._notifications if not n.read)


# Global singleton
notifier = NotificationService()
