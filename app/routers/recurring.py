from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import datetime as dt
from app.database import get_db
from app.models.recurring import RecurringTransaction
from app.models.category import Category
from app.schemas.recurring import RecurringCreate, RecurringUpdate, RecurringResponse
from app.services.recurring_service import generate_recurring_transactions

router = APIRouter(prefix="/api/v1/recurring", tags=["recurring"])

def _to_response(r: RecurringTransaction) -> RecurringResponse:
    return RecurringResponse(
        id=r.id, type=r.type, amount=r.amount, currency=r.currency,
        description=r.description, category_id=r.category_id,
        frequency=r.frequency, start_date=r.start_date, end_date=r.end_date,
        last_generated=r.last_generated, is_active=r.is_active,
        category_name=r.category.name if r.category else None,
        category_icon=r.category.icon if r.category else None,
    )

@router.get("", response_model=list[RecurringResponse])
def list_recurring(db: Session = Depends(get_db)):
    items = db.query(RecurringTransaction).order_by(RecurringTransaction.start_date.desc()).all()
    return [_to_response(r) for r in items]

@router.post("", response_model=RecurringResponse, status_code=201)
def create_recurring(data: RecurringCreate, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == data.category_id).first()
    if not cat:
        raise HTTPException(400, "Category not found")
    dump = data.model_dump()
    # Convert end_date string to date object
    if isinstance(dump.get("end_date"), str):
        try:
            dump["end_date"] = dt.date.fromisoformat(dump["end_date"])
        except ValueError:
            raise HTTPException(400, "Invalid end_date format. Use YYYY-MM-DD.")
    r = RecurringTransaction(**dump)
    db.add(r)
    db.commit()
    db.refresh(r)
    return _to_response(r)

@router.post("/generate")
def trigger_generation(db: Session = Depends(get_db)):
    count = generate_recurring_transactions(db)
    return {"generated": count}

@router.get("/{recurring_id}", response_model=RecurringResponse)
def get_recurring(recurring_id: int, db: Session = Depends(get_db)):
    r = db.query(RecurringTransaction).filter(RecurringTransaction.id == recurring_id).first()
    if not r:
        raise HTTPException(404, "Recurring transaction not found")
    return _to_response(r)

@router.put("/{recurring_id}", response_model=RecurringResponse)
def update_recurring(recurring_id: int, data: RecurringUpdate, db: Session = Depends(get_db)):
    r = db.query(RecurringTransaction).filter(RecurringTransaction.id == recurring_id).first()
    if not r:
        raise HTTPException(404, "Recurring transaction not found")
    update_data = data.model_dump(exclude_unset=True)
    # Convert date strings to date objects
    for date_field in ("start_date", "end_date"):
        if date_field in update_data and isinstance(update_data[date_field], str):
            try:
                update_data[date_field] = dt.date.fromisoformat(update_data[date_field])
            except ValueError:
                raise HTTPException(400, f"Invalid {date_field} format. Use YYYY-MM-DD.")
    if "category_id" in update_data:
        cat = db.query(Category).filter(Category.id == update_data["category_id"]).first()
        if not cat:
            raise HTTPException(400, "Category not found")
    for key, value in update_data.items():
        setattr(r, key, value)
    db.commit()
    db.refresh(r)
    return _to_response(r)

@router.delete("/{recurring_id}", status_code=204)
def delete_recurring(recurring_id: int, db: Session = Depends(get_db)):
    r = db.query(RecurringTransaction).filter(RecurringTransaction.id == recurring_id).first()
    if not r:
        raise HTTPException(404, "Recurring transaction not found")
    db.delete(r)
    db.commit()
