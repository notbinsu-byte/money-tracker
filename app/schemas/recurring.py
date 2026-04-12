from pydantic import BaseModel, Field
from typing import Union
from datetime import date
from decimal import Decimal

class RecurringBase(BaseModel):
    type: str = Field(..., pattern="^(expense|income)$")
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3, pattern="^[A-Z]{3}$")
    description: str = Field(..., max_length=500)
    category_id: int
    frequency: str = Field(..., pattern="^(daily|weekly|monthly|yearly)$")
    start_date: date
    end_date: Union[str, None] = None  # str to avoid Pydantic v2 Union[date, None] bug

class RecurringCreate(RecurringBase):
    pass

class RecurringUpdate(BaseModel):
    type: Union[str, None] = Field(None, pattern="^(expense|income)$")
    amount: Union[Decimal, None] = Field(None, gt=0)
    currency: Union[str, None] = Field(None, max_length=3, pattern="^[A-Z]{3}$")
    description: Union[str, None] = Field(None, max_length=500)
    category_id: Union[int, None] = None
    frequency: Union[str, None] = Field(None, pattern="^(daily|weekly|monthly|yearly)$")
    start_date: Union[str, None] = None
    end_date: Union[str, None] = None
    is_active: Union[bool, None] = None

class RecurringResponse(BaseModel):
    id: int
    type: str
    amount: Decimal
    currency: str
    description: str
    category_id: int
    frequency: str
    start_date: date
    end_date: Union[date, None] = None
    last_generated: Union[date, None] = None
    is_active: bool
    category_name: Union[str, None] = None
    category_icon: Union[str, None] = None

    model_config = {"from_attributes": True}
