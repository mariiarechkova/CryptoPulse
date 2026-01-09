from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum as SAEnum, Numeric, String, Text, ForeignKey, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.billing.enums import PaymentProvider, PaymentStatus, TariffCode
from infrastructure.db.session import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    provider: Mapped[PaymentProvider] = mapped_column(
        SAEnum(
            PaymentProvider,
            name="payment_provider",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        nullable=False,
        server_default=PaymentProvider.CRYPTOBOT.value,
        index=True,
    )
    invoice_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)

    # paid / pending / expired
    status: Mapped[PaymentStatus] = mapped_column(
        SAEnum(
            PaymentStatus,
            name="payment_status",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        nullable=False,
        server_default=PaymentStatus.PENDING.value,
        index=True,
    )

    # paid_month / paid_year
    tariff_plan_id: Mapped[int] = mapped_column(
        ForeignKey("tariff_plans.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    amount: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    asset: Mapped[str] = mapped_column(String(16), nullable=False, server_default="USDT")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    raw_payload: Mapped[str | None] = mapped_column(Text, nullable=True)

    user = relationship("User", back_populates="payments")
    tariff_plan = relationship("TariffPlan")