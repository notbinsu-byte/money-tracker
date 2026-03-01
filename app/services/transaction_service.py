from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date
from decimal import Decimal
from app.models.transaction import Transaction
from app.models.category import Category

def get_monthly_totals(db: Session, year: int, month: int) -> dict:
    """Get total income and expenses for a given month."""
    results = (
        db.query(Transaction.type, func.sum(Transaction.amount_in_base))
        .filter(extract("year", Transaction.date) == year)
        .filter(extract("month", Transaction.date) == month)
        .group_by(Transaction.type)
        .all()
    )
    totals = {"income": Decimal("0"), "expense": Decimal("0")}
    for t_type, total in results:
        totals[t_type] = total or Decimal("0")
    totals["net"] = totals["income"] - totals["expense"]
    return totals

def get_category_breakdown(db: Session, year: int, month: int, type: str = "expense") -> list[dict]:
    """Get spending/income breakdown by category for a month."""
    results = (
        db.query(
            Category.id,
            Category.name,
            Category.icon,
            Category.color,
            func.sum(Transaction.amount_in_base).label("total"),
        )
        .join(Transaction, Transaction.category_id == Category.id)
        .filter(Transaction.type == type)
        .filter(extract("year", Transaction.date) == year)
        .filter(extract("month", Transaction.date) == month)
        .group_by(Category.id)
        .order_by(func.sum(Transaction.amount_in_base).desc())
        .all()
    )
    return [
        {
            "category_id": r.id,
            "category_name": r.name,
            "category_icon": r.icon,
            "category_color": r.color,
            "total": r.total,
        }
        for r in results
    ]

def get_recent_transactions(db: Session, limit: int = 5) -> list[Transaction]:
    """Get the most recent transactions."""
    return (
        db.query(Transaction)
        .order_by(Transaction.date.desc(), Transaction.created_at.desc())
        .limit(limit)
        .all()
    )
