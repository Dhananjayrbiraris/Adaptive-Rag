"""
Home page — auto-redirects to the Chat page.
"""

import uuid

import streamlit as st

st.set_page_config(page_title="LangGraph Chat")

# Auto-generate a session ID if one doesn't exist
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())

# Go straight to chat
st.switch_page("pages/chat.py")
