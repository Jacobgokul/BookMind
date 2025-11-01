"""
AI Services Router
Handles AI chat functionality using Groq's LLaMA model for intelligent responses.
"""

import os  # For accessing environment variables
from dotenv import load_dotenv  # Loads environment variables from .env file
from fastapi import APIRouter  # Router for grouping related endpoints
# from openai import OpenAI  # Alternative: OpenAI client (currently commented out)
from groq import Groq  # Groq client for accessing LLaMA models

# ========================================
# Router Configuration
# ========================================
router = APIRouter(
    prefix="/ai",  # All endpoints in this router start with /ai
    tags=["AI Service"]  # Groups endpoints in API documentation
)

# ========================================
# API Key Setup
# ========================================
load_dotenv()  # Load environment variables from .env file

# Option 1: OpenAI (currently commented out)
# openai_api_key = os.getenv("openai_key")
# openai_client = OpenAI(api_key=openai_api_key)

# Option 2: Groq (currently active)
groq_api_key = os.getenv("groq_api_key")  # Get API key from environment
groq_client = Groq(api_key=groq_api_key)  # Initialize Groq client


# ========================================
# AI Chat Endpoint
# ========================================
@router.get("/chat")
def ai_chat(user_query: str):
    """
    Chat with AI assistant using Groq's LLaMA model.
    
    This endpoint sends user queries to the LLaMA AI model and returns intelligent responses.
    The system prompt defines the AI's behavior and personality.
    
    Args:
        user_query (str): The question or text from the user
        
    Returns:
        str: AI-generated response to the user's query
        
    Example:
        GET /ai/chat?user_query=What is FastAPI?
        Response: "FastAPI is a modern Python web framework..."
    """
    
    # Construct the conversation with system and user roles
    # System role: Defines how the AI should behave
    # User role: The actual question from the user
    prompt = [
        {
            "role": "system",  # System message sets the AI's behavior
            "content": """
                You are a helpfull assitant. 
                Your goal is to respond people with clear and precise answer based on the user query.
                If user provided context analysis that and respond carefully to the question. Don't confuse the question and context provided by the user
                """
        },
        {
            "role": "user",  # User's actual question
            "content": user_query
        }
    ]
    
    # Send prompt to Groq API and get response
    model_response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",  # Specify which LLaMA model to use
        messages=prompt  # Send the conversation history
    )

    # Extract and return the AI's text response
    return model_response.choices[0].message.content
