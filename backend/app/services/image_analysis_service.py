import os
from google import genai
from google.genai import types
from typing import List, Dict
from dotenv import load_dotenv
import base64
from app.config import GEMINI_MODEL_NAME, SUPPORTED_IMAGE_TYPES

# Load environment variables
load_dotenv()

class ImageAnalysisService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Set the API key as environment variable for the client
        os.environ["GEMINI_API_KEY"] = self.api_key
        
        # Initialize Gemini client
        self.client = genai.Client()
        
    def analyze_image(self, image_data: bytes, mime_type: str = "image/jpeg") -> str:
        """
        Analyze an image using Gemini Vision API
        """
        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL_NAME,
                contents=[
                    types.Part.from_bytes(
                        data=image_data,
                        mime_type=mime_type,
                    ),
                    """Please provide a detailed analysis of this image. Include:

**Image Description:**
- What is the main subject or focus of the image?
- Describe the setting, background, and overall composition

**Objects and Elements:**
- List and describe the key objects, people, or elements visible
- Note colors, textures, and visual characteristics

**Context and Details:**
- Any text visible in the image
- Actions or activities taking place
- Mood, atmosphere, or artistic style
- Technical aspects (lighting, perspective, etc.)

**Additional Insights:**
- Any interesting or notable features
- Potential use cases or context for this image

Please format your response with clear sections using markdown headers."""
                ]
            )
            
            if response.text:
                return response.text.strip()
            else:
                return "I was able to process the image, but couldn't generate a detailed description. Please try uploading a different image."
                
        except Exception as e:
            print(f"Error analyzing image: {str(e)}")
            return f"I encountered an error while analyzing the image: {str(e)}. Please try again with a different image."
    
    def get_supported_mime_types(self) -> List[str]:
        """
        Get list of supported image MIME types
        """
        return SUPPORTED_IMAGE_TYPES
