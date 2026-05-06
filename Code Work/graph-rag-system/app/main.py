import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from graph_rag import GraphRAGSystem

app = FastAPI(title="GraphRAG Explorer")

# Initialize System
try:
    rag_system = GraphRAGSystem()
except Exception as e:
    print(f"Warning: Could not initialize GraphRAGSystem: {e}")
    rag_system = None

class QueryRequest(BaseModel):
    query: str

@app.post("/api/query")
async def handle_query(request: QueryRequest):
    if not rag_system:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    try:
        response = rag_system.query(request.query)
        # For simplicity, we'll return the mermaid graph as well
        graph_mermaid = rag_system.get_graph_as_mermaid()
        
        return {
            "answer": response.content,
            "graph": graph_mermaid
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ingest")
async def handle_ingest(request: QueryRequest):
    """Temporary endpoint to ingest raw text into the graph."""
    if not rag_system:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    try:
        rag_system.process_documents([request.query])
        return {"status": "success", "message": "Document ingested and graph updated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount Static Files
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
