"""
Generic Services Router
Handles file upload and parsing for text and PDF documents.
"""

import traceback  # For printing detailed error messages during debugging
from fastapi import APIRouter, UploadFile, status  # FastAPI components for file handling
from fastapi.responses import JSONResponse  # For custom JSON responses
from utils.parser import pdf_parsing  # Custom function to extract text from PDFs

# ========================================
# Router Configuration
# ========================================
router = APIRouter(
    prefix="/genric",  # Note: Consider renaming to "/generic" (typo in original)
    tags=["Genric"]  # Groups endpoints in API documentation
)


# ========================================
# File Upload Endpoint
# ========================================
@router.post("/upload_file")
async def upload_file_api(
    file: UploadFile  # FastAPI automatically handles multipart/form-data file uploads
):
    """
    Upload and parse text or PDF files.
    
    This endpoint accepts file uploads and extracts their text content.
    Supported formats: .txt (text files) and .pdf (PDF documents)
    
    Args:
        file (UploadFile): The uploaded file from the client
        
    Returns:
        JSONResponse: Contains extracted text or error message
        
    Status Codes:
        200: File successfully parsed
        412: Unsupported file type (not text or PDF)
        500: Internal server error during processing
        
    Example:
        POST /genric/upload_file
        Body: form-data with file field
        Response: { "content": "extracted text here..." }
    """
    try:
        # Log the file type for debugging
        print(file.content_type)
        
        # Handle text files (.txt)
        if file.content_type == "text/plain":
            text_content = file.file.read()  # Read raw bytes from file
            parsed_data = text_content.decode()  # Convert bytes to string
            
        # Handle PDF files (.pdf)
        elif file.content_type == "application/pdf":
            parsed_data = pdf_parsing(file.file)  # Use custom PDF parser
            
        # Reject unsupported file types
        else:
            return JSONResponse(
                status_code=status.HTTP_412_PRECONDITION_FAILED,  # 412: Precondition Failed
                content="Sorry! Upload only text or pdf files."
            )
        
        # Return extracted text with success status
        return JSONResponse(
            content=parsed_data,
            status_code=status.HTTP_200_OK  # 200: Success
        )
        
    except:
        # Log full error traceback for debugging
        traceback.print_exc()
        
        # Return generic error message to client
        return JSONResponse(
            content="Something went wrong...",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR  # 500: Internal Server Error
        )
