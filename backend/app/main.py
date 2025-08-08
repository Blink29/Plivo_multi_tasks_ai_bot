from fastapi import FastAPI, HTTPException, Header, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import Optional
import asyncio
from contextlib import asynccontextmanager

from app.services.gemini_service import GeminiService
from app.services.session_manager import SessionManager
from app.services.image_analysis_service import ImageAnalysisService
from app.services.document_summarization_service import DocumentSummarizationService
from app.config import CORS_ORIGINS, API_HOST, API_PORT, MAX_IMAGE_SIZE, MAX_DOCUMENT_SIZE

# Global instances
session_manager = SessionManager()
gemini_service = None
image_analysis_service = None
document_summarization_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global gemini_service, image_analysis_service, document_summarization_service
    try:
        gemini_service = GeminiService()
        print("✅ Gemini service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Gemini service: {e}")
        print("💡 Make sure to add your GEMINI_API_KEY to the .env file")
    
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
    
    # Start background task for session cleanup
    cleanup_task = asyncio.create_task(cleanup_sessions_periodically())
    
    yield
    
    # Shutdown
    cleanup_task.cancel()

async def cleanup_sessions_periodically():
    """Background task to cleanup expired sessions"""
    while True:
        try:
            cleaned = session_manager.cleanup_expired_sessions()
            if cleaned > 0:
                print(f"🧹 Cleaned up {cleaned} expired sessions")
            await asyncio.sleep(300)  # Cleanup every 5 minutes
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Error in session cleanup: {e}")
            await asyncio.sleep(300)

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

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    remaining_queries: int

class SessionResponse(BaseModel):
    session_id: str
    remaining_queries: int

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
        "message": "AskMe Bot API is running!",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat",
            "new_session": "/api/session/new",
            "health": "/health"
        }
    }

@app.post("/api/session/new", response_model=SessionResponse)
async def create_new_session():
    """Create a new chat session"""
    session_id = session_manager.create_session()
    remaining_queries = session_manager.get_remaining_queries(session_id)
    
    return SessionResponse(
        session_id=session_id,
        remaining_queries=remaining_queries
    )

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    Chat endpoint with Gemini API integration and session management
    """
    try:
        if not gemini_service:
            raise HTTPException(
                status_code=503, 
                detail="Gemini service not available. Please check API key configuration."
            )
        
        # Get or create session
        session_id = request.session_id
        if not session_id or not session_manager.get_session(session_id):
            session_id = session_manager.create_session()
        
        # Check if session can make more queries
        if not session_manager.can_make_query(session_id):
            raise HTTPException(
                status_code=429,
                detail="Query limit reached for this session. Please start a new session."
            )
        
        user_message = request.message.strip()
        if not user_message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Add user message to session
        session_manager.add_message_to_session(session_id, user_message, is_user=True)
        
        # Get conversation history for context
        conversation_history = session_manager.get_conversation_history(session_id)
        
        # Generate response with Gemini
        bot_response = gemini_service.generate_response(
            message=user_message,
            conversation_history=conversation_history[:-1]  # Exclude the current message
        )
        
        # Add bot response to session
        session_manager.add_message_to_session(session_id, bot_response, is_user=False)
        
        # Get remaining queries
        remaining_queries = session_manager.get_remaining_queries(session_id)
        
        return ChatResponse(
            response=bot_response,
            session_id=session_id,
            remaining_queries=remaining_queries
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/api/session/{session_id}/history")
async def get_session_history(session_id: str):
    """Get conversation history for a session"""
    history = session_manager.get_conversation_history(session_id)
    remaining_queries = session_manager.get_remaining_queries(session_id)
    
    return {
        "session_id": session_id,
        "history": history,
        "remaining_queries": remaining_queries
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
    gemini_status = "available" if gemini_service else "unavailable"
    image_analysis_status = "available" if image_analysis_service else "unavailable"
    document_summarization_status = "available" if document_summarization_service else "unavailable"
    return {
        "status": "healthy",
        "message": "AI Playground API is running",
        "services": {
            "gemini_service": gemini_status,
            "image_analysis_service": image_analysis_status,
            "document_summarization_service": document_summarization_status
        },
        "active_sessions": len(session_manager.sessions)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
