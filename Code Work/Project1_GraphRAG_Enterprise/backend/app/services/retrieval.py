from langchain_neo4j import Neo4jGraph
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_ollama import OllamaEmbeddings, ChatOllama
from app.core.config import settings

# Monkeypatch Neo4jGraph to skip APOC schema refresh if not available
from langchain_neo4j.graphs import neo4j_graph
neo4j_graph.Neo4jGraph.refresh_schema = lambda self: None

class RetrievalService:
    def __init__(self):
        if settings.MOCK_MODE:
            self.graph = None
        else:
            self.graph = Neo4jGraph(
                url=settings.NEO4J_URI,
                username=settings.NEO4J_USERNAME,
                password=settings.NEO4J_PASSWORD,
                database=settings.NEO4J_DATABASE,
                enhanced_schema=False
            )
        
        if settings.MODEL_PROVIDER == "google":
            self.embeddings = GoogleGenerativeAIEmbeddings(model=settings.EMBEDDING_MODEL, google_api_key=settings.GOOGLE_API_KEY)
            self.llm = ChatGoogleGenerativeAI(model=settings.LLM_MODEL, google_api_key=settings.GOOGLE_API_KEY)
        elif settings.MODEL_PROVIDER == "ollama":
            self.embeddings = OllamaEmbeddings(model=settings.EMBEDDING_MODEL, base_url=settings.OLLAMA_BASE_URL)
            self.llm = ChatOllama(model=settings.LLM_MODEL, base_url=settings.OLLAMA_BASE_URL)
        else:
            self.embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
            self.llm = ChatOpenAI(model=settings.LLM_MODEL, api_key=settings.OPENAI_API_KEY)

    def hybrid_search(self, query: str, top_k=5):
        if settings.MOCK_MODE:
            return {
                "vector_context": ["Mock vector result about " + query],
                "graph_context": ["MOCK_NODE -[:RELATED_TO]-> MOCK_VALUE"],
                "full_context": "Mock Context for " + query
            }
            
        # 1. Try Vector Search
        vector_context = []
        try:
            query_vector = self.embeddings.embed_query(query)
            vector_results = self.graph.query("""
                CALL db.index.vector.queryNodes('document_vector', $top_k, $vector)
                YIELD node, score
                RETURN node.text AS text, score, id(node) AS node_id
            """, {"top_k": top_k, "vector": query_vector})
            vector_context = [r['text'] for r in vector_results]
        except Exception as e:
            print(f"Vector search failed or index empty: {e}")
            # Fallback to keyword search
            kw_results = self.graph.query("""
                MATCH (d:Document)
                WHERE d.text CONTAINS $query
                RETURN d.text AS text
                LIMIT 5
            """, {"query": query.split()[-1]}) # Simple fallback
            vector_context = [r['text'] for r in kw_results]

        # 2. Graph Traversal (The "Intelligence" part)
        # We'll try to find entities mentioned in the query
        graph_context = []
        # Simple entity extraction: look for capitalized words
        potential_entities = [word.strip('?') for word in query.split() if word[0].isupper()]
        
        for entity in potential_entities:
            # Multi-hop traversal: find what this entity is related to, and what those are related to
            traversal_results = self.graph.query("""
                MATCH (n {id: $entity_id})-[r1]-(m)-[r2]-(p)
                RETURN n.id + ' ' + type(r1) + ' ' + m.id + ' AND ' + m.id + ' ' + type(r2) + ' ' + p.id AS path
                LIMIT 10
            """, {"entity_id": entity})
            graph_context.extend([r['path'] for r in traversal_results])
            
            # Also get 1-hop if 2-hop is empty
            if not traversal_results:
                one_hop = self.graph.query("""
                    MATCH (n {id: $entity_id})-[r]-(m)
                    RETURN n.id + ' ' + type(r) + ' ' + m.id AS path
                    LIMIT 10
                """, {"entity_id": entity})
                graph_context.extend([r['path'] for r in one_hop])

        return {
            "vector_context": vector_context,
            "graph_context": list(set(graph_context)),
            "full_context": "Document Chunks:\n" + "\n".join(vector_context) + "\n\nGraph Relationships:\n" + "\n".join(list(set(graph_context)))
        }

    def generate_answer(self, query: str):
        context = self.hybrid_search(query)
        
        prompt = f"""
        You are an Enterprise Knowledge Assistant. Use the following context to answer the user's question.
        
        Context:
        {context['full_context']}
        
        Question: {query}
        
        Instructions:
        1. Be precise. If the answer is "New York City", say it and explain why (e.g. Bob works for Acme, which is in NYC).
        2. If the answer is not in the context, say you don't know.
        3. Explain the reasoning path using the graph relationships provided.
        
        Answer:
        """
        
        response = self.llm.invoke(prompt)
        return {
            "answer": response.content,
            "sources": context['vector_context'],
            "graph_path": context['graph_context']
        }

retrieval_service = RetrievalService()
