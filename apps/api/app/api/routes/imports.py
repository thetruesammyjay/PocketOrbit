import csv

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.import_service import preview_csv

router = APIRouter()
MAX_IMPORT_BYTES = 5 * 1024 * 1024


@router.post("/preview")
async def preview_import(file: UploadFile = File(...)) -> dict[str, object]:
    filename = file.filename or "upload"
    if not filename.lower().endswith(".csv"):
        raise HTTPException(status_code=415, detail="Upload a CSV file to preview it.")

    contents = await file.read(MAX_IMPORT_BYTES + 1)
    if len(contents) > MAX_IMPORT_BYTES:
        raise HTTPException(status_code=413, detail="The preview limit is 5 MB.")

    try:
        return preview_csv(contents, filename)
    except (UnicodeDecodeError, csv.Error) as exc:
        raise HTTPException(status_code=422, detail="The CSV format could not be read.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
