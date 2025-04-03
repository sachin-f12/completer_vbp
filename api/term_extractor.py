from utils.api_caller import ApiCaller
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, APIRouter
from pydantic import BaseModel
from typing import Optional
import json
from fastapi.responses import JSONResponse

router = APIRouter()
api_caller = ApiCaller()

class SurgicalDeviceRequest(BaseModel):
    device_name: str
    technique: str

class DiagnosticRequest(BaseModel):
    test_name: str
    technique: str
    sample_type: str
    diagnostic_type: str

def clean_json_response(raw_response):
    """Clean API response by removing <json> tags and ensuring valid JSON format."""
    if isinstance(raw_response, str):  # Ensure it's a string before processing
        raw_response = raw_response.replace("<json>\n", "").replace("\n</json>", "")
        try:
            return json.loads(raw_response)  # Convert cleaned string to dict
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Invalid JSON format received from API.")
    return raw_response  # If already a dict, return as is

@router.post("/analyze/surgical-device/")
async def analyze_surgical_device(
    file: UploadFile = File(...), 
    device_name: str = Form(...), 
    technique: str = Form(...)
):
    if not device_name or not technique:
        raise HTTPException(status_code=400, detail="Device name and technique are required.")
    
    result = api_caller.analyze_surgical_device(file, device_name, technique)
    cleaned_result = clean_json_response(result)
    
    return JSONResponse(content=cleaned_result)

@router.post("/analyze/diagnostic/")
async def analyze_diagnostic(
    file: UploadFile = File(...),
    test_name: str = Form(...),
    technique: str = Form(...),
    sample_type: str = Form(...),
    diagnostic_type: str = Form(...)
):
    if not test_name or not technique or not sample_type or not diagnostic_type:
        raise HTTPException(status_code=400, detail="All fields are required.")
    
    result = api_caller.analyze_diagnostic(file, test_name, technique, sample_type, diagnostic_type)
    cleaned_result = clean_json_response(result)
    
    return JSONResponse(content=cleaned_result)
