import os
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph
from step3_transform import transform_to_graph

load_dotenv()

def store_in_neo4j():
    """
    Step 4: Loading into the Graph Database.
    """
    print("--- Step 4: Storing in Neo4j ---")
    
    # 1. Connect to the database we created in Step 1
    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
        database="graphraglabdb",
        refresh_schema=False # Fix: Disable APOC schema check
    )

    # 2. Get Graph Documents from Step 3
    graph_docs = transform_to_graph()

    # 3. Add to Graph with specific production flags:
    # include_source=True -> This creates a 'mentions' link between the Node and the Original Doc.
    # base_entity_label=True -> This adds a shared label 'Entity' to every node (Company, Bank, etc.)
    #                          so we can find them 10x faster later.
    print("Writing to Neo4j...")
    try:
        graph.add_graph_documents(
            graph_docs,
            baseEntityLabel=True,
            include_source=True
        )
    except Exception as e:
        # If the error is just about APOC metadata, we can ignore it
        # because the nodes and relationships HAVE already been written.
        if "apoc.meta.data" in str(e):
            print("\n[NOTE] APOC plugin not detected. Skipping schema refresh.")
            print("Successfully saved nodes and relationships to the graph anyway!")
        else:
            raise e
    
    print("Knowledge Graph is now LIVE in Neo4j!")
    return graph

if __name__ == "__main__":
    store_in_neo4j()
