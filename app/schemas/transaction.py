from pydantic import BaseModel, Field, model_validator
from typing import Any, Union
import datetime as dt
from decimal import Decimal

class TransactionBase(BaseModel):
    type: str = Field(..., pattern="^(expense|income)$")
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)
    description: str = Field(..., max_length=500)
    date: dt.date
    category_id: int
    notes: Union[str, None] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    type: Union[str, None] = Field(None, pattern="^(expense|income)$")
    amount: Union[Decimal, None] = Field(None, gt=0)
    currency: Union[str, None] = Field(None, max_length=3)
    description: Union[str, None] = Field(None, max_length=500)
    date: Union[str, None] = None
    category_id: Union[int, None] = None
    notes: Union[str, None] = None

    @model_validator(mode="before")
    @classmethod
    def parse_date_field(cls, data: Any) -> Any:
        if isinstance(data, dict) and data.get("date"):
            val = data["date"]
            if isinstance(val, str):
                data["date"] = val  # keep as string, convert in router
        return data

class TransactionResponse(TransactionBase):
    id: int
    amount_in_base: Decimal
    recurring_id: Union[int, None] = None
    created_at: Union[dt.datetime, None] = None
    updated_at: Union[dt.datetime, None] = None
    category_name: Union[str, None] = None
    category_icon: Union[str, None] = None
    category_color: Union[str, None] = None

    model_config = {"from_attributes": True}

class TransactionListResponse(BaseModel):
    items: list[TransactionResponse]
    total: int
    page: int
    per_page: int
    pages: int
