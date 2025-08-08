from fastapi import FastAPI, HTTPException, Header, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import Optional
import asyncio
from contextlib import asynccontextmanager

from app.services.image_analysis_service import ImageAnalysisService
from app.services.document_summarization_service import DocumentSummarizationService
from app.config import CORS_ORIGINS, API_HOST, API_PORT, MAX_IMAGE_SIZE, MAX_DOCUMENT_SIZE

# Global instances
image_analysis_service = None
document_summarization_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global image_analysis_service, document_summarization_service
    
    try:
        image_analysis_service = ImageAnalysisService()
        print("✅ Image analysis service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Image analysis service: {e}")
    
    try:
        document_summarization_service = DocumentSummarizationService()
        print("✅ Document summarization service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Document summarization service: {e}")
    
    yield
    
    # Shutdown (no cleanup needed without session manager)

app = FastAPI(
    title="AI Playground API", 
    version="1.0.0",
    description="Multi-modal AI capabilities including image analysis, conversation processing, and document summarization",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ImageAnalysisResponse(BaseModel):
    analysis: str
    filename: str
    file_size: int

class DocumentSummarizationResponse(BaseModel):
    summary: str
    filename: Optional[str] = None
    url: Optional[str] = None
    file_size: Optional[int] = None

class URLSummarizationRequest(BaseModel):
    url: str

@app.get("/")
async def root():
    return {
        "message": "AI Playground API is running!",
        "version": "1.0.0",
        "endpoints": {
            "image_analysis": "/api/analyze-image",
            "document_summarization": "/api/summarize-document",
            "document_url_summarization": "/api/summarize-document-url",
            "health": "/health"
        }
    }

@app.post("/api/analyze-image", response_model=ImageAnalysisResponse)
async def analyze_image(image: UploadFile = File(...)):
    """
    Analyze an uploaded image using Gemini Vision API
    """
    try:
        if not image_analysis_service:
            raise HTTPException(
                status_code=503,
                detail="Image analysis service not available. Please check configuration."
            )
        
        # Validate file type
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image"
            )
        
        # Validate file size (max 10MB)
        if image.size and image.size > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size must be less than {MAX_IMAGE_SIZE // (1024*1024)}MB"
            )
        
        # Read image data
        image_data = await image.read()
        
        if not image_data:
            raise HTTPException(
                status_code=400,
                detail="Empty file received"
            )
        
        # Analyze image
        analysis = image_analysis_service.analyze_image(
            image_data=image_data,
            mime_type=image.content_type
        )
        
        return ImageAnalysisResponse(
            analysis=analysis,
            filename=image.filename or "unknown",
            file_size=len(image_data)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Image analysis error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing image: {str(e)}"
        )

@app.post("/api/summarize-document", response_model=DocumentSummarizationResponse)
async def summarize_document(document: UploadFile = File(...)):
    """
    Summarize an uploaded document using Gemini API
    """
    try:
        if not document_summarization_service:
            raise HTTPException(
                status_code=503,
                detail="Document summarization service not available. Please check configuration."
            )
        
        # Validate file type
        supported_extensions = document_summarization_service.get_supported_file_extensions()
        file_extension = '.' + document.filename.split('.')[-1].lower() if document.filename else ''
        
        if file_extension not in supported_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported formats: {', '.join(supported_extensions)}"
            )
        
        # Validate file size (max 50MB)
        if document.size and document.size > MAX_DOCUMENT_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size must be less than {MAX_DOCUMENT_SIZE // (1024*1024)}MB"
            )
        
        # Read document data
        document_data = await document.read()
        
        if not document_data:
            raise HTTPException(
                status_code=400,
                detail="Empty file received"
            )
        
        # Detect MIME type
        mime_type = document_summarization_service.detect_mime_type_from_filename(document.filename or "")
        
        # Summarize document
        summary = document_summarization_service.summarize_document(
            file_data=document_data,
            mime_type=mime_type
        )
        
        return DocumentSummarizationResponse(
            summary=summary,
            filename=document.filename or "unknown",
            file_size=len(document_data)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Document summarization error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error summarizing document: {str(e)}"
        )

@app.post("/api/summarize-document-url", response_model=DocumentSummarizationResponse)
async def summarize_document_url(request: URLSummarizationRequest):
    """
    Summarize a document from URL using Gemini API
    """
    try:
        if not document_summarization_service:
            raise HTTPException(
                status_code=503,
                detail="Document summarization service not available. Please check configuration."
            )
        
        # Basic URL validation
        if not request.url.strip():
            raise HTTPException(
                status_code=400,
                detail="URL is required"
            )
        
        # Detect MIME type from URL
        mime_type = document_summarization_service.detect_mime_type_from_filename(request.url)
        
        # Summarize document from URL
        summary = document_summarization_service.summarize_document(
            file_url=request.url.strip(),
            mime_type=mime_type
        )
        
        return DocumentSummarizationResponse(
            summary=summary,
            url=request.url.strip()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"URL summarization error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error summarizing document from URL: {str(e)}"
        )

@app.get("/health")
async def health_check():
    image_analysis_status = "available" if image_analysis_service else "unavailable"
    document_summarization_status = "available" if document_summarization_service else "unavailable"
    return {
        "status": "healthy",
        "message": "AI Playground API is running",
        "services": {
            "image_analysis_service": image_analysis_status,
            "document_summarization_service": document_summarization_status
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
