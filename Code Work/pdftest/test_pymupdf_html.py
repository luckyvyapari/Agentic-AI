import fitz  # PyMuPDF
import os

def convert_pdf_to_visual_html(pdf_path, output_path):
    print(f"Creating Visual HTML with PyMuPDF: {pdf_path}")
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return

    doc = fitz.open(pdf_path)
    
    # Extract only first 20 pages for the visual test to keep file size reasonable
    html_content = ""
    for i in range(min(20, len(doc))):
        page = doc[i]
        html_content += page.get_text("html")
    
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"<html><body style='background:#f0f0f0; padding:20px;'>{html_content}</body></html>")
    
    print(f"Success! Visual HTML saved to: {output_path}")

if __name__ == "__main__":
    pdf = "/Volumes/SSD/tutorial/Full Stack Agentic AI Engineering /Code Work/langchain_project/pdftest/transformers.pdf"
    output = "/Volumes/SSD/tutorial/Full Stack Agentic AI Engineering /Code Work/langchain_project/pdftest/output/visual_layout.html"
    convert_pdf_to_visual_html(pdf, output)
