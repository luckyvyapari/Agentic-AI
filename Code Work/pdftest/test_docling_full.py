from docling.document_converter import DocumentConverter
import os

def extract_to_txt_docling(pdf_path, output_path):
    print(f"Reading with Docling (IBM): {pdf_path}")
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return

    # 1. Convert the document
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    
    # 2. Export to Markdown (best for Docling)
    markdown_output = result.document.export_to_markdown()
    
    # 3. Save to output folder
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_output)
    
    print(f"Success! Docling markdown saved to: {output_path}")

if __name__ == "__main__":
    pdf = "/Volumes/SSD/tutorial/Full Stack Agentic AI Engineering /Code Work/langchain_project/pdftest/transformers.pdf"
    output = "/Volumes/SSD/tutorial/Full Stack Agentic AI Engineering /Code Work/langchain_project/pdftest/output/docling_transformers_output.md"
    extract_to_txt_docling(pdf, output)
