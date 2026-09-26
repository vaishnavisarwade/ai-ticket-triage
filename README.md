# AI Ticket Triage

An AI agent that classifies customer support tickets, retrieves semantically similar past tickets, drafts a suggested response, and decides whether the ticket needs human review — built with LangGraph, FastAPI, React, and ChromaDB.

## What makes this different

Most GenAI demos retrieve and summarize. This agent makes an actual operational decision: escalate to a human, or auto-approve. It escalates when either **urgency is high** or **its own classification confidence is low** — meaning it recognizes uncertainty rather than always guessing confidently.

## How it works

1. **Classify** — an LLM (via Groq) reads the ticket and returns a category, urgency level, and confidence score
2. **Retrieve** — the ticket is embedded and matched against a vector database of past resolved tickets using semantic search (meaning-based, not keyword-based)
3. **Draft** — the LLM writes a suggested response using the classification and retrieved context
4. **Decide** — the agent escalates if urgency is High/Critical OR confidence is below 70%; otherwise it's auto-approved

## Tech stack

- **Backend**: Python, FastAPI, LangGraph, ChromaDB, Sentence-Transformers, Groq (LLM API), SQLite
- **Frontend**: React (Vite)

## Features

- Real-time ticket classification, retrieval, and drafting
- Confidence-based + urgency-based escalation logic
- Persistent ticket history with search, filter, and sort
- Look up any past ticket by ID
- Delete tickets from history

## Running locally

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```
Create a `.env` file inside `backend/` with:

GROQ_API_KEY=your_key_here

Then:
```bash
python build_vector_store.py   # one-time: embeds the dataset into ChromaDB
uvicorn main:api --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Notes on data quality

The dataset used (Kaggle's Customer Support Ticket Dataset) is synthetic. During evaluation, I found the dataset's own category labels frequently didn't match the actual ticket text — likely an artifact of how the data was generated. My classifier's predictions were often more textually justified than the ground-truth labels themselves. See `evaluate_classifier.py` and `manual_review.py` for the full investigation.

## Status

This is a working prototype demonstrating the core decision pipeline. It is not production-scale — a production version would add authentication, real ticket ingestion (email/chat), and actual response sending.