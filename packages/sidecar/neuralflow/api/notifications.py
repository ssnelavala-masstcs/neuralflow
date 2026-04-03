"""Notifications API endpoints."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from neuralflow.services.notifier import notifier

router = APIRouter(prefix="/api/notifications")


@router.get("")
async def get_notifications(
    unread_only: bool = Query(False),
) -> dict[str, Any]:
    """Get all notifications."""
    return {
        "notifications": notifier.get_all(unread_only=unread_only),
        "unread_count": notifier.unread_count,
    }


@router.post("/{notification_id}/read")
async def mark_notification_read(notification_id: str) -> dict[str, Any]:
    """Mark a notification as read."""
    notifier.mark_read(notification_id)
    return {"message": "Notification marked as read"}


@router.post("/read-all")
async def mark_all_read() -> dict[str, Any]:
    """Mark all notifications as read."""
    notifier.mark_all_read()
    return {"message": "All notifications marked as read"}


@router.delete("")
async def clear_notifications() -> dict[str, Any]:
    """Clear all notifications."""
    notifier.clear()
    return {"message": "Notifications cleared"}
