"""Tests for notification service."""
import pytest
from neuralflow.services.notifier import NotificationService, Notification


def test_notify_creates_entry():
    service = NotificationService()
    notif = service.notify("test", "Test Title", "Test message")
    assert notif.type == "test"
    assert notif.title == "Test Title"
    assert notif.message == "Test message"
    assert notif.severity == "info"
    assert not notif.read


def test_get_all():
    service = NotificationService()
    service.notify("type1", "Title 1", "Message 1")
    service.notify("type2", "Title 2", "Message 2")
    all_notifs = service.get_all()
    assert len(all_notifs) == 2


def test_unread_count():
    service = NotificationService()
    service.notify("type1", "Title 1", "Message 1")
    service.notify("type2", "Title 2", "Message 2")
    assert service.unread_count == 2


def test_mark_read():
    service = NotificationService()
    notif = service.notify("type1", "Title 1", "Message 1")
    assert service.unread_count == 1  # Check before marking read
    service.mark_read(notif.id)
    assert service.unread_count == 0


def test_mark_all_read():
    service = NotificationService()
    service.notify("type1", "Title 1", "Message 1")
    service.notify("type2", "Title 2", "Message 2")
    service.mark_all_read()
    assert service.unread_count == 0


def test_clear():
    service = NotificationService()
    service.notify("type1", "Title 1", "Message 1")
    service.clear()
    assert len(service.get_all()) == 0


def test_listener_callback():
    service = NotificationService()
    received = []
    service.add_listener(lambda n: received.append(n))
    service.notify("test", "Title", "Message")
    assert len(received) == 1
    assert received[0].title == "Title"


def test_max_history():
    service = NotificationService()
    service._max_history = 5
    for i in range(10):
        service.notify("type", f"Title {i}", f"Message {i}")
    assert len(service._notifications) <= 5


def test_notification_to_dict():
    notif = Notification(id="test-1", type="error", title="Error", message="Something broke")
    d = notif.to_dict()
    assert d["id"] == "test-1"
    assert d["type"] == "error"
    assert d["title"] == "Error"
    assert d["read"] is False
