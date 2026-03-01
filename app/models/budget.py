from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, UniqueConstraint
from app.database import Base
from sqlalchemy.orm import relationship

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    period = Column(String(10), nullable=False)  # "monthly" or "yearly"
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=True)  # null for yearly

    category = relationship("Category", back_populates="budgets")

    __table_args__ = (
        UniqueConstraint("category_id", "year", "month", name="uq_budget_category_period"),
    )
