from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.models import DataFile
from backend.app.core.advanced_scrubbing import AdvancedScrubbing
from backend.app.core.bot_detection import BotDetector
from backend.app.core.nlp_engine import NLEngine
from backend.services.spss_processor import SPSSProcessor
from backend.database.base import get_db
import pandas as pd
from pydantic import BaseModel
import traceback
import os

router = APIRouter(prefix="/api", tags=["analysis"])

class FileIdRequest(BaseModel):
    file_id: str

@router.post("/advanced-scrubbing")
async def run_advanced_scrubbing(request: FileIdRequest, db: Session = Depends(get_db)):
    data_file = db.query(DataFile).filter(DataFile.id == request.file_id).first()
    if not data_file:
        raise HTTPException(status_code=404, detail="Data file not found")
    try:
        file_path = os.path.join(os.getcwd(), 'uploads', data_file.original_filename)
        if data_file.file_type == 'sav':
            spss = SPSSProcessor()
            spss.load_file(file_path)
            df = spss.data
        else:
            df = pd.read_csv(file_path)
        scrubbing = AdvancedScrubbing()
        results = {}
        summary = {}
        if 'text' in df.columns:
            brevity = scrubbing.check_response_brevity(df, 'text')
            results['response_brevity'] = brevity
            summary['brief_responses'] = brevity['brief_responses']
        else:
            return {"summary": {}, "detailed_results": {}, "error": "No 'text' column found in data."}
        return {"summary": summary, "detailed_results": results}
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Advanced scrubbing failed: {str(e)}")

@router.post("/bot-detection")
async def run_bot_detection(request: FileIdRequest, db: Session = Depends(get_db)):
    data_file = db.query(DataFile).filter(DataFile.id == request.file_id).first()
    if not data_file:
        raise HTTPException(status_code=404, detail="Data file not found")
    try:
        file_path = os.path.join(os.getcwd(), 'uploads', data_file.original_filename)
        if data_file.file_type == 'sav':
            spss = SPSSProcessor()
            spss.load_file(file_path)
            df = spss.data
        else:
            df = pd.read_csv(file_path)
        detector = BotDetector()
        text_columns = [col for col in df.columns if df[col].dtype == object]
        if not text_columns:
            return {"summary": {}, "detailed_results": {}, "error": "No text columns found in data."}
        patterns = detector.analyze_patterns(df, text_columns)
        return {"summary": {"patterns_found": patterns['patterns_found']}, "detailed_results": patterns}
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Bot detection failed: {str(e)}")

@router.post("/nlp-engine")
async def run_nlp_engine(request: FileIdRequest, db: Session = Depends(get_db)):
    data_file = db.query(DataFile).filter(DataFile.id == request.file_id).first()
    if not data_file:
        raise HTTPException(status_code=404, detail="Data file not found")
    try:
        file_path = os.path.join(os.getcwd(), 'uploads', data_file.original_filename)
        if data_file.file_type == 'sav':
            spss = SPSSProcessor()
            spss.load_file(file_path)
            df = spss.data
        else:
            df = pd.read_csv(file_path)
        nlp = NLEngine()
        text_columns = [col for col in df.columns if df[col].dtype == object]
        if not text_columns:
            return {"summary": {}, "detailed_results": {}, "error": "No text columns found in data."}
        texts = df[text_columns[0]].dropna().astype(str).tolist()
        sentiment = nlp.analyze_sentiment(texts)
        return {"summary": {"average_sentiment": sentiment.get('average_sentiment')}, "detailed_results": sentiment}
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"NLP engine failed: {str(e)}") 