import os
from fastapi import APIRouter, HTTPException
from api.get_metadata import DOWNLOADS_DIR

router = APIRouter()

@router.get("/view-directory/")
async def view_directory():
    if not os.path.exists(DOWNLOADS_DIR):
        return {"message": "Directory does not exist"}
    
    return {"directory": DOWNLOADS_DIR, "files": os.listdir(DOWNLOADS_DIR)}

@router.get("/view-file/{filename}")
async def view_file(filename: str):
    file_path = os.path.join(DOWNLOADS_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    if os.path.isdir(file_path):
        raise HTTPException(status_code=400, detail="Cannot read a directory")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return {"filename": filename, "content": file.read()}
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied. Try changing file permissions.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
