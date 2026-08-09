from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Any, Optional
from services.pattern_recognition_service import PatternRecognitionService

router = APIRouter()
logic_engine = PatternRecognitionService()

class ReasoningRequest(BaseModel):
    prompt: str
    custom_system_instruction: Optional[str] = None

class SequenceRequest(BaseModel):
    sequence: List[Any]

@router.post("/reason")
async def solve_reasoning_problem(req: ReasoningRequest):
    """Solves logical reasoning or pattern puzzles using highly-structured Gemini System Instructions."""
    try:
        response = await logic_engine.solve_logic_problem(
            prompt=req.prompt,
            custom_instruction=req.custom_system_instruction
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sequence")
async def analyze_sequence(req: SequenceRequest):
    """Specifically analyzes sequences of values to find underlying mathematical or logical patterns."""
    try:
        result = await logic_engine.detect_sequence_pattern(req.sequence)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
