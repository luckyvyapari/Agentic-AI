from unstructured.partition.pdf import partition_pdf
import os

def extract_to_txt_unstructured(pdf_path, output_path):
    print(f"Reading with Unstructured (OSS): {pdf_path}")
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return

    # 1. Partition the PDF into elements
    # We use 'fast' strategy for this test. 'hi_res' is better but requires more models.
    print("Partitioning PDF...")
    elements = partition_pdf(
        filename=pdf_path,
        strategy="fast" 
    )
    
    # 2. Extract text and categorize
    full_text = []
    for i, element in enumerate(elements):
        full_text.append(f"[{element.category.upper()}] {element.text}")
    
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(full_text))
    
    print(f"Success! Unstructured text saved to: {output_path}")

if __name__ == "__main__":
    pdf = "/Volumes/SSD/tutorial/Full Stack Agentic AI Engineering /Code Work/langchain_project/pdftest/transformers.pdf"
    output = "/Volumes/SSD/tutorial/Full Stack Agentic AI Engineering /Code Work/langchain_project/pdftest/output/unstructured_transformers_output.txt"
    extract_to_txt_unstructured(pdf, output)
