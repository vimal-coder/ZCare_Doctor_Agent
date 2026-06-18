from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes import router
import os

# Initialize the FastAPI application
app = FastAPI(
    title="Medical AI Assistant API",
    description="Backend for the clinical decision support system.",
    version="1.0.0"
)

# Configure CORS to allow our frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, change this to your specific frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API routes we just created
app.include_router(router, prefix="/api")

# Mount the static files directory to serve HTML, CSS, and JS
# We use a try-except block just in case the folder hasn't been created yet
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_frontend():
    """Serves the main HTML file when users visit the root URL."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Backend is running. Frontend UI not yet created."}

# Run the application (used when running the file directly)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)