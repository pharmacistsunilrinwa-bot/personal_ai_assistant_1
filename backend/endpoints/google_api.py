from fastapi import APIRouter
from services.google_api_service import GoogleApiService

router = APIRouter()
google_service = GoogleApiService()

@router.get("/gmail")
def get_emails(limit: int = 10):
    return {"messages": google_service.get_gmail_messages(limit=limit)}

@router.get("/drive")
def get_drive_files(limit: int = 10):
    return {"files": google_service.get_drive_files(limit=limit)}

@router.get("/photos")
def get_photos(limit: int = 10):
    return {"photos": google_service.get_recent_photos(limit=limit)}
