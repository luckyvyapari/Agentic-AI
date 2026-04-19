import pdfplumber
import os

def extract_to_txt_pdfplumber(pdf_path, output_path):
    print(f"Reading with pdfplumber: {pdf_path}")
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return

    full_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                full_text.append(f"--- Page {i+1} ---\n{text}\n")
    
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(full_text))
    
    print(f"Success! pdfplumber text saved to: {output_path}")

if __name__ == "__main__":
    pdf = "/Volumes/SSD/tutorial/Full Stack Agentic AI Engineering /Code Work/langchain_project/pdftest/transformers.pdf"
    output = "/Volumes/SSD/tutorial/Full Stack Agentic AI Engineering /Code Work/langchain_project/pdftest/output/pdfplumber_transformers_output.txt"
    extract_to_txt_pdfplumber(pdf, output)
