"""
Retriever setup and vector store configuration.
"""

import os
import logging
from typing import Optional, TYPE_CHECKING

from langchain_core.documents import Document
from langchain_core.tools import create_retriever_tool
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from backend.config.settings import settings

logger = logging.getLogger(__name__)

# Initialize embeddings lazily to avoid API key issues at import time
_embeddings = None


def get_embeddings() -> OpenAIEmbeddings:
    """Get or create embeddings instance."""
    global _embeddings
    if _embeddings is None:
        _embeddings = OpenAIEmbeddings()
    return _embeddings


# Cache for Qdrant client to avoid reconnection
_qdrant_client = None
_vectorstore_cache = {}


def get_qdrant_client() -> QdrantClient:
    """Get or create cached Qdrant client."""
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
        )
        logger.info("Qdrant client initialized")
    return _qdrant_client


def retriever_chain(chunks: list[Document], collection_name: Optional[str] = None) -> bool:
    """
    Initialize and store documents in Qdrant vector database.

    Args:
        chunks: List of document chunks to store.
        collection_name: Optional collection name override.

    Returns:
        Boolean indicating success of the operation.
    """
    collection = collection_name or settings.CODE_COLLECTION
    
    try:
        client = get_qdrant_client()
        embeddings = get_embeddings()
        
        # Check if collection exists, create if not
        if not client.collection_exists(collection_name=collection):
            logger.info(f"Creating new collection: {collection}")
        
        vectorstore = QdrantVectorStore.from_documents(
            documents=chunks,
            embedding=embeddings,
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            collection_name=collection,
        )

        logger.info(f"Qdrant vector store initialized with {len(chunks)} document chunks in collection '{collection}'")
        return True
    except Exception as e:
        logger.error(f"Error storing documents in Qdrant: {e}", exc_info=True)
        return False


def get_retriever(collection_name: Optional[str] = None):
    """
    Get a retriever tool connected to the Qdrant vector store.

    Args:
        collection_name: Optional collection name override.

    Returns:
        A LangChain retriever tool configured for the vector store.

    Raises:
        Exception: If vector store initialization fails.
    """
    collection = collection_name or settings.CODE_COLLECTION
    
    try:
        client = get_qdrant_client()
        embeddings = get_embeddings()
        
        if not client.collection_exists(collection_name=collection):
            logger.warning(f"Collection '{collection}' does not exist. Initializing with a dummy document.")
            from langchain_core.documents import Document as LangChainDocument
            dummy_doc = LangChainDocument(
                page_content="No documents have been uploaded yet. Please upload a document first.",
                metadata={"source": "initialization"}
            )
            vectorstore = QdrantVectorStore.from_documents(
                documents=[dummy_doc],
                embedding=embeddings,
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
                collection_name=collection,
            )
        else:
            vectorstore = QdrantVectorStore(
                client=client,
                collection_name=collection,
                embedding=embeddings,
            )
        
        retriever = vectorstore.as_retriever()

        # Load document description from collection-specific file
        desc_filename = f"description_{collection}.txt"
        if os.path.exists(desc_filename):
            with open(desc_filename, "r", encoding="utf-8") as f:
                description = f.read()
            logger.info(f"Loaded description from {desc_filename}")
        else:
            description = "Uploaded documents"
            logger.warning(f"No description file found at {desc_filename}, using default")

        retriever_tool = create_retriever_tool(
            retriever,
            "retriever_customer_uploaded_documents",
            f"Use this tool **only** to answer questions about: {description}\n"
            "Don't use this tool to answer anything else."
        )

        return retriever_tool

    except Exception as e:
        logger.error(f"Error initializing retriever: {e}", exc_info=True)
        raise Exception(f"Retriever initialization failed: {str(e)}")
