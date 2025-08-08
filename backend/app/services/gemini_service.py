import os
from google import genai
from typing import List, Dict
from dotenv import load_dotenv
from app.config import GEMINI_MODEL_NAME

# Load environment variables
load_dotenv()

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Set the API key as environment variable for the client
        os.environ["GEMINI_API_KEY"] = self.api_key
        
        # Initialize Gemini client
        self.client = genai.Client()
        
    def generate_response(self, message: str, conversation_history: List[Dict] = None) -> str:
        """
        Generate a response using Gemini API with conversation context
        """
        try:
            # Build the prompt with conversation history for context
            prompt = self._build_prompt_with_context(message, conversation_history)
            
            # Generate response using the new API
            response = self.client.models.generate_content(
                model=GEMINI_MODEL_NAME,
                contents=prompt
            )
            
            if response.text:
                return response.text.strip()
            else:
                return "I apologize, but I couldn't generate a response. Please try rephrasing your question."
                
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return f"I'm experiencing some technical difficulties. Please try again in a moment. (Error: {str(e)})"
    
    def _build_prompt_with_context(self, current_message: str, conversation_history: List[Dict] = None) -> str:
        """
        Build a prompt that includes conversation context for better responses
        """
        base_prompt = """You are AskMe Bot, a helpful AI assistant. Answer like you're a knowledgeable and friendly assistant. 

IMPORTANT FORMATTING GUIDELINES:
- Use proper markdown formatting for better readability
- For mathematical expressions, use LaTeX notation with $ for inline math and $$ for display math
- Use **bold** for important terms and concepts
- Use ### for section headings
- Use numbered lists (1. 2. 3.) or bullet points (-) for better organization
- Use `code` formatting for technical terms or variables
- Keep your answers well-structured and easy to read

Provide clear, accurate, and helpful responses."""
        
        if not conversation_history:
            return f"{base_prompt}\n\nUser: {current_message}"
        
        # Build conversation context
        context = f"{base_prompt}\n\nPrevious conversation context:\n"
        
        # Add last few exchanges for context (limit to avoid token limits)
        recent_history = conversation_history[-6:]  # Last 3 exchanges (user + bot)
        
        for entry in recent_history:
            if entry['isUser']:
                context += f"User: {entry['text']}\n"
            else:
                context += f"Assistant: {entry['text']}\n"
        
        context += f"\nCurrent question:\nUser: {current_message}"
        
        return context
