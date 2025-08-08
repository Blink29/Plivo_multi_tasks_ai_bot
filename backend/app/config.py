"""
Configuration constants for the AI Playground application
"""

# Gemini API Configuration
GEMINI_MODEL_NAME = "models/gemini-2.5-flash"

# File size limits (in bytes)
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_DOCUMENT_SIZE = 50 * 1024 * 1024  # 50MB

# Supported file types
SUPPORTED_IMAGE_TYPES = [
    "image/jpeg",
    "image/jpg", 
    "image/png",
    "image/gif",
    "image/webp"
]

SUPPORTED_DOCUMENT_TYPES = [
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/html",
    "text/csv",
    "application/rtf"
]

SUPPORTED_DOCUMENT_EXTENSIONS = [
    ".pdf", 
    ".doc", 
    ".docx", 
    ".txt", 
    ".html", 
    ".csv", 
    ".rtf"
]

# Session configuration
SESSION_QUERY_LIMIT = 10
SESSION_TIMEOUT_HOURS = 24

# API Configuration
CORS_ORIGINS = ["http://localhost:5173"]
API_HOST = "0.0.0.0"
API_PORT = 8000
