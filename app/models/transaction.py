from sqlalchemy import Column, Integer, String, Numeric, Date, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(10), nullable=False)  # "expense" or "income"
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD")
    amount_in_base = Column(Numeric(12, 2), nullable=False)
    description = Column(String(500), nullable=False)
    date = Column(Date, nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    recurring_id = Column(Integer, ForeignKey("recurring_transactions.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    category = relationship("Category", back_populates="transactions")
    recurring = relationship("RecurringTransaction", back_populates="generated_transactions")
