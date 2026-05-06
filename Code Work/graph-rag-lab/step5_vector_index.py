import os
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings
from langchain_neo4j import Neo4jVector
from step2_processing import process_complex_documents

load_dotenv()

def create_vector_index():
    """
    Step 5: Indexing Document nodes for similarity search.
    """
    print("--- Step 5: Vector Indexing ---")
    
    # 1. Initialize Embeddings
    embeddings = OllamaEmbeddings(
        model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    )

    # 2. Get Chunks
    chunks = process_complex_documents()

    # 3. Create the Vector Store inside Neo4j
    # We store the raw text and the embedding vectors inside the 'Document' nodes.
    print("Creating Vector Index inside Neo4j...")
    vector_index = Neo4jVector.from_documents(
        chunks,
        embeddings,
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
        database="graphraglabdb",
        index_name="vector_index",
        node_label="Document", # Only index the source documents
        pre_delete_collection=True # Clean start
    )
    
    print("Vector Indexing Complete. Your GraphRAG is now hybrid-ready!")

if __name__ == "__main__":
    create_vector_index()
