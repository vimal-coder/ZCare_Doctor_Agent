import fitz  # PyMuPDF
import io

class DocumentProcessor:
    @staticmethod
    def extract_text_from_pdf(file_bytes: bytes) -> str:
        """
        Extracts text from a PDF file using PyMuPDF, with token limit safeguards.
        """
        try:
            pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
            extracted_text = ""

            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                extracted_text += page.get_text("text") + "\n\n"

            pdf_document.close()
            
            if not extracted_text.strip():
                return "Error: No readable text found in the PDF. If this is a scanned image, OCR is required."
                
            # --- NEW SAFETY VALVE ---
            # 1 token is roughly 4 characters. 
            # To stay safely under the 12,000 token limit (leaving room for the system prompt), 
            # we limit the text to 35,000 characters (approx 8,750 tokens).
            MAX_CHARS = 35000 
            if len(extracted_text) > MAX_CHARS:
                print(f"Warning: Document exceeded {MAX_CHARS} characters. Truncating.")
                extracted_text = extracted_text[:MAX_CHARS] + "\n\n... [DOCUMENT TRUNCATED DUE TO API LIMITS] ..."
                
            return extracted_text

        except Exception as e:
            raise Exception(f"Failed to process PDF document: {str(e)}")