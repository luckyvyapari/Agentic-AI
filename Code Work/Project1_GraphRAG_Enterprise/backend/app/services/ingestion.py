import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_neo4j import Neo4jGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer
from app.core.config import settings

# Monkeypatch Neo4jGraph to skip APOC schema refresh if not available
from langchain_neo4j.graphs import neo4j_graph
neo4j_graph.Neo4jGraph.refresh_schema = lambda self: None

class IngestionService:
    def __init__(self):
        if settings.MOCK_MODE:
            self.graph = None
            print("Running in MOCK_MODE: No Neo4j connection.")
        else:
            self.graph = Neo4jGraph(
                url=settings.NEO4J_URI,
                username=settings.NEO4J_USERNAME,
                password=settings.NEO4J_PASSWORD,
                database=settings.NEO4J_DATABASE,
                enhanced_schema=False
            )

        if settings.MODEL_PROVIDER == "google":
            self.llm = ChatGoogleGenerativeAI(model=settings.LLM_MODEL, google_api_key=settings.GOOGLE_API_KEY)
            self.embeddings = GoogleGenerativeAIEmbeddings(model=settings.EMBEDDING_MODEL, google_api_key=settings.GOOGLE_API_KEY)
        elif settings.MODEL_PROVIDER == "ollama":
            self.llm = ChatOllama(model=settings.LLM_MODEL, base_url=settings.OLLAMA_BASE_URL)
            self.embeddings = OllamaEmbeddings(model=settings.EMBEDDING_MODEL, base_url=settings.OLLAMA_BASE_URL)
        else:
            self.llm = ChatOpenAI(model=settings.LLM_MODEL, api_key=settings.OPENAI_API_KEY)
            self.embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
            
        self.transformer = LLMGraphTransformer(llm=self.llm)

    def ingest_document(self, file_path: str):
        # 1. Load
        if file_path.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        else:
            loader = TextLoader(file_path)
            
        docs = loader.load()
        
        # 2. Split
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(docs)
        
        if settings.MOCK_MODE:
            print("MOCK: Ingesting documents...")
            return 10
        
        # 3. Transform to Graph
        graph_documents = self.transformer.convert_to_graph_documents(chunks)
        
        # 4. Custom Cypher Ingestion (Bypassing APOC)
        self.manual_add_graph_documents(graph_documents)
        
        # 5. Store source chunks for vector search
        self.store_chunks_for_vector(chunks)
        
        return len(graph_documents)

    def manual_add_graph_documents(self, graph_documents):
        """Manually ingests graph documents using Cypher to avoid APOC dependencies."""
        for gd in graph_documents:
            # Create Nodes
            for node in gd.nodes:
                label = node.type if node.type else "Entity"
                self.graph.query(f"""
                    MERGE (n:`{label}` {{id: $id}})
                    SET n += $properties
                """, {"id": node.id, "properties": node.properties or {}})
            
            # Create Relationships
            for rel in gd.relationships:
                source_label = rel.source.type if rel.source.type else "Entity"
                target_label = rel.target.type if rel.target.type else "Entity"
                rel_type = rel.type.replace(" ", "_").upper()
                
                self.graph.query(f"""
                    MATCH (s:`{source_label}` {{id: $source_id}})
                    MATCH (t:`{target_label}` {{id: $target_id}})
                    MERGE (s)-[r:`{rel_type}`]->(t)
                    SET r += $properties
                """, {
                    "source_id": rel.source.id,
                    "target_id": rel.target.id,
                    "properties": rel.properties or {}
                })

    def store_chunks_for_vector(self, chunks):
        """Stores text chunks as Document nodes for vector indexing."""
        for chunk in chunks:
            content = chunk.page_content
            # Note: We use a separate Document label for vector search
            # We also store the embedding manually if needed, but Neo4j can handle it
            self.graph.query("""
                CREATE (d:Document {text: $text})
            """, {"text": content})
        
        self.create_vector_index()

    def create_vector_index(self):
        try:
            self.graph.query("""
                CREATE VECTOR INDEX document_vector IF NOT EXISTS
                FOR (m:Document) ON (m.text)
                OPTIONS {indexConfig: {
                 `vector.dimensions`: 768,
                 `vector.similarity_function`: 'cosine'
                }}
            """)
        except Exception as e:
            print(f"Error creating index: {e}")

ingestion_service = IngestionService()
