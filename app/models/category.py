from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    type = Column(String(10), nullable=False)  # "expense" or "income"
    icon = Column(String(50), default="📁")
    color = Column(String(7), default="#6c757d")
    is_default = Column(Boolean, default=False)

    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category")
    recurring_transactions = relationship("RecurringTransaction", back_populates="category")
