"""
ReAct agent setup for document retrieval and question answering.
"""

import os

from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

from backend.config.settings import prompt_config
from backend.engine.llms.openai import llm
from backend.engine.retriever_setup import get_retriever

config = prompt_config

# Load document description if available
if os.path.exists("description.txt"):
    with open("description.txt", "r", encoding="utf-8") as f:
        description = f.read()
else:
    description = None

# Create ReAct agent prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", config.prompt("system_prompt")),
    ("human", "{input}"),
    ("ai", "{agent_scratchpad}")
])


def get_agent_executor() -> AgentExecutor:
    """
    Build and return the ReAct AgentExecutor with a freshly-initialized retriever.
    Called lazily at query time instead of at module import to avoid blocking startup.
    """
    tools = [get_retriever()]
    react_agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=react_agent,
        tools=tools,
        handle_parsing_errors=True,
        max_iterations=2,
        verbose=True,
        return_intermediate_steps=True
    )
