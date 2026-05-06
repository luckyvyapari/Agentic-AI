import os
from dotenv import load_dotenv
from step1_init_db import initialize_database
from step4_graph_store import store_in_neo4j
from step5_vector_index import create_vector_index

def run_complete_pipeline():
    """
    Master Script: Runs the entire GraphRAG pipeline from start to finish.
    """
    print("🚀 STARTING COMPLETE GRAPHRAG PIPELINE 🚀\n")
    
    # 1. Init Database
    initialize_database()
    
    # 2. Build Graph (Steps 2, 3, 4 are bundled in store_in_neo4j)
    store_in_neo4j()
    
    # 3. Build Vector Index
    create_vector_index()
    
    print("\n✅ GRAPHRAG SYSTEM IS FULLY CONSTRUCTED ✅")
    print("You can now query your graph using the Hybrid Retriever.")

if __name__ == "__main__":
    run_complete_pipeline()
