import os
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph, Neo4jVector
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
from langchain_text_splitters import TokenTextSplitter
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableParallel
from langchain_core.prompts import ChatPromptTemplate
from neo4j import GraphDatabase

class GraphRAGSystem:
    def __init__(self):
        load_dotenv()
        self.provider = os.getenv("MODEL_PROVIDER", "ollama").lower()
        
        # 1. Initialize LLM and Embeddings based on provider
        if self.provider == "openai":
            from langchain_openai import ChatOpenAI, OpenAIEmbeddings
            self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        else:
            from langchain_ollama import ChatOllama, OllamaEmbeddings
            self.llm = ChatOllama(
                model=os.getenv("OLLAMA_MODEL", "llama3.2"),
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            )
            self.embeddings = OllamaEmbeddings(
                model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            )
            
        self.url = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.username = os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.database = os.getenv("NEO4J_DATABASE", "neo4j")

        # 3. Ensure Database Exists (as per transcript)
        self._ensure_database()
        
        # 4. Initialize Graph Instance
        self.graph = Neo4jGraph(
            url=self.url,
            username=self.username,
            password=self.password,
            database=self.database
        )

    def _ensure_database(self):
        """Creates the database if it does not exist using a system driver."""
        driver = GraphDatabase.driver(self.url, auth=(self.username, self.password))
        with driver.session(database="system") as session:
            # Check if database exists
            result = session.run("SHOW DATABASES")
            databases = [record["name"] for record in result]
            if self.database not in databases:
                print(f"Creating database {self.database}...")
                session.run(f"CREATE DATABASE {self.database} IF NOT EXISTS")
        driver.close()

    def process_documents(self, raw_documents: list[str]):
        """Converts raw text into chunks and then into Graph Nodes/Relations."""
        # 1. Chunking
        text_splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=24)
        docs = [Document(page_content=txt) for txt in raw_documents]
        chunks = text_splitter.split_documents(docs)
        
        # 2. Graph Transformation (The 'Magic' line from transcript)
        print("Transforming documents into graph format...")
        transformer = LLMGraphTransformer(llm=self.llm)
        graph_docs = transformer.convert_to_graph_documents(chunks)
        
        # 3. Load into Neo4j
        print(f"Loading {len(graph_docs)} graph documents into Neo4j...")
        self.graph.add_graph_documents(
            graph_docs, 
            base_entity_label=True, # secondary label 'Entity' for faster retrieval
            include_source=True     # link nodes back to source documents
        )
        
        # 4. Create Vector Index within Neo4j
        print("Creating vector index on Document nodes...")
        Neo4jVector.from_documents(
            chunks,
            self.embeddings,
            url=self.url,
            username=self.username,
            password=self.password,
            database=self.database,
            index_name="vector_index",
            node_label="Document",
            pre_delete_collection=True # Refresh for demo
        )
        
        self.graph.refresh_schema()
        print("Indexing complete.")

    def get_retriever_chain(self):
        """Constructs a hybrid retriever (Vector + Graph)."""
        
        # Vector Retriever
        vector_store = Neo4jVector.from_existing_index(
            self.embeddings,
            url=self.url,
            username=self.username,
            password=self.password,
            database=self.database,
            index_name="vector_index",
        )
        vector_retriever = vector_store.as_retriever()

        # Graph Retriever (Cypher-based or Traversal)
        # For simplicity in this demo, we'll use a direct Cypher search 
        # or the built-in graph traversal capabilities.
        
        def graph_retriever(query: str):
            # Example Cypher: Find entities related to the query terms
            # In a production system, you'd use LLM to extract entities first.
            cypher = """
            MATCH (e:Entity)
            WHERE e.id CONTAINS $query
            MATCH (e)-[r]->(related)
            RETURN e.id + ' ' + type(r) + ' ' + related.id AS info
            LIMIT 10
            """
            results = self.graph.query(cypher, {"query": query})
            return "\n".join([r['info'] for r in results])

        # Parallel Execution (RunnableParallel from transcript)
        chain = RunnableParallel({
            "vector_context": vector_retriever,
            "graph_context": RunnableLambda(graph_retriever),
            "question": RunnablePassthrough()
        }) | RunnableLambda(lambda x: {
            "context": f"Vector Data:\n{x['vector_context']}\n\nGraph Data:\n{x['graph_context']}",
            "question": x["question"]
        })
        
        return chain

    def get_graph_as_mermaid(self):
        """Returns the current graph state as a Mermaid flowchart string."""
        cypher = """
        MATCH (s)-[r]->(t)
        RETURN s.id AS source, type(r) AS rel, t.id AS target
        LIMIT 50
        """
        results = self.graph.query(cypher)
        
        mermaid = "flowchart TD\n"
        for res in results:
            # Clean IDs for Mermaid
            s = res['source'].replace('"', '').replace(':', '')
            t = res['target'].replace('"', '').replace(':', '')
            rel = res['rel']
            mermaid += f'    {s}["{s}"] -->|{rel}| {t}["{t}"]\n'
        
        return mermaid

    def query(self, question: str):
        """Runs the full Hybrid RAG query."""
        prompt = ChatPromptTemplate.from_template("""
        Answer the question based on the combined context below.
        If the information is not in the context, say you don't know.
        
        Context:
        {context}
        
        Question: {question}
        
        Answer:""")
        
        chain = self.get_retriever_chain() | prompt | self.llm
        return chain.invoke(question)

if __name__ == "__main__":
    # Example usage
    system = GraphRAGSystem()
    sample_docs = [
        "Lucy Fopco, Mumbai exporter sold speciality dyes to Richmond AG under contract CTR-2024. Payment via LC issued by Deutsche Bank.",
        "Richmond AG is a chemical distribution company based in Zurich. They have a long-term partnership with Fopco."
    ]
    # system.process_documents(sample_docs)
    # print(system.query("Who issued the letter of credit for Fopco?"))
