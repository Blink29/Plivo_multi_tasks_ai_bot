"""
Configuration constants for the AI Playground application
"""
import os

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
# Development CORS origins
DEV_CORS_ORIGINS = ["http://localhost:5173"]

# Production CORS origins (add your Vercel domain)
PROD_CORS_ORIGINS = [
    "https://plivo-multi-tasks-ai-bot.vercel.app",  # Your main Vercel domain
    "https://plivo-multi-tasks-ai-j967msym8-blink29s-projects.vercel.app",  # Your deployment URL
    "https://*.vercel.app"  # Wildcard for all Vercel subdomains
]

# Determine environment and set CORS origins
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
CORS_ORIGINS = PROD_CORS_ORIGINS if ENVIRONMENT == "production" else DEV_CORS_ORIGINS

API_HOST = "0.0.0.0"
API_PORT = int(os.getenv("PORT", 8000))  # Use PORT from environment or default to 8000
