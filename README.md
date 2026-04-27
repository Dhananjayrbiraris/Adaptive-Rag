# Adaptive RAG - Agentic AI Chatbot

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.5.4-orange.svg)](https://python.langchain.com/langgraph/)
[![Qdrant](https://img.shields.io/badge/Qdrant-VectorDB-purple.svg)](https://qdrant.tech/)

## 📋 Overview

**Adaptive RAG** is an intelligent, end-to-end Retrieval-Augmented Generation (RAG) system powered by agentic AI architecture. It combines dynamic query routing, intelligent document retrieval, and advanced LLM capabilities to provide accurate, context-aware answers to user queries.

---

## 🏗️ Architecture

```text
Adaptive-Rag/
├── backend/                  # FastAPI Backend
│   ├── api/                  # API routes and endpoints
│   ├── config/               # Settings and Prompts
│   ├── database/             # MongoDB and Qdrant clients
│   ├── engine/               # Core RAG logic (Graph, Agents, Retriever)
│   ├── models/               # Pydantic schemas
│   ├── tools/                # Shared helper tools
│   └── main.py               # FastAPI entry point
├── frontend/                 # Streamlit Frontend
│   ├── pages/                # Multi-page app structure
│   ├── utils/                # API client
│   └── app.py                # Streamlit entry point
├── .env                      # Environment variables
├── requirements.txt          # Dependencies
└── README.md                 # Documentation
```

---

## 📖 Usage Guide

### 1. Prerequisites
- Python 3.9+
- MongoDB (Local or Atlas)
- Qdrant (Cloud or Local)
- OpenAI API Key
- Tavily API Key

### 2. Installation

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
QDRANT_URL=https://...
QDRANT_API_KEY=...
MONGODB_URL=mongodb+srv://...
MONGODB_DB_NAME=adaptive_rag
```

### 4. Running the Application

**Start FastAPI Backend:**
```bash
python -m uvicorn backend.main:app --reload
```

**Start Streamlit Frontend:**
```bash
streamlit run frontend/app.py
```

**Access the Application:**
- Web Interface: http://localhost:8501
- API Documentation: http://localhost:8000/docs
