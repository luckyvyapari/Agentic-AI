from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

passwords = ["password", "neo4j", "admin", "12345678"]
uri = "bolt://localhost:7687"
user = "neo4j"

def test_connections():
    for pw in passwords:
        print(f"Testing password: {pw}...")
        try:
            driver = GraphDatabase.driver(uri, auth=(user, pw))
            driver.verify_connectivity()
            print(f"SUCCESS! Password is: {pw}")
            driver.close()
            return pw
        except Exception as e:
            print(f"Failed: {e}")
    return None

if __name__ == "__main__":
    test_connections()
