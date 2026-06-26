from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List
from app.models.schemas import ChatRequest, ChatResponse, ClearRequest
from app.services.document_processor import DocumentProcessor
from app.services.ai_agent import ai_agent_instance
import uuid

# Create the router
router = APIRouter()

# In-memory storage for user sessions (In a production app, use a database like Redis)
sessions = {}

@router.post("/upload")
async def upload_medical_reports(files: List[UploadFile] = File(...)):
    """Handles multiple PDF and image uploads, extracts text, and stores the medical context."""
    all_raw_text = []
    all_images = []
    
    for file in files:
        filename_lower = file.filename.lower()
        if not (filename_lower.endswith('.pdf') or filename_lower.endswith(('.png', '.jpg', '.jpeg'))):
            raise HTTPException(status_code=400, detail=f"Only PDF and Image (PNG, JPG, JPEG) files are supported. Found: {file.filename}")
        
        try:
            # 1. Read the uploaded file
            file_bytes = await file.read()
            
            # 2. Extract raw text and images based on file type
            if filename_lower.endswith('.pdf'):
                raw_text, extracted_images = DocumentProcessor.extract_data_from_pdf(file_bytes)
            else:
                mime_type = "image/png" if filename_lower.endswith('.png') else "image/jpeg"
                raw_text, extracted_images = DocumentProcessor.extract_data_from_image(file_bytes, mime_type)
                
            all_raw_text.append(f"--- Document: {file.filename} ---\n{raw_text}")
            all_images.extend(extracted_images)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing {file.filename}: {str(e)}")
            
    # Combine the extracted text from all documents
    combined_raw_text = "\n\n=== NEXT DOCUMENT ===\n\n".join(all_raw_text)
    
    try:
        # 3. Use the AI Agent to extract structured medical information
        structured_info = ai_agent_instance.extract_structured_info(combined_raw_text)
        
        # 4. Format the extracted data into a readable context string
        medical_context = f"""
        Report Type: {structured_info.report_type if structured_info.report_type else 'Not specified'}
        Diagnoses: {', '.join(structured_info.diagnoses) if structured_info.diagnoses else 'None noted'}
        Medications: {', '.join(structured_info.medications) if structured_info.medications else 'None noted'}
        Laboratory Results: {', '.join(structured_info.laboratory_results) if structured_info.laboratory_results else 'None noted'}
        Conditions: {', '.join(structured_info.medical_conditions) if structured_info.medical_conditions else 'None noted'}
        Allergies: {', '.join(structured_info.allergies) if structured_info.allergies else 'None noted'}
        Other Findings: {', '.join(structured_info.other_clinical_findings) if structured_info.other_clinical_findings else 'None noted'}
        """
        
        # 5. Create a unique session ID for this user's context
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            "medical_context": medical_context,
            "images": all_images
        }
        
        return {
            "message": "Documents processed successfully.",
            "session_id": session_id,
            "extracted_data": structured_info.dict()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    """Handles interactive chat queries using the stored medical context."""
    # Retrieve the patient context using the session ID
    session_data = sessions.get(request.session_id)
    
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found. Please upload a medical report first.")
    
    try:
        # Pass the query, the context, and any images to our LangGraph agent
        ai_response = ai_agent_instance.chat(
            user_message=request.message,
            medical_context=session_data["medical_context"],
            images=session_data.get("images", [])
        )
        
        return ChatResponse(response=ai_response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI processing failed: {str(e)}")

@router.post("/clear")
async def clear_session(request: ClearRequest):
    """Clears the session data."""
    if request.session_id in sessions:
        del sessions[request.session_id]
    return {"message": "Session cleared"}