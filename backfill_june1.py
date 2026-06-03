"""One-off: backfill the June 1 2026 occurrences for the iPad Pro M5 and
Remitly Credit Tams recurring rules that were skipped by the old end_date
guard. Re-activates those rules so the (now fixed) generator emits the
missing on-end-date occurrence, then lets it re-deactivate them.

Run once on the machine that owns money_tracker.db:
    .venv\\Scripts\\activate
    python backfill_june1.py
"""
from app.database import SessionLocal
from app.models.recurring import RecurringTransaction
from app.models.transaction import Transaction
from app.services.recurring_service import generate_recurring_transactions

RULE_IDS = (9, 11)  # iPad Pro M5 Monthly, Remitly Credit Tams

db = SessionLocal()
try:
    # Guard against double-running: skip if a June 1 tx already exists.
    already = (
        db.query(Transaction)
        .filter(Transaction.recurring_id.in_(RULE_IDS))
        .filter(Transaction.date == __import__("datetime").date(2026, 6, 1))
        .count()
    )
    if already:
        print(f"June 1 transactions already exist for these rules ({already}). Nothing to do.")
    else:
        for rid in RULE_IDS:
            r = db.get(RecurringTransaction, rid)
            if r:
                r.is_active = True
                print(f"Re-activated rule {rid}: {r.description} (end {r.end_date}, last_generated {r.last_generated})")
        db.commit()
        n = generate_recurring_transactions(db)
        print(f"Generated {n} transaction(s).")
        for rid in RULE_IDS:
            r = db.get(RecurringTransaction, rid)
            print(f"  rule {rid}: active={r.is_active} last_generated={r.last_generated}")
finally:
    db.close()
