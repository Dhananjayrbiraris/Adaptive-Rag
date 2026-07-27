"""
OpenAI LLM initialization and configuration.
"""

import logging
from langchain_openai import ChatOpenAI
from backend.config.settings import settings

logger = logging.getLogger(__name__)

# Initialize LLM lazily to avoid API key issues at import time
_llm = None


def get_llm() -> ChatOpenAI:
    """Get or create the OpenAI LLM instance."""
    global _llm
    if _llm is None:
        if not settings.OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY is not configured")
            raise ValueError("OPENAI_API_KEY environment variable is required")
        _llm = ChatOpenAI(model="gpt-4o", api_key=settings.OPENAI_API_KEY)
        logger.info("OpenAI LLM initialized")
    return _llm


# For backward compatibility, provide llm as a property-like accessor
class _LLMWrapper:
    """Wrapper to provide lazy loading of LLM for backward compatibility."""
    
    def __getattr__(self, name):
        llm = get_llm()
        return getattr(llm, name)
    
    def __call__(self, *args, **kwargs):
        llm = get_llm()
        return llm(*args, **kwargs)


llm = _LLMWrapper()