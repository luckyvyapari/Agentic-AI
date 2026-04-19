import fitz  # PyMuPDF
import os

def extract_to_txt_pymupdf(pdf_path, output_path):
    print(f"Reading with PyMuPDF: {pdf_path}")
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return

    doc = fitz.open(pdf_path)
    full_text = []
    
    for i, page in enumerate(doc):
        text = page.get_text()
        full_text.append(f"--- Page {i+1} ---\n{text}\n")
    
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(full_text))
    
    print(f"Success! PyMuPDF text saved to: {output_path}")

if __name__ == "__main__":
    pdf = "/Volumes/SSD/tutorial/Full Stack Agentic AI Engineering /Code Work/langchain_project/pdftest/transformers.pdf"
    output = "/Volumes/SSD/tutorial/Full Stack Agentic AI Engineering /Code Work/langchain_project/pdftest/output/pymupdf_transformers_output.txt"
    extract_to_txt_pymupdf(pdf, output)
