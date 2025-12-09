import enum
from datetime import datetime

from sqlalchemy import ForeignKey, String, DateTime, func, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.db.session import Base


class UserCoin(Base):
    __tablename__ = "user_coins"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    has_active_alerts: Mapped[bool] = mapped_column(
        nullable=False,
        server_default="false",
    )
    last_used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    user = relationship("User", back_populates="coins")

class Timeframe(str, enum.Enum):
    D1 = "D1"
    H4 = "H4"
    H1 = "H1"

class Candle(Base):
    __tablename__ = "candles"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    timeframe: Mapped[Timeframe] = mapped_column(
        Enum(Timeframe, name="candle_timeframe"),
        nullable=False,
        index=True
    )
    open_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    # prices
    open: Mapped[float] = mapped_column(nullable=False)
    high: Mapped[float] = mapped_column(nullable=False)
    low: Mapped[float] = mapped_column(nullable=False)
    close: Mapped[float] = mapped_column(nullable=False)

    volume: Mapped[float | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    # uniqueness of candle
    __table_args__ = (
        UniqueConstraint("symbol", "timeframe", "open_time"),
    )


