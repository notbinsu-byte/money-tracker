from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
import os

router = APIRouter(tags=["pages"])

app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates")
templates = Jinja2Templates(directory=os.path.abspath(templates_dir))

@router.get("/")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/transactions")
async def transactions_page(request: Request):
    return templates.TemplateResponse("transactions.html", {"request": request})

@router.get("/categories")
async def categories_page(request: Request):
    return templates.TemplateResponse("categories.html", {"request": request})

@router.get("/budgets")
async def budgets_page(request: Request):
    return templates.TemplateResponse("budgets.html", {"request": request})

@router.get("/recurring")
async def recurring_page(request: Request):
    return templates.TemplateResponse("recurring.html", {"request": request})

@router.get("/reports")
async def reports_page(request: Request):
    return templates.TemplateResponse("reports.html", {"request": request})

@router.get("/import-export")
async def import_export_page(request: Request):
    return templates.TemplateResponse("import_export.html", {"request": request})

@router.get("/ai-chat")
async def ai_chat_page(request: Request):
    return templates.TemplateResponse("ai_chat.html", {"request": request})
