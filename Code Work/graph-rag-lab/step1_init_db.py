import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Step 1: Load environment variables (URI, Username, Password)
load_dotenv()

# Configuration - Update these in your .env file or hardcode them here for the lab
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password") # Ensure this is your actual password
TARGET_DATABASE = "graphraglabdb" # The name of our new graph database

def initialize_database():
    """
    This script connects to the Neo4j 'system' database to create 
    a brand new user database for our GraphRAG project.
    """
    print(f"--- Connecting to Neo4j at {NEO4J_URI} ---")
    
    # We use the 'system' database because only it has the permission to CREATE other databases
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    try:
        with driver.session(database="system") as session:
            # 1. Check existing databases
            print("Checking existing databases...")
            result = session.run("SHOW DATABASES")
            existing_dbs = [record["name"] for record in result]
            
            if TARGET_DATABASE in existing_dbs:
                print(f"Database '{TARGET_DATABASE}' already exists. Skipping creation.")
            else:
                # 2. Create the new database (This is the equivalent of 'CREATE TABLE' in SQL)
                print(f"Creating new database: '{TARGET_DATABASE}'...")
                session.run(f"CREATE DATABASE {TARGET_DATABASE} IF NOT EXISTS")
                print(f"Success! Database '{TARGET_DATABASE}' is now being initialized.")

            # 3. Verify it is online
            print("\nDatabase Status:")
            result = session.run("SHOW DATABASES")
            for record in result:
                if record["name"] == TARGET_DATABASE:
                    print(f"-> {record['name']}: {record['currentStatus']}")

    except Exception as e:
        print(f"\n[ERROR] Could not initialize database: {e}")
        print("Please check if:")
        print("1. Neo4j is running.")
        print("2. Your NEO4J_PASSWORD in .env is correct.")
    
    finally:
        driver.close()
        print("\n--- Done ---")

if __name__ == "__main__":
    initialize_database()
