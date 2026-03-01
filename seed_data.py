"""Seed default categories into the database."""
from app.database import SessionLocal, engine, Base
from app.models.category import Category

DEFAULT_CATEGORIES = [
    # Expense categories
    {"name": "Food & Dining", "type": "expense", "icon": "🍔", "color": "#e74c3c", "is_default": True},
    {"name": "Transportation", "type": "expense", "icon": "🚗", "color": "#3498db", "is_default": True},
    {"name": "Housing", "type": "expense", "icon": "🏠", "color": "#9b59b6", "is_default": True},
    {"name": "Utilities", "type": "expense", "icon": "💡", "color": "#f39c12", "is_default": True},
    {"name": "Healthcare", "type": "expense", "icon": "🏥", "color": "#1abc9c", "is_default": True},
    {"name": "Entertainment", "type": "expense", "icon": "🎬", "color": "#e67e22", "is_default": True},
    {"name": "Shopping", "type": "expense", "icon": "🛒", "color": "#2ecc71", "is_default": True},
    {"name": "Education", "type": "expense", "icon": "📚", "color": "#34495e", "is_default": True},
    {"name": "Personal Care", "type": "expense", "icon": "💇", "color": "#fd79a8", "is_default": True},
    {"name": "Insurance", "type": "expense", "icon": "🛡️", "color": "#636e72", "is_default": True},
    {"name": "Gifts & Donations", "type": "expense", "icon": "🎁", "color": "#a29bfe", "is_default": True},
    {"name": "Other Expense", "type": "expense", "icon": "📦", "color": "#b2bec3", "is_default": True},
    # Income categories
    {"name": "Salary", "type": "income", "icon": "💰", "color": "#27ae60", "is_default": True},
    {"name": "Freelance", "type": "income", "icon": "💻", "color": "#2980b9", "is_default": True},
    {"name": "Investments", "type": "income", "icon": "📈", "color": "#8e44ad", "is_default": True},
    {"name": "Rental Income", "type": "income", "icon": "🏘️", "color": "#16a085", "is_default": True},
    {"name": "Other Income", "type": "income", "icon": "💵", "color": "#7f8c8d", "is_default": True},
]

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(Category).count()
        if existing > 0:
            print(f"Database already has {existing} categories. Skipping seed.")
            return
        for cat_data in DEFAULT_CATEGORIES:
            db.add(Category(**cat_data))
        db.commit()
        print(f"Seeded {len(DEFAULT_CATEGORIES)} default categories.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
