from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])

@router.get("", response_model=list[CategoryResponse])
def list_categories(type: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Category)
    if type:
        query = query.filter(Category.type == type)
    return query.order_by(Category.name).all()

@router.post("", response_model=CategoryResponse, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    if db.query(Category).filter(Category.name == data.name).first():
        raise HTTPException(400, "Category name already exists")
    cat = Category(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(404, "Category not found")
    return cat

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(404, "Category not found")
    update_data = data.model_dump(exclude_unset=True)
    if "name" in update_data:
        existing = db.query(Category).filter(Category.name == update_data["name"], Category.id != category_id).first()
        if existing:
            raise HTTPException(400, "Category name already exists")
    for key, value in update_data.items():
        setattr(cat, key, value)
    db.commit()
    db.refresh(cat)
    return cat

@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(404, "Category not found")
    from app.models.transaction import Transaction
    if db.query(Transaction).filter(Transaction.category_id == category_id).first():
        raise HTTPException(400, "Cannot delete category with existing transactions")
    db.delete(cat)
    db.commit()
