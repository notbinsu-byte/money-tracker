from decimal import Decimal
from sqlalchemy.orm import Session
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from app.models.recurring import RecurringTransaction
from app.models.transaction import Transaction
from app.services.currency_service import get_cached_rate
from app.config import settings

def generate_recurring_transactions(db: Session) -> int:
    """Generate pending recurring transactions up to today."""
    today = date.today()
    active = db.query(RecurringTransaction).filter(RecurringTransaction.is_active == True).all()
    count = 0

    for rule in active:
        next_date = rule.last_generated or rule.start_date
        if rule.last_generated:
            next_date = _next_occurrence(next_date, rule.frequency)

        # Generate every occurrence that is due (on or before today) and still
        # within the rule's end_date. Note: we deliberately do NOT skip a rule
        # just because its end_date has passed — a final occurrence falling on
        # the end_date (e.g. end_date == today - 1) must still be generated
        # before the rule is deactivated below.
        while next_date <= today:
            if rule.end_date and next_date > rule.end_date:
                break
            currency = rule.currency or "USD"
            base = settings.BASE_CURRENCY
            if currency != base:
                rate = get_cached_rate(db, base, currency)
                amount_in_base = round(rule.amount / rate, 2) if rate else rule.amount
            else:
                amount_in_base = rule.amount
            t = Transaction(
                type=rule.type,
                amount=rule.amount,
                currency=currency,
                amount_in_base=amount_in_base,
                description=rule.description,
                date=next_date,
                category_id=rule.category_id,
                recurring_id=rule.id,
            )
            db.add(t)
            rule.last_generated = next_date
            count += 1
            next_date = _next_occurrence(next_date, rule.frequency)

        # Deactivate once the rule has run past its end_date (after generating
        # any final on-date occurrence above).
        if rule.end_date and next_date > rule.end_date:
            rule.is_active = False

    db.commit()
    return count

def _next_occurrence(current: date, frequency: str) -> date:
    if frequency == "daily":
        return current + timedelta(days=1)
    elif frequency == "weekly":
        return current + timedelta(weeks=1)
    elif frequency == "monthly":
        return current + relativedelta(months=1)
    elif frequency == "yearly":
        return current + relativedelta(years=1)
    return current + relativedelta(months=1)
