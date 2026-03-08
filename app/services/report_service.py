from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from decimal import Decimal
from app.models.transaction import Transaction
from app.models.category import Category

# Coalesce NULL currency to "USD" for consistent grouping
_tx_currency = func.coalesce(Transaction.currency, "USD")

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
    """Yearly summary with monthly trends, grouped by currency."""
    monthly_data = []
    for month in range(1, 13):
        results = (
            db.query(_tx_currency, Transaction.type, func.sum(Transaction.amount))
            .filter(extract("year", Transaction.date) == year)
            .filter(extract("month", Transaction.date) == month)
            .group_by(_tx_currency, Transaction.type)
            .all()
        )
        month_totals = {}
        for currency, t_type, total in results:
            cur = currency
            if cur not in month_totals:
                month_totals[cur] = {"income": Decimal("0"), "expense": Decimal("0")}
            month_totals[cur][t_type] = total or Decimal("0")
        for cur in month_totals:
            month_totals[cur]["net"] = month_totals[cur]["income"] - month_totals[cur]["expense"]
        monthly_data.append({"month": month, "currencies": month_totals})

    # Build year totals per currency
    year_totals = {}
    for m in monthly_data:
        for cur, vals in m["currencies"].items():
            if cur not in year_totals:
                year_totals[cur] = {"income": Decimal("0"), "expense": Decimal("0")}
            year_totals[cur]["income"] += vals["income"]
            year_totals[cur]["expense"] += vals["expense"]
    for cur in year_totals:
        year_totals[cur]["net"] = year_totals[cur]["income"] - year_totals[cur]["expense"]

    return {
        "year": year,
        "totals": year_totals,
        "monthly_data": monthly_data,
    }

def trend_data(db: Session, months: int = 12) -> list[dict]:
    """Get income/expense trend over the last N months, grouped by currency."""
    from datetime import date
    from dateutil.relativedelta import relativedelta

    today = date.today()
    result = []
    for i in range(months - 1, -1, -1):
        d = today - relativedelta(months=i)
        year, month = d.year, d.month
        totals = (
            db.query(_tx_currency, Transaction.type, func.sum(Transaction.amount))
            .filter(extract("year", Transaction.date) == year)
            .filter(extract("month", Transaction.date) == month)
            .group_by(_tx_currency, Transaction.type)
            .all()
        )
        currencies = {}
        for currency, t_type, total in totals:
            cur = currency
            if cur not in currencies:
                currencies[cur] = {"income": Decimal("0"), "expense": Decimal("0")}
            currencies[cur][t_type] = total or Decimal("0")
        result.append({"year": year, "month": month, "currencies": currencies})
    return result
