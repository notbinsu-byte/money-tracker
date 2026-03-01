from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import os

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models import Category, Transaction, Budget, RecurringTransaction, CurrencyRate

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    # Auto-generate recurring transactions on startup
    from app.services.recurring_service import generate_recurring_transactions
    db = SessionLocal()
    try:
        count = generate_recurring_transactions(db)
        if count:
            print(f"Generated {count} recurring transaction(s)")
    finally:
        db.close()
    yield

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app_dir = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(app_dir, "static")), name="static")

# Register API routers
from app.routers import categories, transactions, budgets, recurring, reports, csv_io, currencies, pages
app.include_router(pages.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(recurring.router)
app.include_router(reports.router)
app.include_router(csv_io.router)
app.include_router(currencies.router)
