import httpx
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.currency import CurrencyRate
from app.config import settings

SUPPORTED_CURRENCIES = ["USD", "PHP"]

async def fetch_rates(base: str = None) -> dict[str, Decimal]:
    """Fetch latest rates from frankfurter.app."""
    base = base or settings.BASE_CURRENCY
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{settings.CURRENCY_API_URL}/latest", params={"from": base})
        resp.raise_for_status()
        data = resp.json()
        return {k: Decimal(str(v)) for k, v in data.get("rates", {}).items()}

async def refresh_rates(db: Session, base: str = None) -> int:
    """Fetch and cache latest exchange rates."""
    base = base or settings.BASE_CURRENCY
    rates = await fetch_rates(base)
    now = datetime.now(timezone.utc)
    count = 0
    for currency, rate in rates.items():
        existing = (
            db.query(CurrencyRate)
            .filter(CurrencyRate.base_currency == base, CurrencyRate.target_currency == currency)
            .first()
        )
        if existing:
            existing.rate = rate
            existing.fetched_at = now
        else:
            db.add(CurrencyRate(
                base_currency=base, target_currency=currency, rate=rate, fetched_at=now
            ))
        count += 1
    db.commit()
    return count

def get_cached_rate(db: Session, base: str, target: str) -> Decimal | None:
    """Get a cached exchange rate."""
    if base == target:
        return Decimal("1")
    rate_entry = (
        db.query(CurrencyRate)
        .filter(CurrencyRate.base_currency == base, CurrencyRate.target_currency == target)
        .first()
    )
    if rate_entry:
        return rate_entry.rate
    return None

def convert_amount(amount: Decimal, rate: Decimal) -> Decimal:
    """Convert an amount using a given rate."""
    return round(amount * rate, 2)

def rates_are_stale(db: Session, base: str = None) -> bool:
    """Check if cached rates are older than 24 hours."""
    base = base or settings.BASE_CURRENCY
    latest = (
        db.query(CurrencyRate)
        .filter(CurrencyRate.base_currency == base)
        .order_by(CurrencyRate.fetched_at.desc())
        .first()
    )
    if not latest or not latest.fetched_at:
        return True
    return datetime.now(timezone.utc) - latest.fetched_at.replace(tzinfo=timezone.utc) > timedelta(hours=24)
