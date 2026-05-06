from graph_rag import GraphRAGSystem

def run_demo():
    print("--- Initializing GraphRAG System ---")
    system = GraphRAGSystem()
    
    # Complex document from transcript
    complex_docs = [
        """MedFreeze Medical Affairs Instruction: 
        1. Administer Med-X 500mg at T+25 minutes. 
        2. Return email to medical.affairs@medfreeze.com if adverse reactions occur.
        3. Transaction ID: TX-9982. Amount: $4,500.00. 
        4. Relationship: MedFreeze is the primary supplier for City Hospital.""",
        
        """City Hospital Procurement Note:
        Contact: Dr. Aris. 
        Approved Med-X 500mg purchase under contract CF-2026. 
        MedFreeze is authorized to deliver directly to the pharmacy."""
    ]
    
    print("\n--- Processing Documents (Graph Transformation) ---")
    # Uncomment to actually run (requires Neo4j and OpenAI Key)
    # system.process_documents(complex_docs)
    
    print("\n--- Running Hybrid Query ---")
    question = "What is the instruction for Med-X administration and which hospital is involved?"
    # response = system.query(question)
    # print(f"Question: {question}")
    # print(f"Answer: {response.content}")

    print("\nNote: To run this demo, ensure you have set your OPENAI_API_KEY and NEO4J credentials in a .env file.")

if __name__ == "__main__":
    run_demo()
