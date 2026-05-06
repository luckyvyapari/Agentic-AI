from neo4j import GraphDatabase
from app.core.config import settings

class Neo4jService:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI, 
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
        )

    def close(self):
        self.driver.close()

    def query(self, cypher, parameters=None):
        with self.driver.session(database=settings.NEO4J_DATABASE) as session:
            result = session.run(cypher, parameters)
            return [record.data() for record in result]

    def execute(self, cypher, parameters=None):
        with self.driver.session(database=settings.NEO4J_DATABASE) as session:
            session.run(cypher, parameters)

neo4j_service = Neo4jService()
