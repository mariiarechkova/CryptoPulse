from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.billing.enums import TariffCode
from infrastructure.db.session import Base


class TariffPlan(Base):
    __tablename__ = "tariff_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)

    # price is in USDT
    price_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    price_currency: Mapped[str] = mapped_column(String(10), nullable=False, default="USDT")

    duration_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # main monetization lever: how many symbols can be tracked at the same time
    max_symbols: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    demo_levels_requests_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    llm_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    @staticmethod
    def default_free() -> dict:
        return {
            "code": TariffCode.FREE.value,
            "title": "Free",
            "price_amount": 0,
            "price_currency": "USDT",
            "duration_days": 0,
            "max_symbols": 1,
            "demo_levels_requests_total": 3,
            "llm_enabled": True,
            "is_active": True,
        }

    @staticmethod
    def default_paid_month() -> dict:
        return {
            "code": TariffCode.PAID_MONTH.value,
            "title": "Full access (30 days)",
            "price_amount": 10,
            "price_currency": "USDT",
            "duration_days": 30,
            "max_symbols": 10,
            "demo_levels_requests_total": 999999,
            "llm_enabled": True,
            "is_active": True,
        }
