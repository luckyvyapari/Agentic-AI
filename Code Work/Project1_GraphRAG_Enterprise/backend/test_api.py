import requests
import time
import os

BASE_URL = "http://localhost:8001"


def test_ingestion():
    print("Testing Ingestion...")
    file_path = "../test_data.txt"
    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{BASE_URL}/ingest", files=files)
    
    print(f"Ingestion Response: {response.status_code}")
    print(response.json())
    return response.status_code == 200

def test_query(query):
    print(f"Testing Query: {query}")
    response = requests.post(f"{BASE_URL}/query", json={"query": query})
    print(f"Query Response: {response.status_code}")
    print(response.json())
    return response.json()

if __name__ == "__main__":
    # Give the server time to start
    print("Waiting for server to start...")
    time.sleep(5)
    
    if test_ingestion():
        time.sleep(2) # Wait for Neo4j to index
        test_query("Who is the CEO of Acme Corp and where is it located?")
        test_query("Who reports to Bob?")
    else:
        print("Ingestion failed, skipping queries.")
