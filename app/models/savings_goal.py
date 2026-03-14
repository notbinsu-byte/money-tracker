from sqlalchemy import Column, Integer, String, Numeric, Date, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class SavingsGoal(Base):
    __tablename__ = "savings_goals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    target_amount = Column(Numeric(12, 2), nullable=False)
    current_amount = Column(Numeric(12, 2), default=0, server_default="0")
    currency = Column(String(3), default="USD", server_default="USD")
    deadline = Column(Date, nullable=True)
    icon = Column(String(50), default="🎯", server_default="🎯")
    color = Column(String(7), default="#2ecc71", server_default="#2ecc71")
    notes = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False, server_default="0")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
