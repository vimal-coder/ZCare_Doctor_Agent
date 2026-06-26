# ZCare Doctor Agent (Medical AI Assistant)

ZCare Doctor Agent is an advanced clinical decision support system designed for healthcare professionals. It provides a secure, locally-hosted web interface where doctors can upload patient medical reports (PDFs), instantly extract structured clinical data, and interactively chat with a specialized AI assistant about the patient's medical context.

## 🚀 Features

- **Document Processing**: Upload clinical PDF reports with drag-and-drop support.
- **Automated Information Extraction**: Utilizes PyMuPDF and Google's Generative AI to automatically parse and extract structured data from medical documents, including:
  - Diagnoses
  - Medications
  - Medical Conditions
  - Allergies
  - Laboratory Results
- **Interactive AI Clinical Assistant**: A chat interface powered by a LangGraph workflow that allows doctors to ask complex questions, explore treatment options, and analyze symptoms based strictly on the uploaded patient context.
- **Quick Action Queries**: Pre-configured, one-click prompts for common clinical inquiries (e.g., Treatment Options, Drug Interactions, Lifestyle Advice).
- **Modern User Interface**: A clean, responsive, full-screen UI built with pure HTML/CSS/JS.

## 🛠️ Technology Stack

- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) with Uvicorn
- **AI & Orchestration**: 
  - [LangChain](https://python.langchain.com/) & [LangGraph](https://python.langchain.com/docs/langgraph)
  - Google Generative AI (`gemini-2.5-flash`)
- **Document Parsing**: [PyMuPDF](https://pymupdf.readthedocs.io/)
- **Data Validation**: [Pydantic](https://docs.pydantic.dev/)
- **Frontend**: Vanilla HTML5, CSS3 (CSS Variables, Grid/Flexbox), JavaScript

## 📁 Project Structure

```
ZCare_Doctor_Agent/
├── app/
│   ├── api/                 # FastAPI routes (upload, chat endpoints)
│   ├── core/                # Configuration and environment setup
│   ├── models/              # Pydantic schemas for data validation
│   └── services/            # Business logic (AI Agent, Document Processor)
├── static/                  # Frontend assets
│   ├── css/style.css        # UI styling
│   ├── js/script.js         # Frontend logic and API integration
│   └── index.html           # Main application interface
├── main.py                  # Application entry point
├── config.ini               # Model configuration parameters
├── .env                     # API keys and secrets
├── pyproject.toml           # Project metadata and dependencies
└── requirements.txt         # Python package dependencies
```

## ⚙️ Setup and Installation

### Prerequisites
Ensure you have [`uv`](https://docs.astral.sh/uv/) installed. You can install it using:

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

1. **Clone the repository** (if applicable) or navigate to the project directory:
   ```bash
   cd ZCare_Doctor_Agent
   ```

2. **Initialize the Project** (if setting up from scratch):
   ```bash
   uv init
   ```

3. **Install Dependencies**:
   This project uses [`uv`](https://docs.astral.sh/uv/) as the package manager. To create a virtual environment and install all dependencies automatically from `pyproject.toml`, run:
   ```bash
   uv sync
   ```

   *Alternatively, if you prefer installing from `requirements.txt` using `uv`, run:*
   ```bash
   # Create a virtual environment
   uv venv
   
   # Activate it (Windows)
   .venv\Scripts\activate
   # Activate it (macOS/Linux)
   source .venv/bin/activate
   
   # Install requirements
   uv add  -r requirements.txt
   ```

3. **Environment Variables**:
   Ensure you have a `.env` file in the root directory containing your Google API key:
   ```env
   GOOGLE_API_KEY="your_api_key_here"
   ```

4. **Configuration**:
   You can tweak the LLM parameters in `config.ini`:
   ```ini
   [MODEL]
   MODEL_ID = gemini-2.5-flash
   TEMPERATURE = 0.0
   MAX_TOKENS = 8192
   ```

## 🏃‍♂️ Running the Application

Start the FastAPI backend server using Uvicorn (via `uv run`):

```bash
uv run uvicorn main:app --reload
```

Or run the main script directly:

```bash
uv run python main.py
```

Once the server is running, open your web browser and navigate to:
**http://localhost:8000**

## ⚠️ Disclaimer
This AI tool is designed for **clinical support only** and is not a replacement for professional medical judgment, diagnosis, or treatment. Healthcare professionals should always verify the AI-generated insights against their own medical expertise.