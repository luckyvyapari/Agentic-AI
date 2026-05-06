from langchain_neo4j import Neo4jGraph
from app.core.config import settings

# Monkeypatch Neo4jGraph to skip APOC schema refresh if not available
from langchain_neo4j.graphs import neo4j_graph
neo4j_graph.Neo4jGraph.refresh_schema = lambda self: None

def verify():
    g = Neo4jGraph(
        url=settings.NEO4J_URI,
        username=settings.NEO4J_USERNAME,
        password=settings.NEO4J_PASSWORD,
        database=settings.NEO4J_DATABASE,
        enhanced_schema=False
    )
    print("--- Nodes ---")
    print(g.query('MATCH (n) RETURN labels(n) as label, n.id as id, n.text as text LIMIT 20'))
    print("--- Relationships ---")
    print(g.query('MATCH (s)-[r]->(t) RETURN labels(s) as s_label, s.id as s_id, type(r) as type, labels(t) as t_label, t.id as t_id LIMIT 20'))

if __name__ == "__main__":
    verify()
