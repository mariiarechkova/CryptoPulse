from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        server_default="ru",
    )
    paid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    tariff_plan_id: Mapped[int] = mapped_column(
        ForeignKey("tariff_plans.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    levels_demo_remaining: Mapped[int] = mapped_column(Integer, nullable=False, server_default="3")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    coins = relationship("UserCoin", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    tariff_plan = relationship("TariffPlan")
