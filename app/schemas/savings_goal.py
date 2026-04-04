from pydantic import BaseModel, Field
from typing import Union
from decimal import Decimal
from datetime import date


class SavingsGoalBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    target_amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD", pattern="^[A-Z]{3}$")
    deadline: Union[date, None] = None
    icon: str = Field(default="🎯", max_length=50)
    color: str = Field(default="#2ecc71", pattern="^#[0-9a-fA-F]{6}$")
    notes: Union[str, None] = Field(None, max_length=500)


class SavingsGoalCreate(SavingsGoalBase):
    pass


class SavingsGoalUpdate(BaseModel):
    name: Union[str, None] = Field(None, min_length=1, max_length=100)
    target_amount: Union[Decimal, None] = Field(None, gt=0)
    current_amount: Union[Decimal, None] = Field(None, ge=0)
    currency: Union[str, None] = Field(None, pattern="^[A-Z]{3}$")
    deadline: Union[str, None] = None  # str due to Pydantic v2 date bug
    icon: Union[str, None] = Field(None, max_length=50)
    color: Union[str, None] = Field(None, pattern="^#[0-9a-fA-F]{6}$")
    notes: Union[str, None] = Field(None, max_length=500)


class SavingsGoalResponse(SavingsGoalBase):
    id: int
    current_amount: Decimal
    is_completed: bool
    percentage: float = 0.0
    days_remaining: Union[int, None] = None

    model_config = {"from_attributes": True}


class ContributeRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
