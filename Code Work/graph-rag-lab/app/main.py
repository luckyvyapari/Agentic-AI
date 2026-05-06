import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_neo4j import Neo4jVector, Neo4jGraph
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

app = FastAPI(title="GraphRAG Lab Explorer")

class QueryRequest(BaseModel):
    query: str

@app.post("/api/query")
async def handle_query(request: QueryRequest):
    try:
        llm = ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "llama3.2"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        )
        embeddings = OllamaEmbeddings(
            model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        )

        vector_store = Neo4jVector.from_existing_index(
            embeddings,
            url=os.getenv("NEO4J_URI"),
            username=os.getenv("NEO4J_USERNAME"),
            password=os.getenv("NEO4J_PASSWORD"),
            database="graphraglabdb",
            index_name="vector_index",
        )
        
        template = """
        Answer the question based only on the following context.
        Context:
        {context}
        
        Question: {question}
        Answer:
        """
        prompt = ChatPromptTemplate.from_template(template)
        chain = (
            {"context": vector_store.as_retriever(), "question": RunnablePassthrough()}
            | prompt
            | llm
        )
        
        response = chain.invoke(request.query)
        return {"answer": response.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_status():
    """Returns the current state of the Neo4j Graph."""
    try:
        graph = Neo4jGraph(
            url=os.getenv("NEO4J_URI"),
            username=os.getenv("NEO4J_USERNAME"),
            password=os.getenv("NEO4J_PASSWORD"),
            database="graphraglabdb",
            refresh_schema=False
        )
        # Count nodes
        res = graph.query("MATCH (n) RETURN count(n) as count")
        return {"node_count": res[0]['count']}
    except Exception as e:
        return {"node_count": 0, "error": str(e)}

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
