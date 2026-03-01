from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.sql import func
from app.database import Base

class CurrencyRate(Base):
    __tablename__ = "currency_rates"

    id = Column(Integer, primary_key=True, index=True)
    base_currency = Column(String(3), nullable=False)
    target_currency = Column(String(3), nullable=False)
    rate = Column(Numeric(16, 8), nullable=False)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
