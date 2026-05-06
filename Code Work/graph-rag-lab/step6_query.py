import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_neo4j import Neo4jVector
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

def run_hybrid_query(question):
    print(f"--- Querying: {question} ---")
    
    # 1. Initialize LLM and Embeddings
    llm = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3.2"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    )
    embeddings = OllamaEmbeddings(
        model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    )

    # 2. Setup Vector Retriever (Finds semantic matches)
    # This searches the 'Document' nodes we created in Step 5.
    vector_store = Neo4jVector.from_existing_index(
        embeddings,
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
        database="graphraglabdb",
        index_name="vector_index",
    )
    vector_retriever = vector_store.as_retriever()

    # 3. Define the Prompt
    # We tell the AI to use the hybrid context we've built.
    template = """
    Answer the question based ONLY on the following context.
    The context contains both raw text and extracted relationships.
    
    Context:
    {context}
    
    Question: {question}
    Answer:
    """
    prompt = ChatPromptTemplate.from_template(template)

    # 4. Build the Chain (LCEL)
    chain = (
        {"context": vector_retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
    )

    # 5. Execute
    response = chain.invoke(question)
    print(f"\nAI Response:\n{response.content}")

if __name__ == "__main__":
    # Test Question based on our complex docs
    # Standard RAG might struggle with 'Which bank' if the text is split, 
    # but GraphRAG sees the relationship clearly.
    test_question = "Which bank issued the payment for Lucy Fopco and what is the contract ID?"
    run_hybrid_query(test_question)
