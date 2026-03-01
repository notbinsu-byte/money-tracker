from pydantic import BaseModel, Field
from typing import Union
from decimal import Decimal

class BudgetBase(BaseModel):
    category_id: int
    amount: Decimal = Field(..., gt=0)
    period: str = Field(..., pattern="^(monthly|yearly)$")
    year: int
    month: Union[int, None] = Field(None, ge=1, le=12)

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BaseModel):
    amount: Union[Decimal, None] = Field(None, gt=0)
    period: Union[str, None] = Field(None, pattern="^(monthly|yearly)$")
    year: Union[int, None] = None
    month: Union[int, None] = Field(None, ge=1, le=12)

class BudgetResponse(BudgetBase):
    id: int
    category_name: Union[str, None] = None
    category_icon: Union[str, None] = None

    model_config = {"from_attributes": True}

class BudgetSummary(BaseModel):
    budget_id: int
    category_id: int
    category_name: str
    category_icon: str
    budget_amount: Decimal
    spent_amount: Decimal
    remaining: Decimal
    percentage: float
    period: str
    year: int
    month: Union[int, None] = None
