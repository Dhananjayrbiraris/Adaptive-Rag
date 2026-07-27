"""
API routes for RAG operations.
"""

import logging
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Header, HTTPException, Query
from langchain_core.messages import HumanMessage, AIMessage

from backend.database.chat_history import ChatHistory
from backend.models.query_request import QueryRequest
from backend.engine.document_upload import documents
from backend.engine.graph_builder import builder

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/rag/query")
async def rag_query(req: QueryRequest):
    """
    Process a RAG query and return the result.

    Args:
        req: The query request containing query text and session_id.

    Returns:
        The generated response from the RAG pipeline.
        
    Raises:
        HTTPException: If query processing fails.
    """
    try:
        chat_history = ChatHistory.get_session_history(req.session_id)
        await chat_history.add_message(HumanMessage(content=req.query))

        # Fetch full history
        messages = await chat_history.get_messages()
        
        if not messages:
            logger.warning(f"No messages found for session {req.session_id}")
            raise HTTPException(status_code=400, detail="Failed to retrieve chat history")
        
        result = await builder.ainvoke({
            "messages": messages
        })
        
        if not result or "messages" not in result or len(result["messages"]) == 0:
            logger.error("Empty result from graph builder")
            raise HTTPException(status_code=500, detail="Failed to generate response")
        
        output_text = result["messages"][-1].content

        # Save assistant message
        await chat_history.add_message(AIMessage(content=output_text))
        
        logger.info(f"Successfully processed query for session {req.session_id}")

        return {"result": result["messages"][-1]}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing RAG query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@router.post("/rag/documents/upload")
async def upload_file(
    file: UploadFile = File(...),
    description: str = Header(..., alias="X-Description"),
    collection_name: Optional[str] = Query(None, description="Optional collection name override")
):
    """
    Upload a document for RAG processing.

    Args:
        file: The file to upload (PDF or TXT).
        description: Document description provided via header.
        collection_name: Optional collection name to override default.

    Returns:
        Upload status.
        
    Raises:
        HTTPException: If file validation or upload fails.
    """
    # Validate file type
    allowed_extensions = {".pdf", ".txt"}
    file_ext = file.filename.lower().split('.')[-1] if file.filename else ""
    
    if f".{file_ext}" not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size (max 10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Reset file pointer for processing
    from io import BytesIO
    file.file = BytesIO(file_content)
    file.filename = file.filename or "uploaded_file"
    
    try:
        status_upload = documents(description, file, collection_name)
        if status_upload:
            logger.info(f"Successfully uploaded document: {file.filename}")
            return {"status": "success", "filename": file.filename}
        else:
            logger.error(f"Document upload failed: {file.filename}")
            raise HTTPException(status_code=500, detail="Document processing failed")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

