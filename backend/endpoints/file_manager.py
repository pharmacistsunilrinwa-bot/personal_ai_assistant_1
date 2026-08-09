from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from services.file_manager_service import FileManagerService

router = APIRouter()
file_manager = FileManagerService()

class FileWriteRequest(BaseModel):
    path: str
    content: str

class FileTransferRequest(BaseModel):
    source_path: str
    dest_path: str

@router.get("/list")
def list_directory(path: str = Query(".", description="Directory path relative to sandbox base")):
    """Securely lists contents of a sandbox directory."""
    try:
        items = file_manager.list_directory(path)
        return {"items": items}
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except NotADirectoryError as nde:
        raise HTTPException(status_code=400, detail=str(nde))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/read")
def read_file(path: str = Query(..., description="File path relative to sandbox base")):
    """Securely reads the content of a text file inside sandbox."""
    try:
        content = file_manager.read_text_file(path)
        return {"content": content}
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=404, detail=str(fnf))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/write")
def write_file(req: FileWriteRequest):
    """Securely writes text content to a file inside sandbox, creating folders if missing."""
    try:
        saved_path = file_manager.write_text_file(req.path, req.content)
        return {"status": "success", "saved_path": saved_path}
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/copy")
def copy_item(req: FileTransferRequest):
    """Securely copies a file or folder inside sandbox."""
    try:
        dest = file_manager.copy_item(req.source_path, req.dest_path)
        return {"status": "success", "destination": dest}
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=404, detail=str(fnf))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/move")
def move_item(req: FileTransferRequest):
    """Securely moves a file or folder inside sandbox."""
    try:
        dest = file_manager.move_item(req.source_path, req.dest_path)
        return {"status": "success", "destination": dest}
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=404, detail=str(fnf))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete")
def delete_item(path: str = Query(..., description="File or folder path relative to sandbox base")):
    """Securely deletes a file or recursive directory inside sandbox."""
    try:
        result = file_manager.delete_item(path)
        return result
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=404, detail=str(fnf))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
