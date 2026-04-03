"""Quota management — budget limits, rate limiting per provider, and spend alerts."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("neuralflow.quota_manager")


@dataclass
class QuotaConfig:
    """Budget and rate quota configuration."""

    monthly_budget_usd: float = 0.0  # 0 = unlimited
    daily_budget_usd: float = 0.0
    per_run_budget_usd: float = 0.0
    alert_threshold_pct: float = 80.0  # Alert at 80% of budget
    hard_stop_at_budget: bool = True
    provider_rate_limits: dict[str, int] = field(default_factory=dict)  # provider -> max calls/min

    def to_dict(self) -> dict[str, Any]:
        return {
            "monthly_budget_usd": self.monthly_budget_usd,
            "daily_budget_usd": self.daily_budget_usd,
            "per_run_budget_usd": self.per_run_budget_usd,
            "alert_threshold_pct": self.alert_threshold_pct,
            "hard_stop_at_budget": self.hard_stop_at_budget,
            "provider_rate_limits": self.provider_rate_limits,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QuotaConfig":
        return cls(
            monthly_budget_usd=data.get("monthly_budget_usd", 0.0),
            daily_budget_usd=data.get("daily_budget_usd", 0.0),
            per_run_budget_usd=data.get("per_run_budget_usd", 0.0),
            alert_threshold_pct=data.get("alert_threshold_pct", 80.0),
            hard_stop_at_budget=data.get("hard_stop_at_budget", True),
            provider_rate_limits=data.get("provider_rate_limits", {}),
        )


@dataclass
class UsageTracker:
    """Tracks current period usage against quotas."""

    monthly_spent_usd: float = 0.0
    daily_spent_usd: float = 0.0
    current_run_spent_usd: float = 0.0
    provider_call_counts: dict[str, list[float]] = field(default_factory=dict)  # provider -> [timestamps]

    def check_budget(self, quota: QuotaConfig) -> tuple[bool, str | None]:
        """Check if budget limits are exceeded. Returns (allowed, alert_message)."""
        if quota.monthly_budget_usd > 0 and self.monthly_spent_usd >= quota.monthly_budget_usd:
            if quota.hard_stop_at_budget:
                return False, "Monthly budget exceeded. Hard stop enforced."
            return True, f"Warning: Monthly budget {quota.alert_threshold_pct}% exceeded."

        if quota.daily_budget_usd > 0 and self.daily_spent_usd >= quota.daily_budget_usd:
            if quota.hard_stop_at_budget:
                return False, "Daily budget exceeded. Hard stop enforced."
            return True, f"Warning: Daily budget {quota.alert_threshold_pct}% exceeded."

        # Check alert thresholds
        if quota.monthly_budget_usd > 0:
            pct = (self.monthly_spent_usd / quota.monthly_budget_usd) * 100
            if pct >= quota.alert_threshold_pct:
                return True, f"Alert: {pct:.0f}% of monthly budget used (${self.monthly_spent_usd:.2f}/${quota.monthly_budget_usd:.2f})"

        return True, None

    def record_cost(self, cost_usd: float, provider: str | None = None) -> None:
        """Record a cost entry."""
        self.monthly_spent_usd += cost_usd
        self.daily_spent_usd += cost_usd
        self.current_run_spent_usd += cost_usd
        if provider:
            if provider not in self.provider_call_counts:
                self.provider_call_counts[provider] = []
            self.provider_call_counts[provider].append(datetime.now(timezone.utc).timestamp())

    def reset_run(self) -> None:
        self.current_run_spent_usd = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "monthly_spent_usd": round(self.monthly_spent_usd, 6),
            "daily_spent_usd": round(self.daily_spent_usd, 6),
            "current_run_spent_usd": round(self.current_run_spent_usd, 6),
            "provider_call_counts": {
                k: len(v) for k, v in self.provider_call_counts.items()
            },
        }


# Global singleton
_quota = QuotaConfig()
_usage = UsageTracker()


def get_quota() -> QuotaConfig:
    return _quota


def set_quota(config: QuotaConfig) -> None:
    global _quota
    _quota = config


def get_usage() -> UsageTracker:
    return _usage


def check_and_record_cost(cost_usd: float, provider: str | None = None) -> tuple[bool, str | None]:
    """Check budget before recording cost. Returns (allowed, message)."""
    allowed, message = _usage.check_budget(_quota)
    if allowed:
        _usage.record_cost(cost_usd, provider)
    return allowed, message
