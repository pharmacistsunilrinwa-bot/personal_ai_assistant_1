from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from services.google_workspace_service import GoogleWorkspaceService
from config import Config

router = APIRouter()
workspace_service = GoogleWorkspaceService()

class SendEmailRequest(BaseModel):
    to: str
    subject: str
    body: str

class UploadFileRequest(BaseModel):
    file_path: str
    mime_type: str = 'application/octet-stream'
    folder_id: str = None

@router.get("/auth-url")
def get_auth_url(redirect_uri: str = None):
    """Generates the authorization URL for Google OAuth 2.0."""
    try:
        # Fallback to configured redirect URI if none provided
        r_uri = redirect_uri or Config.GOOGLE_REDIRECT_URI
        url = workspace_service.get_authorization_url(r_uri)
        return {"authorization_url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/oauth2callback")
def oauth2callback(code: str, redirect_uri: str = None):
    """Handles OAuth 2.0 redirect callback, exchanges authorization code for tokens."""
    try:
        r_uri = redirect_uri or Config.GOOGLE_REDIRECT_URI
        workspace_service.fetch_token_from_code(code, r_uri)
        return {"status": "success", "message": "Successfully authenticated with Google Workspace!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
def get_auth_status():
    """Checks if the service is currently authenticated."""
    return {"authenticated": workspace_service.is_authenticated()}

@router.get("/emails")
def list_emails(limit: int = 10, q: str = Query(None, description="Gmail query format e.g. 'from:boss'")):
    """Retrieves metadata of recent emails."""
    try:
        emails = workspace_service.list_emails(max_results=limit, query=q)
        return {"emails": emails}
    except ValueError as ve:
        raise HTTPException(status_code=401, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/email/send")
def send_email(req: SendEmailRequest):
    """Sends an email using authenticated user's account."""
    try:
        result = workspace_service.send_email(to=req.to, subject=req.subject, body=req.body)
        return {"status": "success", "message_id": result.get("id")}
    except ValueError as ve:
        raise HTTPException(status_code=401, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files")
def list_drive_files(limit: int = 10, q: str = Query(None, description="Drive query format e.g. 'name contains \"Project\"'")):
    """Lists files available in Google Drive."""
    try:
        files = workspace_service.list_drive_files(max_results=limit, query=q)
        return {"files": files}
    except ValueError as ve:
        raise HTTPException(status_code=401, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/file/upload")
def upload_drive_file(req: UploadFileRequest):
    """Uploads a local file to the Google Drive."""
    try:
        result = workspace_service.upload_drive_file(
            file_path=req.file_path,
            mime_type=req.mime_type,
            folder_id=req.folder_id
        )
        return {"status": "success", "file": result}
    except ValueError as ve:
        raise HTTPException(status_code=401, detail=str(ve))
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=404, detail=str(fnf))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
