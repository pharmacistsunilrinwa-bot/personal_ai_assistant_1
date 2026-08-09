from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from services.sentiment_service import SentimentService

router = APIRouter()
sentiment_service = SentimentService()

class SentimentRequest(BaseModel):
    text: str

class BatchSentimentRequest(BaseModel):
    texts: List[str]

@router.post("/analyze")
def analyze_sentiment(req: SentimentRequest):
    """Analyzes a single text string and returns polarity, subjectivity, and label."""
    try:
        result = sentiment_service.analyze_sentiment(req.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch")
def batch_analyze_sentiment(req: BatchSentimentRequest):
    """Analyzes a batch of text strings and returns a brief summary for each."""
    try:
        results = sentiment_service.batch_analyze(req.texts)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
