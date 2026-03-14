from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.models.savings_goal import SavingsGoal
from app.schemas.savings_goal import (
    SavingsGoalCreate, SavingsGoalUpdate, SavingsGoalResponse, ContributeRequest,
)

router = APIRouter(prefix="/api/v1/savings-goals", tags=["savings-goals"])


def _to_response(g: SavingsGoal) -> SavingsGoalResponse:
    target = float(g.target_amount) if g.target_amount else 1
    current = float(g.current_amount or 0)
    pct = round(min(current / target * 100, 100), 1) if target > 0 else 0.0
    days_rem = None
    if g.deadline:
        delta = g.deadline - date.today()
        days_rem = max(delta.days, 0)
    return SavingsGoalResponse(
        id=g.id,
        name=g.name,
        target_amount=g.target_amount,
        current_amount=g.current_amount or 0,
        currency=g.currency or "USD",
        deadline=g.deadline,
        icon=g.icon or "🎯",
        color=g.color or "#2ecc71",
        notes=g.notes,
        is_completed=g.is_completed,
        percentage=pct,
        days_remaining=days_rem,
    )


@router.get("", response_model=list[SavingsGoalResponse])
def list_goals(
    status: str = Query("all", pattern="^(active|completed|all)$"),
    db: Session = Depends(get_db),
):
    query = db.query(SavingsGoal)
    if status == "active":
        query = query.filter(SavingsGoal.is_completed == False)
    elif status == "completed":
        query = query.filter(SavingsGoal.is_completed == True)
    goals = query.order_by(SavingsGoal.created_at.desc()).all()
    return [_to_response(g) for g in goals]


@router.post("", response_model=SavingsGoalResponse, status_code=201)
def create_goal(data: SavingsGoalCreate, db: Session = Depends(get_db)):
    goal = SavingsGoal(**data.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return _to_response(goal)


@router.get("/{goal_id}", response_model=SavingsGoalResponse)
def get_goal(goal_id: int, db: Session = Depends(get_db)):
    g = db.query(SavingsGoal).filter(SavingsGoal.id == goal_id).first()
    if not g:
        raise HTTPException(404, "Savings goal not found")
    return _to_response(g)


@router.put("/{goal_id}", response_model=SavingsGoalResponse)
def update_goal(goal_id: int, data: SavingsGoalUpdate, db: Session = Depends(get_db)):
    g = db.query(SavingsGoal).filter(SavingsGoal.id == goal_id).first()
    if not g:
        raise HTTPException(404, "Savings goal not found")
    update_data = data.model_dump(exclude_unset=True)
    # Handle deadline string → date conversion (Pydantic v2 bug workaround)
    if "deadline" in update_data:
        val = update_data["deadline"]
        if val is not None and val != "":
            from datetime import date as date_cls
            update_data["deadline"] = date_cls.fromisoformat(val)
        else:
            update_data["deadline"] = None
    for key, value in update_data.items():
        setattr(g, key, value)
    db.commit()
    db.refresh(g)
    return _to_response(g)


@router.put("/{goal_id}/contribute", response_model=SavingsGoalResponse)
def contribute(goal_id: int, data: ContributeRequest, db: Session = Depends(get_db)):
    g = db.query(SavingsGoal).filter(SavingsGoal.id == goal_id).first()
    if not g:
        raise HTTPException(404, "Savings goal not found")
    if g.is_completed:
        raise HTTPException(400, "Goal is already completed")
    current = g.current_amount or 0
    g.current_amount = current + data.amount
    if g.current_amount >= g.target_amount:
        g.current_amount = g.target_amount
        g.is_completed = True
    db.commit()
    db.refresh(g)
    return _to_response(g)


@router.delete("/{goal_id}", status_code=204)
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    g = db.query(SavingsGoal).filter(SavingsGoal.id == goal_id).first()
    if not g:
        raise HTTPException(404, "Savings goal not found")
    db.delete(g)
    db.commit()
