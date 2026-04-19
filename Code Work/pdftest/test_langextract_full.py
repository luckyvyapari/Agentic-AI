import langextract as lx
import os
from pypdf import PdfReader
from dotenv import load_dotenv

# Load environment variables (for GOOGLE_API_KEY)
load_dotenv()

# Ensure the library can find the API key (it often looks for LANGEXTRACT_API_KEY)
if "GOOGLE_API_KEY" in os.environ and "LANGEXTRACT_API_KEY" not in os.environ:
    os.environ["LANGEXTRACT_API_KEY"] = os.environ["GOOGLE_API_KEY"]

def test_google_langextract(pdf_path, output_path):
    print(f"--- Testing Google LangExtract ---")
    
    # 1. Extract text first (langextract works best on text)
    reader = PdfReader(pdf_path)
    # We'll just take the first 5 pages for this test to keep it fast
    input_text = ""
    for page in reader.pages[:5]:
        input_text += page.extract_text() + "\n"

    # 2. Define the extraction task
    prompt = "Extract key technical terms, their meaning, and any related technologies mentioned."
    
    # 3. Provide an example
    examples = [
        lx.data.ExampleData(
            text="The Transformer model uses an attention mechanism to weigh the importance of different words in a sentence.",
            extractions=[
                lx.data.Extraction(
                    extraction_class="tech_term",
                    extraction_text="Transformer model",
                    attributes={"explanation": "A deep learning architecture used for NLP task", "related": "attention mechanism"}
                )
            ]
        )
    ]

    print("Sending text to LangExtract (Gemini)...")
    try:
        # 4. Run the extraction (with slow settings for Free Tier)
        result = lx.extract(
            text_or_documents=input_text,
            prompt_description=prompt,
            examples=examples,
            model_id="gemini-2.5-flash", 
            max_workers=1,        # Important for Free Tier
            extraction_passes=1    # Keep it simple for the test
        )

        # 5. Save the output
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)
        
        # Save as Markdown-like structure in text file
        output_content = []
        for ext in result.extractions:
            output_content.append(f"TERM: {ext.extraction_text}")
            for key, val in ext.attributes.items():
                output_content.append(f"  {key}: {val}")
            output_content.append("-" * 20)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(output_content))

        print(f"Success! LangExtract results saved to: {output_path}")
        
    except Exception as e:
        print(f"Error during LangExtract process: {e}")

if __name__ == "__main__":
    pdf_file = "/Volumes/SSD/tutorial/Full Stack Agentic AI Engineering /Code Work/langchain_project/pdftest/transformers.pdf"
    output_file = "/Volumes/SSD/tutorial/Full Stack Agentic AI Engineering /Code Work/langchain_project/pdftest/output/langextract_transformers_output.txt"
    test_google_langextract(pdf_file, output_file)
