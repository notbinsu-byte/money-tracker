from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from decimal import Decimal
from app.models.transaction import Transaction
from app.models.category import Category

def monthly_summary(db: Session, year: int, month: int) -> dict:
    """Complete monthly summary with totals and category breakdowns."""
    from app.services.transaction_service import get_monthly_totals, get_category_breakdown
    totals = get_monthly_totals(db, year, month)
    expense_breakdown = get_category_breakdown(db, year, month, "expense")
    income_breakdown = get_category_breakdown(db, year, month, "income")
    return {
        "year": year,
        "month": month,
        "totals": totals,
        "expense_breakdown": expense_breakdown,
        "income_breakdown": income_breakdown,
    }

def yearly_summary(db: Session, year: int) -> dict:
    """Yearly summary with monthly trends."""
    monthly_data = []
    for month in range(1, 13):
        results = (
            db.query(Transaction.type, func.sum(Transaction.amount_in_base))
            .filter(extract("year", Transaction.date) == year)
            .filter(extract("month", Transaction.date) == month)
            .group_by(Transaction.type)
            .all()
        )
        totals = {"month": month, "income": Decimal("0"), "expense": Decimal("0")}
        for t_type, total in results:
            totals[t_type] = total or Decimal("0")
        totals["net"] = totals["income"] - totals["expense"]
        monthly_data.append(totals)

    year_totals = {
        "income": sum(m["income"] for m in monthly_data),
        "expense": sum(m["expense"] for m in monthly_data),
    }
    year_totals["net"] = year_totals["income"] - year_totals["expense"]

    return {
        "year": year,
        "totals": year_totals,
        "monthly_data": monthly_data,
    }

def trend_data(db: Session, months: int = 12) -> list[dict]:
    """Get income/expense trend over the last N months."""
    from datetime import date, timedelta
    from dateutil.relativedelta import relativedelta

    today = date.today()
    result = []
    for i in range(months - 1, -1, -1):
        d = today - relativedelta(months=i)
        year, month = d.year, d.month
        totals = (
            db.query(Transaction.type, func.sum(Transaction.amount_in_base))
            .filter(extract("year", Transaction.date) == year)
            .filter(extract("month", Transaction.date) == month)
            .group_by(Transaction.type)
            .all()
        )
        entry = {"year": year, "month": month, "income": Decimal("0"), "expense": Decimal("0")}
        for t_type, total in totals:
            entry[t_type] = total or Decimal("0")
        result.append(entry)
    return result
