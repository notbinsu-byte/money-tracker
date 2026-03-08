from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date
from decimal import Decimal
from app.models.transaction import Transaction
from app.models.category import Category

# Coalesce NULL currency to "USD" for consistent grouping
_tx_currency = func.coalesce(Transaction.currency, "USD")

def get_monthly_totals(db: Session, year: int, month: int) -> dict:
    """Get total income and expenses for a given month, grouped by currency."""
    results = (
        db.query(_tx_currency, Transaction.type, func.sum(Transaction.amount))
        .filter(extract("year", Transaction.date) == year)
        .filter(extract("month", Transaction.date) == month)
        .group_by(_tx_currency, Transaction.type)
        .all()
    )
    totals = {}
    for currency, t_type, total in results:
        cur = currency
        if cur not in totals:
            totals[cur] = {"income": Decimal("0"), "expense": Decimal("0")}
        totals[cur][t_type] = total or Decimal("0")
    for cur in totals:
        totals[cur]["net"] = totals[cur]["income"] - totals[cur]["expense"]
    return totals

def get_category_breakdown(db: Session, year: int, month: int, type: str = "expense") -> list[dict]:
    """Get spending/income breakdown by category for a month, grouped by currency."""
    results = (
        db.query(
            Category.id,
            Category.name,
            Category.icon,
            Category.color,
            _tx_currency.label("currency"),
            func.sum(Transaction.amount).label("total"),
        )
        .join(Transaction, Transaction.category_id == Category.id)
        .filter(Transaction.type == type)
        .filter(extract("year", Transaction.date) == year)
        .filter(extract("month", Transaction.date) == month)
        .group_by(Category.id, _tx_currency)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )
    return [
        {
            "category_id": r.id,
            "category_name": r.name,
            "category_icon": r.icon,
            "category_color": r.color,
            "currency": r.currency,
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
