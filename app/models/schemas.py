
from pydantic import BaseModel
from typing import List, Optional

# Schema for the user's interactive chat queries
class ChatRequest(BaseModel):
    session_id: str
    message: str

# Schema for clearing the session
class ClearRequest(BaseModel):
    session_id: str

# Schema for the structured data we want the AI to extract from the PDF
class ExtractedMedicalInfo(BaseModel):
    diagnoses: List[str] = []
    medications: List[str] = []
    laboratory_results: List[str] = []
    medical_conditions: List[str] = []
    allergies: List[str] = []
    other_clinical_findings: List[str] = []

# Schema for the final API response to the frontend
class ChatResponse(BaseModel):
    response: str