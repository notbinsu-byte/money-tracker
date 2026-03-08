import csv
import io
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.models.category import Category

EXPORT_FIELDS = ["date", "type", "amount", "currency", "description", "category", "notes"]

def _sanitize_csv_field(value: str) -> str:
    """Prevent CSV injection by escaping formula-triggering characters."""
    if value and value[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + value
    return value

def export_transactions(db: Session, type: str | None = None) -> str:
    """Export transactions to CSV string."""
    query = db.query(Transaction).order_by(Transaction.date.desc())
    if type:
        query = query.filter(Transaction.type == type)
    transactions = query.all()

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=EXPORT_FIELDS)
    writer.writeheader()
    for t in transactions:
        writer.writerow({
            "date": t.date.isoformat(),
            "type": t.type,
            "amount": str(t.amount),
            "currency": t.currency,
            "description": _sanitize_csv_field(t.description),
            "category": _sanitize_csv_field(t.category.name if t.category else ""),
            "notes": _sanitize_csv_field(t.notes or ""),
        })
    return output.getvalue()

def get_csv_template() -> str:
    """Return an empty CSV template."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=EXPORT_FIELDS)
    writer.writeheader()
    writer.writerow({
        "date": "2024-01-15",
        "type": "expense",
        "amount": "29.99",
        "currency": "USD",
        "description": "Example transaction",
        "category": "Food & Dining",
        "notes": "Optional notes",
    })
    return output.getvalue()

def parse_csv(content: str) -> tuple[list[dict], list[str]]:
    """Parse CSV content and return (rows, errors)."""
    content = content.lstrip("\ufeff")
    reader = csv.DictReader(io.StringIO(content))
    rows = []
    errors = []
    for i, row in enumerate(reader, start=2):
        line_errors = []
        if not row.get("date"):
            line_errors.append(f"Row {i}: missing date")
        else:
            try:
                datetime.strptime(row["date"].strip(), "%Y-%m-%d")
            except ValueError:
                line_errors.append(f"Row {i}: invalid date format (use YYYY-MM-DD)")
        if row.get("type", "").strip() not in ("expense", "income"):
            line_errors.append(f"Row {i}: type must be 'expense' or 'income'")
        if not row.get("amount"):
            line_errors.append(f"Row {i}: missing amount")
        else:
            try:
                amt = Decimal(row["amount"].strip())
                if amt <= 0:
                    line_errors.append(f"Row {i}: amount must be positive")
            except InvalidOperation:
                line_errors.append(f"Row {i}: invalid amount")
        if not row.get("description", "").strip():
            line_errors.append(f"Row {i}: missing description")

        if line_errors:
            errors.extend(line_errors)
        else:
            rows.append(row)
    return rows, errors

def import_transactions(db: Session, rows: list[dict]) -> int:
    """Import parsed CSV rows as transactions."""
    count = 0
    for row in rows:
        cat_name = row.get("category", "").strip()
        category = db.query(Category).filter(Category.name == cat_name).first()
        if not category:
            category = db.query(Category).filter(
                Category.name == ("Other Expense" if row["type"].strip() == "expense" else "Other Income")
            ).first()

        if not category:
            category = db.query(Category).first()
        if not category:
            raise ValueError("No categories exist in database. Please seed categories first.")

        t = Transaction(
            type=row["type"].strip(),
            amount=Decimal(row["amount"].strip()),
            currency=row.get("currency", "USD").strip() or "USD",
            amount_in_base=Decimal(row["amount"].strip()),
            description=row["description"].strip(),
            date=datetime.strptime(row["date"].strip(), "%Y-%m-%d").date(),
            category_id=category.id if category else None,
            notes=row.get("notes", "").strip() or None,
        )
        db.add(t)
        count += 1
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise ValueError(f"Database error during import: {str(e)}")
    return count
