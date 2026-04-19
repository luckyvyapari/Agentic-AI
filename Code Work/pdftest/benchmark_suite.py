import os
import time
import json
from pypdf import PdfReader
from docling.document_converter import DocumentConverter
import fitz # PyMuPDF
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
from unstructured.partition.pdf import partition_pdf

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

SAMPLES_DIR = "pdftest/samples"
OUTPUT_DIR = "pdftest/output/benchmark"
os.makedirs(OUTPUT_DIR, exist_ok=True)

SAMPLES = {
    "Simple": "simple.pdf",
    "Invoice (Tables)": "invoice.pdf",
    "Research Paper": "research.pdf",
    "Fillable Form": "form.pdf"
}

def run_pypdf(path):
    reader = PdfReader(path)
    return " ".join([p.extract_text() for p in reader.pages])

def run_docling(path):
    converter = DocumentConverter()
    result = converter.convert(path)
    return result.document.export_to_markdown()

def run_pymupdf(path):
    doc = fitz.open(path)
    return " ".join([p.get_text() for p in doc])

def run_pdfplumber(path):
    with pdfplumber.open(path) as pdf:
        return " ".join([p.extract_text() or "" for p in pdf.pages])

def run_ocr(path):
    # Only first 2 pages for benchmarks to save time
    pages = convert_from_path(path, first_page=1, last_page=2, poppler_path='/opt/homebrew/bin')
    return " ".join([pytesseract.image_to_string(p) for p in pages])

def run_unstructured(path):
    elements = partition_pdf(filename=path, strategy="fast")
    return " ".join([e.text for e in elements])

METHODS = {
    "PyPDF": run_pypdf,
    "Docling": run_docling,
    "PyMuPDF": run_pymupdf,
    "pdfplumber": run_pdfplumber,
    "OCR (Tesseract)": run_ocr,
    "Unstructured": run_unstructured
}

def run_benchmark():
    results = {}
    
    for category, filename in SAMPLES.items():
        print(f"\n🚀 Benchmarking Category: {category}")
        path = os.path.join(SAMPLES_DIR, filename)
        if not os.path.exists(path):
            print(f"Skipping {path} (not found)")
            continue
            
        results[category] = {}
        
        for name, func in METHODS.items():
            print(f"  - Running {name}...")
            start_time = time.time()
            try:
                text = func(path)
                elapsed = time.time() - start_time
                char_count = len(text)
                
                # Save sample output
                safe_name = name.replace(" ", "_").lower()
                safe_cat = category.replace(" ", "_").lower().replace("(", "").replace(")", "")
                out_file = os.path.join(OUTPUT_DIR, f"{safe_cat}_{safe_name}.txt")
                with open(out_file, "w", encoding="utf-8") as f:
                    f.write(text)
                
                results[category][name] = {
                    "time": round(elapsed, 2),
                    "chars": char_count,
                    "status": "Success",
                    "file": out_file
                }
            except Exception as e:
                print(f"    Error: {e}")
                results[category][name] = {"status": f"Error: {e}"}

    with open(os.path.join(OUTPUT_DIR, "results.json"), "w") as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    run_benchmark()
