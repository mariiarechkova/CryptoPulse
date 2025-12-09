import enum
from datetime import datetime

from sqlalchemy import BigInteger, String, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.db.session import Base

class SubscriptionPlan(str, enum.Enum):
    FREE = "free"
    PREMIUM = "premium"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id:Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(10), nullable=False, server_default="ru",)
    is_subscription_active: Mapped[bool] = mapped_column(nullable=False, server_default="false")
    current_plan: Mapped[SubscriptionPlan] = mapped_column(
        Enum(SubscriptionPlan, name="subscription_plan"),
        nullable=False,
        server_default=SubscriptionPlan.FREE.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    coins = relationship("UserCoin", back_populates="user")