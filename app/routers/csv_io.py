from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io
from app.database import get_db
from app.services.csv_service import export_transactions, get_csv_template, parse_csv, import_transactions

router = APIRouter(prefix="/api/v1/csv", tags=["csv"])

@router.get("/export")
def csv_export(type: str | None = None, db: Session = Depends(get_db)):
    csv_content = export_transactions(db, type)
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"},
    )

@router.get("/template")
def csv_template():
    csv_content = get_csv_template()
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=template.csv"},
    )

MAX_CSV_SIZE = 5 * 1024 * 1024  # 5 MB

@router.post("/import")
async def csv_import(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(400, "File must be a CSV")
    content = await file.read()
    if len(content) > MAX_CSV_SIZE:
        raise HTTPException(400, "File too large. Maximum size is 5 MB.")
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    rows, errors = parse_csv(text)
    if errors:
        return {"success": False, "errors": errors, "valid_rows": len(rows)}

    count = import_transactions(db, rows)
    return {"success": True, "imported": count}
