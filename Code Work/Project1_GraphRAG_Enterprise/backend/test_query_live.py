import requests

BASE_URL = "http://localhost:8001"

def test_live_query():
    print("Testing Live Query...")
    query = "Bob work in which city"
    response = requests.post(f"{BASE_URL}/query", json={"query": query})
    
    print(f"Query Response: {response.status_code}")
    print(response.json())

if __name__ == "__main__":
    test_live_query()
