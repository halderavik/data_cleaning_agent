import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from tempfile import NamedTemporaryFile
from typing import Any

from backend.security import get_current_active_user
from backend.models import User
from backend.services.spss_processor import SPSSProcessor

router = APIRouter(
    prefix="/files",
    tags=["files"],
    responses={404: {"description": "Not found"}},
)

@router.post("/analyze-spss", summary="Upload and analyze SPSS file")
async def analyze_spss_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Upload an SPSS (.sav) file and return its structure analysis.
    Args:
        file (UploadFile): The uploaded SPSS file.
        current_user (User): The authenticated user.
    Returns:
        dict: Structure analysis of the SPSS file.
    Raises:
        HTTPException: If file is not a valid SPSS file or analysis fails.
    """
    if not file.filename.lower().endswith(".sav"):
        raise HTTPException(status_code=400, detail="Only SPSS (.sav) files are supported.")

    try:
        with NamedTemporaryFile(delete=False, suffix=".sav") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        processor = SPSSProcessor()
        structure = processor.load_file(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process SPSS file: {str(e)}")
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
    return JSONResponse(content=structure) 