"""
AI Services Router
Handles AI chat functionality using Groq's LLaMA model for intelligent responses.
"""

import os  # For accessing environment variables
from dotenv import load_dotenv  # Loads environment variables from .env file
from fastapi import APIRouter, Depends  # Router for grouping related endpoints
# from openai import OpenAI  # Alternative: OpenAI client (currently commented out)
from groq import Groq  # Groq client for accessing LLaMA models
from utils.indexing import get_context_for_query  # RAG retrieval
from utils.ai_utils import model  # Embedding model for query encoding
from utils.auth_utils import get_current_user

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
def ai_chat(user_query: str, _ = Depends(get_current_user)):
    """
    Chat with AI assistant using Groq's LLaMA model with RAG.
    
    This endpoint:
    1. Retrieves relevant context from uploaded documents
    2. Sends user query + context to LLaMA model
    3. Returns intelligent, context-aware response
    
    Args:
        user_query (str): The question or text from the user
        
    Returns:
        str: AI-generated response based on user's documents
        
    Example:
        GET /ai/chat?user_query=What is this document about?
        Response: "Based on the document, it discusses..."
    """
    
    # Retrieve relevant context from uploaded documents
    context = get_context_for_query(user_query, model, top_k=3)
    
    # Construct enhanced prompt with context
    prompt = [
        {
            "role": "system",  # System message sets the AI's behavior
            "content": """
                You are a helpful assistant. 
                Your goal is to respond to people with clear and precise answers based on the user query.
                If user provided context, analyze that and respond carefully to the question. 
                Don't confuse the question and context provided by the user.
                If no relevant context is found, answer based on your general knowledge but mention that it's not from the uploaded documents.
                """
        },
        {
            "role": "user",  # User's question with context
            "content": f"{context}\n\nQuestion: {user_query}"
        }
    ]
    
    # Send prompt to Groq API and get response
    model_response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",  # Specify which LLaMA model to use
        messages=prompt  # Send the conversation history
    )

    # Extract and return the AI's text response
    return model_response.choices[0].message.content
