from pydantic import BaseModel, Field
from typing import Union
from datetime import datetime
from decimal import Decimal

class CurrencyRateResponse(BaseModel):
    base_currency: str
    target_currency: str
    rate: Decimal
    fetched_at: Union[datetime, None] = None

    model_config = {"from_attributes": True}

class ConversionRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    from_currency: str = Field(..., max_length=3)
    to_currency: str = Field(..., max_length=3)

class ConversionResponse(BaseModel):
    original_amount: Decimal
    converted_amount: Decimal
    from_currency: str
    to_currency: str
    rate: Decimal
