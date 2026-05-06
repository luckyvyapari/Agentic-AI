import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_experimental.graph_transformers import LLMGraphTransformer
from step2_processing import process_complex_documents

load_dotenv()

def transform_to_graph():
    """
    Step 3: The LLM Brain.
    Converts text chunks into Graph Documents (Nodes and Relationships).
    """
    print("--- Step 3: LLM Graph Transformation ---")
    
    # 1. Initialize our local Brain (Ollama)
    # We use llama3.2 because it is fast and smart at identifying entities.
    llm = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3.2"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    )

    # 2. Setup the Transformer
    # This is the built-in LangChain function that does the magic.
    # It doesn't need a manual schema; it figures it out itself!
    transformer = LLMGraphTransformer(llm=llm)

    # 3. Process Chunks from Step 2
    chunks = process_complex_documents()
    
    print("AI is extracting entities and relationships... (This takes a moment)")
    graph_documents = transformer.convert_to_graph_documents(chunks)
    
    # 4. Preview the AI's logic
    print(f"AI extracted {len(graph_documents)} graph-structured objects.")
    for g_doc in graph_documents:
        print(f"Nodes found: {[n.id for n in g_doc.nodes]}")
        print(f"Relationships: {[r.type for r in g_doc.relationships]}")
    
    return graph_documents

if __name__ == "__main__":
    transform_to_graph()
