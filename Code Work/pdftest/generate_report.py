import os

def generate_html_report(output_dir, report_path):
    files = [
        {"name": "IBM Docling", "file": "docling_transformers_output.md", "quality": "High", "rating": "⭐⭐⭐⭐⭐"},
        {"name": "PyMuPDF", "file": "pymupdf_transformers_output.txt", "quality": "Good", "rating": "⭐⭐⭐⭐"},
        {"name": "LangChain", "file": "langchain_transformers_output.txt", "quality": "Average", "rating": "⭐⭐⭐"},
        {"name": "pdfplumber", "file": "pdfplumber_transformers_output.txt", "quality": "Good", "rating": "⭐⭐⭐⭐"},
        {"name": "PyPDF", "file": "pypdf_transformers_output.txt", "quality": "Low", "rating": "⭐⭐"},
        {"name": "OCR (Tesseract)", "file": "ocr_transformers_output.txt", "quality": "Variable", "rating": "⭐⭐"},
        {"name": "PyMuPDF Detailed (JSON)", "file": "pymupdf_detailed_data.json", "quality": "Maximum", "rating": "⭐⭐⭐⭐⭐"},
    ]

    html_content = """
    <html>
    <head>
        <title>PDF Extraction Comparison Report</title>
        <style>
            body { font-family: 'Inter', -apple-system, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 40px; background: #f8f9fa; }
            h1 { color: #1a73e8; border-bottom: 2px solid #1a73e8; padding-bottom: 10px; }
            h2 { color: #1e8e3e; margin-top: 50px; border-left: 5px solid #1e8e3e; padding-left: 15px; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 30px; background: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; }
            th, td { padding: 15px; text-align: left; border-bottom: 1px solid #eee; }
            th { background-color: #f1f3f4; font-weight: 600; color: #555; }
            .content-box { background: #fff; border: 1px solid #ddd; padding: 20px; border-radius: 8px; max-height: 400px; overflow-y: scroll; white-space: pre-wrap; font-family: 'Fira Code', monospace; font-size: 14px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.05); }
            .tag { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }
            .tag-fast { background: #e6f4ea; color: #1e8e3e; }
            .tag-structural { background: #e8f0fe; color: #1a73e8; }
            .tag-fallback { background: #fef7e0; color: #f9ab00; }
            .btn { background: #1a73e8; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold; margin-bottom: 30px; display: inline-block; }
            .btn:hover { background: #1557b0; }
        </style>
    </head>
    <body>
        <h1>PDF Extraction Analysis & Comparison</h1>
        
        <p>This report compares the output quality and performance of different extraction libraries.</p>
        
        <a href="visual_layout.html" class="btn" target="_blank">👁️ View PDF Visual Layout (HTML)</a>

        <table>
            <thead>
                <tr>
                    <th>Library</th>
                    <th>Quality</th>
                    <th>Rating</th>
                    <th>Char Count</th>
                    <th>Key Features</th>
                </tr>
            </thead>
            <tbody>
    """

    for item in files:
        full_path = os.path.join(output_dir, item["file"])
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            char_count = len(content)
            
            # Feature tagging
            feature = ""
            if "pypdf" in item["file"]: feature = '<span class="tag tag-fast">Fastest</span>'
            elif "docling" in item["file"]: feature = '<span class="tag tag-structural">Structural</span>'
            elif "ocr" in item["file"]: feature = '<span class="tag tag-fallback">Image-to-Text</span>'
            else: feature = '<span class="tag tag-structural">Robust</span>'

            html_content += f"""
                <tr>
                    <td>{item["name"]}</td>
                    <td>{item["quality"]}</td>
                    <td>{item["rating"]}</td>
                    <td>{char_count:,}</td>
                    <td>{feature}</td>
                </tr>
            """

    html_content += """
            </tbody>
        </table>

        <h1>Detailed Output View</h1>
    """

    for item in files:
        full_path = os.path.join(output_dir, item["file"])
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            html_content += f"""
                <h2>{item["name"]} ({item["file"]})</h2>
                <div class="content-box">{content[:10000]}...</div>
            """

    html_content += """
    </body>
    </html>
    """

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"Report generated successfully: {report_path}")

if __name__ == "__main__":
    out_dir = "/Volumes/SSD/tutorial/Full Stack Agentic AI Engineering /Code Work/langchain_project/pdftest/output"
    rep_path = "/Volumes/SSD/tutorial/Full Stack Agentic AI Engineering /Code Work/langchain_project/pdftest/output/comparison_report.html"
    generate_html_report(out_dir, rep_path)
