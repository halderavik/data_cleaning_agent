import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from tempfile import NamedTemporaryFile
from typing import Any
from pandas import read_csv
import openpyxl
import numpy as np
import logging
import traceback

from backend.security import get_current_active_user
from backend.models import User
from backend.services.spss_processor import SPSSProcessor
from backend.cleaning_engine import CleaningEngine

router = APIRouter(
    prefix="/files",
    tags=["files"],
    responses={404: {"description": "Not found"}},
)

def to_serializable(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_serializable(i) for i in obj]
    return obj

@router.post("/analyze-spss", summary="Upload and analyze SPSS file")
async def analyze_spss_file(
    file: UploadFile = File(...)
) -> Any:
    """
    Upload an SPSS (.sav) file and return its structure analysis.
    Args:
        file (UploadFile): The uploaded SPSS file.
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
        # Load data as DataFrame for cleaning
        import pyreadstat
        df, meta = pyreadstat.read_sav(tmp_path)
        cleaning_engine = CleaningEngine()
        cleaning_results = cleaning_engine.process_data(df)
    except Exception as e:
        logging.error(f"Failed to process SPSS file: {str(e)}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to process SPSS file: {str(e)}")
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
    return JSONResponse(content=to_serializable({"structure": structure, "cleaning_results": cleaning_results}))

@router.post("/analyze-csv", summary="Upload and analyze CSV file")
async def analyze_csv_file(
    file: UploadFile = File(...)
) -> Any:
    """
    Upload a CSV file and return its structure analysis.
    """
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
    try:
        with NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        df = read_csv(tmp_path)
        structure = {
            "columns": [to_serializable(col) for col in df.columns.tolist()],
            "row_count": int(len(df)),
            "preview": [{k: to_serializable(v) for k, v in row.items()} for row in df.head(5).to_dict(orient="records")]
        }
        cleaning_engine = CleaningEngine()
        cleaning_results = cleaning_engine.process_data(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process CSV file: {str(e)}")
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
    return JSONResponse(content=to_serializable({"structure": structure, "cleaning_results": cleaning_results}))

@router.post("/analyze-excel", summary="Upload and analyze Excel file")
async def analyze_excel_file(
    file: UploadFile = File(...)
) -> Any:
    """
    Upload an Excel file (.xls, .xlsx) and return its structure analysis.
    """
    if not (file.filename.lower().endswith(".xls") or file.filename.lower().endswith(".xlsx")):
        raise HTTPException(status_code=400, detail="Only Excel files (.xls, .xlsx) are supported.")
    try:
        with NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        wb = openpyxl.load_workbook(tmp_path, read_only=True)
        sheet = wb.active
        columns = [cell.value for cell in next(sheet.iter_rows(min_row=1, max_row=1))]
        row_count = sheet.max_row - 1
        preview = []
        for i, row in enumerate(sheet.iter_rows(min_row=2, max_row=6), start=1):
            preview.append({columns[j]: cell.value for j, cell in enumerate(row)})
        import pandas as pd
        data = list(sheet.values)
        df = pd.DataFrame(data[1:], columns=data[0])
        structure = {
            "columns": [to_serializable(col) for col in columns],
            "row_count": int(row_count),
            "preview": [
                {k: to_serializable(v) for k, v in row.items()} for row in preview
            ]
        }
        cleaning_engine = CleaningEngine()
        cleaning_results = cleaning_engine.process_data(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process Excel file: {str(e)}")
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
    return JSONResponse(content=to_serializable({"structure": structure, "cleaning_results": cleaning_results})) 