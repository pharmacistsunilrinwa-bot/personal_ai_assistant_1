from fastapi import APIRouter, UploadFile, File, Form
from services.gemini_service import GeminiService
from pydantic import BaseModel

router = APIRouter()
gemini = GeminiService()

class ChatRequest(BaseModel):
    message: str
    context: str = None

@router.post("/chat")
async def chat(request: ChatRequest):
    response = await gemini.generate_content(request.message, request.context)
    return {"response": response}

@router.post("/stt")
async def speech_to_text(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    text = await gemini.speech_to_text(audio_bytes)
    return {"text": text}

@router.post("/tts")
async def text_to_speech(text: str = Form(...)):
    audio_data = await gemini.text_to_speech(text)
    return {"audio": audio_data}
