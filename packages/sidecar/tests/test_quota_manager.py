"""Tests for quota manager service."""
import pytest
from neuralflow.services.quota_manager import (
    QuotaConfig,
    UsageTracker,
    check_and_record_cost,
    get_quota,
    set_quota,
    get_usage,
)


def test_quota_config_defaults():
    config = QuotaConfig()
    assert config.monthly_budget_usd == 0.0
    assert config.hard_stop_at_budget is True
    assert config.alert_threshold_pct == 80.0


def test_quota_config_to_dict():
    config = QuotaConfig(monthly_budget_usd=100.0)
    d = config.to_dict()
    assert d["monthly_budget_usd"] == 100.0


def test_quota_config_from_dict():
    config = QuotaConfig.from_dict({"monthly_budget_usd": 50.0, "hard_stop_at_budget": False})
    assert config.monthly_budget_usd == 50.0
    assert config.hard_stop_at_budget is False


def test_usage_tracker_initial():
    tracker = UsageTracker()
    assert tracker.monthly_spent_usd == 0.0
    assert tracker.current_run_spent_usd == 0.0


def test_usage_tracker_record_cost():
    tracker = UsageTracker()
    tracker.record_cost(0.05, "openai")
    assert tracker.monthly_spent_usd == 0.05
    assert tracker.current_run_spent_usd == 0.05
    assert len(tracker.provider_call_counts.get("openai", [])) == 1


def test_usage_tracker_reset_run():
    tracker = UsageTracker()
    tracker.record_cost(0.10)
    tracker.reset_run()
    assert tracker.current_run_spent_usd == 0.0
    assert tracker.monthly_spent_usd == 0.10  # Monthly stays


def test_budget_check_under_budget():
    config = QuotaConfig(monthly_budget_usd=100.0)
    tracker = UsageTracker()
    tracker.monthly_spent_usd = 50.0
    allowed, message = tracker.check_budget(config)
    assert allowed is True
    assert message is None


def test_budget_check_over_budget_soft_stop():
    config = QuotaConfig(monthly_budget_usd=100.0, hard_stop_at_budget=False)
    tracker = UsageTracker()
    tracker.monthly_spent_usd = 150.0
    allowed, message = tracker.check_budget(config)
    assert allowed is True
    assert message is not None


def test_budget_check_over_budget_hard_stop():
    config = QuotaConfig(monthly_budget_usd=100.0, hard_stop_at_budget=True)
    tracker = UsageTracker()
    tracker.monthly_spent_usd = 150.0
    allowed, message = tracker.check_budget(config)
    assert allowed is False
    assert message is not None


def test_budget_check_alert_threshold():
    config = QuotaConfig(monthly_budget_usd=100.0, alert_threshold_pct=80.0)
    tracker = UsageTracker()
    tracker.monthly_spent_usd = 85.0
    allowed, message = tracker.check_budget(config)
    assert allowed is True
    assert message is not None
    assert "85%" in message or "Alert" in message


def test_check_and_record_cost_allowed():
    set_quota(QuotaConfig(monthly_budget_usd=1000.0))
    allowed, message = check_and_record_cost(0.50, "openai")
    assert allowed is True
    assert get_usage().monthly_spent_usd >= 0.50
