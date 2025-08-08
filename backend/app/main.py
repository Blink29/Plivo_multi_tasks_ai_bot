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

# Global instances
session_manager = SessionManager()
gemini_service = None
image_analysis_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global gemini_service, image_analysis_service
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
    allow_origins=["http://localhost:5173"],  # React dev server
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
        if image.size and image.size > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File size must be less than 10MB"
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

@app.get("/health")
async def health_check():
    gemini_status = "available" if gemini_service else "unavailable"
    image_analysis_status = "available" if image_analysis_service else "unavailable"
    return {
        "status": "healthy",
        "message": "AI Playground API is running",
        "services": {
            "gemini_service": gemini_status,
            "image_analysis_service": image_analysis_status
        },
        "active_sessions": len(session_manager.sessions)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
