from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from datetime import date
from decimal import Decimal
import datetime as dt
from app.database import get_db
from app.models.transaction import Transaction
from app.models.category import Category
from app.schemas.transaction import (
    TransactionCreate, TransactionUpdate, TransactionResponse, TransactionListResponse
)

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])

def _to_response(t: Transaction) -> dict:
    return {
        "id": t.id,
        "type": t.type,
        "amount": t.amount,
        "currency": t.currency,
        "amount_in_base": t.amount_in_base,
        "description": t.description,
        "date": t.date,
        "category_id": t.category_id,
        "recurring_id": t.recurring_id,
        "notes": t.notes,
        "created_at": t.created_at,
        "updated_at": t.updated_at,
        "category_name": t.category.name if t.category else None,
        "category_icon": t.category.icon if t.category else None,
        "category_color": t.category.color if t.category else None,
    }

@router.get("", response_model=TransactionListResponse)
def list_transactions(
    search: str | None = None,
    category_id: int | None = None,
    type: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    amount_min: Decimal | None = None,
    amount_max: Decimal | None = None,
    sort_by: str = Query(default="date", pattern="^(date|amount|description|created_at)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Transaction)

    if search:
        query = query.filter(Transaction.description.ilike(f"%{search}%"))
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if type:
        query = query.filter(Transaction.type == type)
    if date_from:
        query = query.filter(Transaction.date >= date_from)
    if date_to:
        query = query.filter(Transaction.date <= date_to)
    if amount_min is not None:
        query = query.filter(Transaction.amount >= amount_min)
    if amount_max is not None:
        query = query.filter(Transaction.amount <= amount_max)

    total = query.count()

    sort_col = getattr(Transaction, sort_by, Transaction.date)
    order_func = desc if sort_order == "desc" else asc
    query = query.order_by(order_func(sort_col))

    offset = (page - 1) * per_page
    transactions = query.offset(offset).limit(per_page).all()
    pages = (total + per_page - 1) // per_page if total > 0 else 1

    return TransactionListResponse(
        items=[TransactionResponse(**_to_response(t)) for t in transactions],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )

@router.post("", response_model=TransactionResponse, status_code=201)
def create_transaction(data: TransactionCreate, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == data.category_id).first()
    if not cat:
        raise HTTPException(400, "Category not found")
    t = Transaction(
        **data.model_dump(),
        amount_in_base=data.amount,  # same currency for now, Phase 8 adds conversion
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return TransactionResponse(**_to_response(t))

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    t = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not t:
        raise HTTPException(404, "Transaction not found")
    return TransactionResponse(**_to_response(t))

@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(transaction_id: int, data: TransactionUpdate, db: Session = Depends(get_db)):
    t = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not t:
        raise HTTPException(404, "Transaction not found")
    update_data = data.model_dump(exclude_unset=True)
    if "date" in update_data and isinstance(update_data["date"], str):
        try:
            update_data["date"] = dt.date.fromisoformat(update_data["date"])
        except ValueError:
            raise HTTPException(400, f"Invalid date format: {update_data['date']}. Use YYYY-MM-DD.")
    if "category_id" in update_data:
        cat = db.query(Category).filter(Category.id == update_data["category_id"]).first()
        if not cat:
            raise HTTPException(400, "Category not found")
    for key, value in update_data.items():
        setattr(t, key, value)
    if "amount" in update_data:
        t.amount_in_base = update_data["amount"]  # Phase 8 adds conversion
    db.commit()
    db.refresh(t)
    return TransactionResponse(**_to_response(t))

@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    t = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not t:
        raise HTTPException(404, "Transaction not found")
    db.delete(t)
    db.commit()
