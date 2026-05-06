import requests
import os

BASE_URL = "http://localhost:8001"
FILE_PATH = "/Volumes/SSD/tutorial/Full Stack Agentic AI Engineering /Code Work/Project1_GraphRAG_Enterprise/test_data.txt"

def test_live_ingestion():
    print("Testing Live Ingestion...")
    with open(FILE_PATH, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{BASE_URL}/ingest", files=files)
    
    print(f"Ingestion Response: {response.status_code}")
    print(response.json())

if __name__ == "__main__":
    test_live_ingestion()
