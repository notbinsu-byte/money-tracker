from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from decimal import Decimal
from app.database import get_db
from app.config import settings
from app.models.currency import CurrencyRate
from app.services.currency_service import (
    refresh_rates, get_cached_rate, convert_amount,
    rates_are_stale, SUPPORTED_CURRENCIES,
)
from app.schemas.currency import CurrencyRateResponse, ConversionResponse

router = APIRouter(prefix="/api/v1/currencies", tags=["currencies"])

@router.get("")
def list_currencies():
    return {"currencies": SUPPORTED_CURRENCIES, "base": settings.BASE_CURRENCY}

@router.get("/rates", response_model=list[CurrencyRateResponse])
def get_rates(db: Session = Depends(get_db)):
    rates = (
        db.query(CurrencyRate)
        .filter(CurrencyRate.base_currency == settings.BASE_CURRENCY)
        .all()
    )
    return rates

@router.post("/refresh")
async def refresh(db: Session = Depends(get_db)):
    try:
        count = await refresh_rates(db)
    except Exception:
        raise HTTPException(502, "Failed to fetch exchange rates. Please try again later.")
    return {"refreshed": count}

@router.get("/convert", response_model=ConversionResponse)
def convert(
    amount: Decimal = Query(..., gt=0),
    from_currency: str = Query(..., max_length=3),
    to_currency: str = Query(..., max_length=3),
    db: Session = Depends(get_db),
):
    if from_currency == to_currency:
        return ConversionResponse(
            original_amount=amount, converted_amount=amount,
            from_currency=from_currency, to_currency=to_currency,
            rate=Decimal("1"),
        )

    # Try direct rate
    rate = get_cached_rate(db, from_currency, to_currency)
    if rate is None:
        # Try via base currency
        rate_from = get_cached_rate(db, settings.BASE_CURRENCY, from_currency)
        rate_to = get_cached_rate(db, settings.BASE_CURRENCY, to_currency)
        if rate_from and rate_from != 0 and rate_to:
            rate = rate_to / rate_from
        else:
            raise HTTPException(404, f"Exchange rate not found for {from_currency} -> {to_currency}. Try refreshing rates first.")

    converted = convert_amount(amount, rate)
    return ConversionResponse(
        original_amount=amount, converted_amount=converted,
        from_currency=from_currency, to_currency=to_currency,
        rate=round(rate, 8),
    )
