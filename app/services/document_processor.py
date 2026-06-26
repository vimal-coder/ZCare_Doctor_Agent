import fitz  # PyMuPDF
import io
import base64
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from app.core.config import GOOGLE_API_KEY, MODEL_ID

class DocumentProcessor:
    @staticmethod
    def extract_data_from_pdf(file_bytes: bytes) -> tuple[str, list]:
        """
        Extracts text and images from a PDF file using PyMuPDF, with token limit safeguards.
        """
        try:
            pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
            extracted_text = ""
            images = []

            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                extracted_text += page.get_text("text") + "\n\n"
                
                # Extract images from page
                for img_index, img in enumerate(page.get_images(full=True)):
                    xref = img[0]
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    # Cap images to avoid excessive token usage
                    if len(images) < 5:
                        images.append({
                            "mime_type": f"image/{image_ext}",
                            "data": base64.b64encode(image_bytes).decode("utf-8")
                        })

            pdf_document.close()
            
            if not extracted_text.strip():
                extracted_text = "Error: No readable text found in the PDF. If this is a scanned image, OCR is required."
                
            # --- NEW SAFETY VALVE ---
            # 1 token is roughly 4 characters. 
            # To stay safely under the 12,000 token limit (leaving room for the system prompt), 
            # we limit the text to 35,000 characters (approx 8,750 tokens).
            MAX_CHARS = 35000 
            if len(extracted_text) > MAX_CHARS:
                print(f"Warning: Document exceeded {MAX_CHARS} characters. Truncating.")
                extracted_text = extracted_text[:MAX_CHARS] + "\n\n... [DOCUMENT TRUNCATED DUE TO API LIMITS] ..."
                
            return extracted_text, images

        except Exception as e:
            raise Exception(f"Failed to process PDF document: {str(e)}")

    @staticmethod
    def extract_data_from_image(file_bytes: bytes, mime_type: str) -> tuple[str, list]:
        """
        Extracts text from an image using Google Gemini Vision capabilities. Returns the text and the image data.
        """
        try:
            # Initialize Gemini for vision tasks
            llm = ChatGoogleGenerativeAI(
                model=MODEL_ID,
                temperature=0.0,
                google_api_key=GOOGLE_API_KEY,
            )
            
            image_b64 = base64.b64encode(file_bytes).decode("utf-8")
            
            message = HumanMessage(
                content=[
                    {
                        "type": "text", 
                        "text": "Please extract all the readable text from this medical document image accurately. If there are tables, try to represent them clearly. If the image is not a document or contains no text, simply output 'No readable text found'."
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{image_b64}"}
                    }
                ]
            )
            
            response = llm.invoke([message])
            extracted_text = response.content
            
            if not extracted_text.strip() or "no readable text found" in extracted_text.lower():
                extracted_text = "Error: No readable text found in the image."
                
            return extracted_text, [{"mime_type": mime_type, "data": image_b64}]
            
        except Exception as e:
            raise Exception(f"Failed to process image document: {str(e)}")