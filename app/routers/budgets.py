from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.models.budget import Budget
from app.models.category import Category
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse, BudgetSummary
from app.services.budget_service import get_budget_summary

router = APIRouter(prefix="/api/v1/budgets", tags=["budgets"])

@router.get("", response_model=list[BudgetResponse])
def list_budgets(
    year: int = Query(default_factory=lambda: date.today().year),
    month: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Budget).filter(Budget.year == year)
    if month is not None:
        query = query.filter((Budget.month == month) | (Budget.month.is_(None)))
    budgets = query.all()
    result = []
    for b in budgets:
        cat = db.query(Category).filter(Category.id == b.category_id).first()
        result.append(BudgetResponse(
            id=b.id,
            category_id=b.category_id,
            amount=b.amount,
            currency=b.currency or "USD",
            period=b.period,
            year=b.year,
            month=b.month,
            category_name=cat.name if cat else None,
            category_icon=cat.icon if cat else None,
        ))
    return result

@router.post("", response_model=BudgetResponse, status_code=201)
def create_budget(data: BudgetCreate, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == data.category_id).first()
    if not cat:
        raise HTTPException(400, "Category not found")
    existing = db.query(Budget).filter(
        Budget.category_id == data.category_id,
        Budget.year == data.year,
        Budget.month == data.month,
        Budget.currency == data.currency,
    ).first()
    if existing:
        raise HTTPException(400, "Budget already exists for this category, currency, and period")
    budget = Budget(**data.model_dump())
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return BudgetResponse(
        id=budget.id, category_id=budget.category_id, amount=budget.amount,
        currency=budget.currency or "USD",
        period=budget.period, year=budget.year, month=budget.month,
        category_name=cat.name, category_icon=cat.icon,
    )

@router.get("/summary", response_model=list[BudgetSummary])
def budget_summary(
    year: int = Query(default_factory=lambda: date.today().year),
    month: int = Query(default_factory=lambda: date.today().month),
    db: Session = Depends(get_db),
):
    return get_budget_summary(db, year, month)

@router.get("/{budget_id}", response_model=BudgetResponse)
def get_budget(budget_id: int, db: Session = Depends(get_db)):
    b = db.query(Budget).filter(Budget.id == budget_id).first()
    if not b:
        raise HTTPException(404, "Budget not found")
    cat = db.query(Category).filter(Category.id == b.category_id).first()
    return BudgetResponse(
        id=b.id, category_id=b.category_id, amount=b.amount,
        currency=b.currency or "USD",
        period=b.period, year=b.year, month=b.month,
        category_name=cat.name if cat else None, category_icon=cat.icon if cat else None,
    )

@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(budget_id: int, data: BudgetUpdate, db: Session = Depends(get_db)):
    b = db.query(Budget).filter(Budget.id == budget_id).first()
    if not b:
        raise HTTPException(404, "Budget not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(b, key, value)
    db.commit()
    db.refresh(b)
    cat = db.query(Category).filter(Category.id == b.category_id).first()
    return BudgetResponse(
        id=b.id, category_id=b.category_id, amount=b.amount,
        currency=b.currency or "USD",
        period=b.period, year=b.year, month=b.month,
        category_name=cat.name if cat else None, category_icon=cat.icon if cat else None,
    )

@router.delete("/{budget_id}", status_code=204)
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    b = db.query(Budget).filter(Budget.id == budget_id).first()
    if not b:
        raise HTTPException(404, "Budget not found")
    db.delete(b)
    db.commit()
