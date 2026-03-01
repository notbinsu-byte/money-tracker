from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.services.report_service import monthly_summary, yearly_summary, trend_data
from app.services.transaction_service import get_category_breakdown

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])

@router.get("/monthly-summary")
def get_monthly_summary(
    year: int = Query(default_factory=lambda: date.today().year),
    month: int = Query(default_factory=lambda: date.today().month),
    db: Session = Depends(get_db),
):
    return monthly_summary(db, year, month)

@router.get("/yearly-summary")
def get_yearly_summary(
    year: int = Query(default_factory=lambda: date.today().year),
    db: Session = Depends(get_db),
):
    return yearly_summary(db, year)

@router.get("/category-breakdown")
def get_category_breakdown_endpoint(
    year: int = Query(default_factory=lambda: date.today().year),
    month: int = Query(default_factory=lambda: date.today().month),
    type: str = Query(default="expense", pattern="^(expense|income)$"),
    db: Session = Depends(get_db),
):
    return get_category_breakdown(db, year, month, type)

@router.get("/trend")
def get_trend(
    months: int = Query(default=12, ge=1, le=24),
    db: Session = Depends(get_db),
):
    return trend_data(db, months)
