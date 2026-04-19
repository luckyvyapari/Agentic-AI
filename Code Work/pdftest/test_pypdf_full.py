from pypdf import PdfReader
import os

def extract_to_txt(pdf_path, output_path):
    print(f"Reading: {pdf_path}")
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return

    reader = PdfReader(pdf_path)
    full_text = []
    
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            full_text.append(f"--- Page {i+1} ---\n{text}\n")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(full_text))
    
    print(f"Success! Text saved to: {output_path}")

if __name__ == "__main__":
    pdf = "/Volumes/SSD/tutorial/Full Stack Agentic AI Engineering /Code Work/langchain_project/pdftest/transformers.pdf"
    output_dir = "/Volumes/SSD/tutorial/Full Stack Agentic AI Engineering /Code Work/langchain_project/pdftest/output"
    os.makedirs(output_dir, exist_ok=True)
    output = os.path.join(output_dir, "pypdf_transformers_output.txt")
    extract_to_txt(pdf, output)
