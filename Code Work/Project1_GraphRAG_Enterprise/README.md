# Project 1: Enterprise Knowledge Intelligence Agent (GraphRAG)

This project implements a state-of-the-art GraphRAG system for enterprise document intelligence.

## Features
- **Graph Ingestion**: Automatically extracts entities and relationships from PDFs/Text using LLMs and stores them in Neo4j.
- **Hybrid Retrieval**: Combines Neo4j Vector Index (semantic search) with multi-hop graph traversal (relational reasoning).
- **Explainable AI**: The UI shows both the answer and the graph path used to derive it.
- **Modern UI**: A premium, glassmorphism-based React interface.

## Prerequisites
- Neo4j instance (Local or Aura)
- Google Gemini API Key (or OpenAI)
- Python 3.9+
- Node.js & npm

## Setup

### Backend
1. `cd backend`
2. Create `.env` (see below)
3. `python -m venv venv`
4. `source venv/bin/activate`
5. `pip install -r requirements.txt`
6. `python main.py`

### Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev`

## Environment Variables (.env)
```env
MODEL_PROVIDER=google
GOOGLE_API_KEY=your_key
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=neo4j
```
