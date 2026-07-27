"""
Document upload and processing module.
"""

import os
import tempfile
import logging
from typing import Optional

from fastapi import UploadFile, HTTPException
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.engine.retriever_setup import retriever_chain
from backend.tools.common_tools import enhance_description_with_llm
from backend.config.settings import settings

logger = logging.getLogger(__name__)


def documents(description: str, file: UploadFile, collection_name: Optional[str] = None) -> bool:
    """
    Process and upload a document for RAG.

    Validates file type, loads content, enhances description, chunks documents,
    and stores them in the vector database.

    Args:
        description: User-provided document description.
        file: The uploaded file (PDF or TXT).
        collection_name: Optional collection name override.

    Returns:
        Boolean indicating success of the upload process.

    Raises:
        HTTPException: If file type is not supported or loading fails.
    """
    filename = file.filename
    logger.info(f"Processing document: {filename}")
    
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    if not filename.endswith(".pdf") and not filename.endswith(".txt"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported"
        )

    file_bytes = file.file.read()

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=os.path.splitext(filename)[1]
    ) as tmp_file:
        tmp_file.write(file_bytes)
        tmp_path = tmp_file.name

    try:
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(tmp_path)
        else:
            loader = TextLoader(tmp_path, encoding="utf-8")

        docs = loader.load()
        logger.info(f"Loaded {len(docs)} documents from {filename}")
    except Exception as e:
        logger.error(f"Error loading file {filename}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error loading file: {str(e)}"
        )
    finally:
        os.unlink(tmp_path)

    # Enhance description using LLM
    try:
        description_llm = enhance_description_with_llm(description)
        logger.info("Description enhanced successfully")
    except Exception as e:
        logger.warning(f"Failed to enhance description: {e}, using original")
        description_llm = description

    # Save enhanced description to a unique file per session/collection
    desc_filename = f"description_{collection_name or settings.CODE_COLLECTION}.txt"
    try:
        with open(desc_filename, "w", encoding="utf-8") as f:
            f.write(description_llm)
        logger.info(f"Saved enhanced description to {desc_filename}")
    except Exception as e:
        logger.error(f"Failed to save description: {e}")

    # Split documents into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )
    chunks = splitter.split_documents(docs)
    logger.info(f"Split documents into {len(chunks)} chunks")

    return retriever_chain(chunks, collection_name)




