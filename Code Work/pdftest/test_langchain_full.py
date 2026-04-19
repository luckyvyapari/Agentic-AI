from langchain_community.document_loaders import PyPDFLoader
import os

def extract_to_txt_langchain(pdf_path, output_path):
    print(f"Reading with LangChain: {pdf_path}")
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return

    loader = PyPDFLoader(pdf_path)
    pages = loader.load_and_split()
    
    full_text = []
    for i, doc in enumerate(pages):
        full_text.append(f"--- Page {i+1} ---\n{doc.page_content}\n")
    
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(full_text))
    
    print(f"Success! LangChain text saved to: {output_path}")

if __name__ == "__main__":
    pdf = "/Volumes/SSD/tutorial/Full Stack Agentic AI Engineering /Code Work/langchain_project/pdftest/transformers.pdf"
    output = "/Volumes/SSD/tutorial/Full Stack Agentic AI Engineering /Code Work/langchain_project/pdftest/output/langchain_transformers_output.txt"
    extract_to_txt_langchain(pdf, output)
