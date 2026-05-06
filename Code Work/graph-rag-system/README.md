# GraphRAG End-to-End System

This project implements a hybrid **Graph + Vector RAG** pipeline using Neo4j and LangChain, based on the Advanced AI Engineering curriculum (Batch 5).

## 🌟 Why GraphRAG?

As discussed in the session, standard Vector RAG can lose information during chunking and lacks the ability to handle complex relationships and reasoning-based logic in "confusing" documents. 

**GraphRAG solving these issues by:**
1.  **Extracting Entities & Relations**: Using `LLMGraphTransformer` to map unstructured text to a structured knowledge graph.
2.  **Hybrid Retrieval**: Parallelizing search across a Vector Index (for semantic similarity) and a Graph Index (for relationship traversal).
3.  **Context Augmentation**: Passing both data streams to the LLM for smarter, context-aware answers.

## 🚀 Getting Started

### **1. Prerequisites**
- **Neo4j**: A running Neo4j instance (Aura or Local).
- **OpenAI API Key**: Required for GPT-4o Mini and Text Embeddings.

### **2. Setup**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **3. Configuration**
Rename `.env.example` to `.env` and fill in your credentials:
- `MODEL_PROVIDER`: Set to `ollama` (default) or `openai`.
- `NEO4J_URI`: Your Neo4j connection string.
- `NEO4J_DATABASE`: Set to `batch5_demo`.

### **5. Run the Demo**
```bash
python demo_graph_rag.py
```

## 🧠 Key Components

- **Multi-Provider Support**: Switch between **OpenAI** (GPT-4o Mini) and **Ollama** (Llama 3.2) by simply changing the `MODEL_PROVIDER` in your `.env` file.
- **`LLMGraphTransformer`**: The core LangChain experimental tool that uses an LLM to convert text chunks into graph nodes and edges.
- **`Neo4jVector`**: Used to store and search document embeddings within the same Neo4j environment.
- **`RunnableParallel`**: Orchestrates the dual-retrieval process to feed the LLM with both vector and graph context.

## 📂 File Structure
- `graph_rag.py`: The main system class implementing transformation, indexing, and querying.
- `demo_graph_rag.py`: Example script with complex medical/business document simulation.
