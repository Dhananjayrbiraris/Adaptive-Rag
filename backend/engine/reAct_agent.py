"""
ReAct agent setup for document retrieval and question answering.
"""

import os
import logging

from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent

from backend.config.settings import prompt_config
from backend.engine.llms.openai import get_llm
from backend.engine.retriever_setup import get_retriever

logger = logging.getLogger(__name__)
config = prompt_config

# Load document description if available
if os.path.exists("description_codebase.txt"):
    with open("description_codebase.txt", "r", encoding="utf-8") as f:
        description = f.read()
else:
    description = None

# Create ReAct agent prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", config.prompt("system_prompt")),
    ("human", "{input}"),
    ("ai", "{agent_scratchpad}")
])


def get_agent_executor():
    """
    Build and return the ReAct AgentExecutor with a freshly-initialized retriever.
    Called lazily at query time instead of at module import to avoid blocking startup.
    """
    try:
        llm = get_llm()
        tools = [get_retriever()]
        react_agent = create_react_agent(llm, tools, prompt)
        return react_agent
    except Exception as e:
        logger.error(f"Error creating agent executor: {e}", exc_info=True)
        raise
