import pytesseract
from pdf2image import convert_from_path
import os

# Set tesseract path for macOS (Homebrew)
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

def extract_to_txt_ocr(pdf_path, output_path):
    print(f"Reading with OCR (Scanned PDF Mode): {pdf_path}")
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return

    # 1. Convert PDF pages to images (using poppler)
    # We take first 5 pages for the test to avoid taking too much time/memory
    print("Converting PDF to images...")
    pages = convert_from_path(
        pdf_path, 
        first_page=1, 
        last_page=5,
        poppler_path='/opt/homebrew/bin'  # Added for Homebrew on Apple Silicon
    )
    
    full_text = []
    for i, page_image in enumerate(pages):
        print(f"OCR processing page {i+1}...")
        text = pytesseract.image_to_string(page_image)
        full_text.append(f"--- Page {i+1} (OCR) ---\n{text}\n")
    
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(full_text))
    
    print(f"Success! OCR text saved to: {output_path}")

if __name__ == "__main__":
    pdf = "/Volumes/SSD/tutorial/Full Stack Agentic AI Engineering /Code Work/langchain_project/pdftest/transformers.pdf"
    output = "/Volumes/SSD/tutorial/Full Stack Agentic AI Engineering /Code Work/langchain_project/pdftest/output/ocr_transformers_output.txt"
    extract_to_txt_ocr(pdf, output)
