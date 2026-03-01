from sqlalchemy import Column, Integer, String, Numeric, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class RecurringTransaction(Base):
    __tablename__ = "recurring_transactions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(10), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD")
    description = Column(String(500), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    frequency = Column(String(10), nullable=False)  # daily, weekly, monthly, yearly
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    last_generated = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)

    category = relationship("Category", back_populates="recurring_transactions")
    generated_transactions = relationship("Transaction", back_populates="recurring")
