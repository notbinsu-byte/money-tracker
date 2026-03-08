from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case
from decimal import Decimal
from app.models.budget import Budget
from app.models.transaction import Transaction
from app.models.category import Category

# Coalesce NULL currency to "USD" for consistent grouping/filtering
_tx_currency = func.coalesce(Transaction.currency, "USD")

def get_budget_summary(db: Session, year: int, month: int) -> list[dict]:
    """Get all budgets with their spending status for a given period."""
    budgets = (
        db.query(Budget)
        .filter(
            ((Budget.period == "monthly") & (Budget.year == year) & (Budget.month == month))
            | ((Budget.period == "yearly") & (Budget.year == year))
        )
        .all()
    )

    summaries = []
    for budget in budgets:
        budget_currency = budget.currency or "USD"
        query = (
            db.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(Transaction.category_id == budget.category_id)
            .filter(Transaction.type == "expense")
            .filter(_tx_currency == budget_currency)
            .filter(extract("year", Transaction.date) == year)
        )
        if budget.period == "monthly":
            query = query.filter(extract("month", Transaction.date) == month)

        raw = query.scalar()
        spent = Decimal(str(raw)) if raw else Decimal("0")
        remaining = budget.amount - spent
        percentage = float(spent / budget.amount * 100) if budget.amount > 0 else 0

        cat = db.query(Category).filter(Category.id == budget.category_id).first()
        summaries.append({
            "budget_id": budget.id,
            "category_id": budget.category_id,
            "category_name": cat.name if cat else "Unknown",
            "category_icon": cat.icon if cat else "\U0001f4c1",
            "budget_amount": budget.amount,
            "spent_amount": spent,
            "remaining": remaining,
            "percentage": round(percentage, 1),
            "period": budget.period,
            "currency": budget_currency,
            "year": budget.year,
            "month": budget.month,
        })
    return summaries
