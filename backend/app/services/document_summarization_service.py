import os
import io
import pathlib
from google import genai
from google.genai import types
from typing import Union, BinaryIO
from dotenv import load_dotenv
import httpx
import tempfile
from urllib.parse import urlparse
import requests
from app.config import GEMINI_MODEL_NAME, SUPPORTED_DOCUMENT_TYPES, SUPPORTED_DOCUMENT_EXTENSIONS

# Load environment variables
load_dotenv()

class DocumentSummarizationService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Set the API key as environment variable for the client
        os.environ["GEMINI_API_KEY"] = self.api_key
        
        # Initialize Gemini client
        self.client = genai.Client()
        
    def summarize_document(self, file_data: bytes = None, file_url: str = None, mime_type: str = "application/pdf") -> str:
        """
        Summarize a document using Gemini API
        Supports both file upload and URL input
        """
        try:
            prompt = """Please provide a comprehensive summary of this document. Include:

**Document Overview:**
- Main topic and purpose of the document
- Type of document (research paper, report, article, etc.)
- Key themes and subjects covered

**Key Points:**
- Main arguments, findings, or conclusions
- Important data, statistics, or evidence presented
- Critical insights or recommendations

**Structure and Content:**
- How the document is organized
- Major sections or chapters
- Methodology (if applicable)

**Summary:**
- Concise overview of the entire document
- Most important takeaways
- Target audience and relevance

Please format your response with clear sections using markdown headers and provide a well-structured summary that captures the essence of the document."""

            if file_url:
                return self._summarize_from_url(file_url, prompt, mime_type)
            elif file_data:
                return self._summarize_from_bytes(file_data, prompt, mime_type)
            else:
                return "No document provided. Please upload a file or provide a URL."
                
        except Exception as e:
            print(f"Error summarizing document: {str(e)}")
            return f"I encountered an error while summarizing the document: {str(e)}. Please try again with a different document."
    
    def _summarize_from_url(self, url: str, prompt: str, mime_type: str) -> str:
        """
        Summarize document from URL
        """
        try:
            # Fetch document from URL
            response = httpx.get(url, timeout=30.0)
            response.raise_for_status()
            doc_data = response.content
            
            # For larger documents, use File API
            if len(doc_data) > 20 * 1024 * 1024:  # 20MB threshold
                return self._summarize_large_document_from_bytes(doc_data, prompt, mime_type)
            else:
                return self._summarize_from_bytes(doc_data, prompt, mime_type)
                
        except httpx.TimeoutException:
            return "The document URL took too long to respond. Please try again or use a different URL."
        except httpx.HTTPStatusError as e:
            return f"Could not access the document at the provided URL. HTTP Error: {e.response.status_code}"
        except Exception as e:
            return f"Error fetching document from URL: {str(e)}"
    
    def _summarize_from_bytes(self, doc_data: bytes, prompt: str, mime_type: str) -> str:
        """
        Summarize document from bytes data (for smaller files)
        """
        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL_NAME,
                contents=[
                    types.Part.from_bytes(
                        data=doc_data,
                        mime_type=mime_type,
                    ),
                    prompt
                ]
            )
            
            if response.text:
                return response.text.strip()
            else:
                return "I was able to process the document, but couldn't generate a summary. Please try uploading a different document."
                
        except Exception as e:
            print(f"Error in _summarize_from_bytes: {str(e)}")
            # If direct processing fails, try File API for larger documents
            return self._summarize_large_document_from_bytes(doc_data, prompt, mime_type)
    
    def _summarize_large_document_from_bytes(self, doc_data: bytes, prompt: str, mime_type: str) -> str:
        """
        Summarize large document using File API
        """
        try:
            # Create a BytesIO object for upload
            doc_io = io.BytesIO(doc_data)
            
            # Upload the document using File API
            uploaded_file = self.client.files.upload(
                file=doc_io,
                config=dict(mime_type=mime_type)
            )
            
            # Generate summary
            response = self.client.models.generate_content(
                model=GEMINI_MODEL_NAME,
                contents=[uploaded_file, prompt]
            )
            
            # Clean up the uploaded file
            try:
                self.client.files.delete(uploaded_file.name)
            except Exception as cleanup_error:
                print(f"Warning: Could not delete uploaded file: {cleanup_error}")
            
            if response.text:
                return response.text.strip()
            else:
                return "I was able to process the document, but couldn't generate a summary. Please try uploading a different document."
                
        except Exception as e:
            print(f"Error in _summarize_large_document_from_bytes: {str(e)}")
            return f"Error processing large document: {str(e)}"
    
    def get_supported_mime_types(self) -> list:
        """
        Get list of supported document MIME types
        """
        return SUPPORTED_DOCUMENT_TYPES
    
    def get_supported_file_extensions(self) -> list:
        """
        Get list of supported file extensions
        """
        return SUPPORTED_DOCUMENT_EXTENSIONS
    
    def detect_mime_type_from_filename(self, filename: str) -> str:
        """
        Detect MIME type from filename extension
        """
        extension = pathlib.Path(filename).suffix.lower()
        
        mime_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.html': 'text/html',
            '.htm': 'text/html',
            '.csv': 'text/csv',
            '.rtf': 'application/rtf'
        }
        
        return mime_types.get(extension, 'application/pdf')  # Default to PDF
