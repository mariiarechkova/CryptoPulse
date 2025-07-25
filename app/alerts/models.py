from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from infrastructure.db.session import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)  # Telegram user ID
    symbol = Column(String, nullable=False)  # Example: BTCUSDT
    target_price = Column(Float, nullable=False)
    direction = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())