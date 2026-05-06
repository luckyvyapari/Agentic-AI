import os
from langchain_core.documents import Document
from langchain_text_splitters import TokenTextSplitter

def process_complex_documents():
    """
    Step 2: Load and split documents.
    In business cases, we use small chunks to avoid losing context.
    """
    print("--- Step 2: Processing Complex Documents ---")
    
    # 1. The 'Confusing' documents from Sasmita's session
    raw_data = [
        "Lucy Fopco, Mumbai exporter sold speciality dyes to Richmond AG under contract CTR-2024. Payment via LC issued by Deutsche Bank.",
        "MedFreeze Medical Affairs: Administer Med-X 500mg at T+25 minutes. Relationship: MedFreeze is primary supplier for City Hospital."
    ]

    # 2. Wrapping in LangChain Document objects
    # We add metadata so we can track the source later in Step 4.
    documents = [Document(page_content=text, metadata={"source": f"doc_{i}"}) for i, text in enumerate(raw_data)]
    print(f"Loaded {len(documents)} source documents.")

    # 3. Chunking (Splitting)
    # TokenTextSplitter is great for LLMs as it respects token limits.
    # chunk_overlap ensures that if a relationship spans across two chunks, it isn't lost.
    text_splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=24)
    chunks = text_splitter.split_documents(documents)
    
    print(f"Split into {len(chunks)} chunks.")
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i} Preview: {chunk.page_content[:50]}...")
    
    return chunks

if __name__ == "__main__":
    process_complex_documents()
