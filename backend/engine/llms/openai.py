"""
OpenAI LLM initialization and configuration.
"""

from langchain_openai import ChatOpenAI
from backend.config.settings import settings

llm = ChatOpenAI(model="gpt-4o", api_key=settings.OPENAI_API_KEY)