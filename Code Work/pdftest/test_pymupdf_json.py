import fitz  # PyMuPDF
import json
import os

def extract_pdf_to_json(pdf_path, output_path):
    print(f"Extracting JSON with PyMuPDF: {pdf_path}")
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return

    doc = fitz.open(pdf_path)
    # Extract only the first page as JSON to keep it readable
    page = doc[0]
    json_doc = page.get_text("json") # Returns a string
    
    # Parse and re-format for pretty printing
    data = json.loads(json_doc)
    
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    print(f"Success! Detailed JSON saved to: {output_path}")

if __name__ == "__main__":
    pdf = "/Volumes/SSD/tutorial/Full Stack Agentic AI Engineering /Code Work/langchain_project/pdftest/transformers.pdf"
    output = "/Volumes/SSD/tutorial/Full Stack Agentic AI Engineering /Code Work/langchain_project/pdftest/output/pymupdf_detailed_data.json"
    extract_pdf_to_json(pdf, output)
