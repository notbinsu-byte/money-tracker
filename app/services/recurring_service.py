from sqlalchemy.orm import Session
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from app.models.recurring import RecurringTransaction
from app.models.transaction import Transaction

def generate_recurring_transactions(db: Session) -> int:
    """Generate pending recurring transactions up to today."""
    today = date.today()
    active = db.query(RecurringTransaction).filter(RecurringTransaction.is_active == True).all()
    count = 0

    for rule in active:
        if rule.end_date and rule.end_date < today:
            rule.is_active = False
            continue

        next_date = rule.last_generated or rule.start_date
        if rule.last_generated:
            next_date = _next_occurrence(next_date, rule.frequency)

        while next_date <= today:
            if rule.end_date and next_date > rule.end_date:
                break
            t = Transaction(
                type=rule.type,
                amount=rule.amount,
                currency=rule.currency,
                amount_in_base=rule.amount,
                description=rule.description,
                date=next_date,
                category_id=rule.category_id,
                recurring_id=rule.id,
            )
            db.add(t)
            rule.last_generated = next_date
            count += 1
            next_date = _next_occurrence(next_date, rule.frequency)

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
