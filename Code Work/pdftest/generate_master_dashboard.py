import json
import os

def generate_master_dashboard(results_file, report_path):
    with open(results_file, "r") as f:
        results = json.load(f)

    # Scoring Logic (1-5 stars)
    # This is a heuristic based on industry standards for these specific tools
    weights = {
        "Simple": {"PyMuPDF": 5, "PyPDF": 5, "Docling": 3, "pdfplumber": 4, "OCR (Tesseract)": 1, "Unstructured": 4},
        "Invoice (Tables)": {"Docling": 5, "pdfplumber": 5, "Unstructured": 4, "PyMuPDF": 3, "PyPDF": 2, "OCR (Tesseract)": 2},
        "Research Paper": {"Docling": 5, "Unstructured": 5, "PyMuPDF": 3, "pdfplumber": 2, "PyPDF": 3, "OCR (Tesseract)": 1},
        "Fillable Form": {"PyMuPDF": 5, "pdfplumber": 5, "Docling": 2, "PyPDF": 4, "Unstructured": 3, "OCR (Tesseract)": 1}
    }

    html_content = """
    <html>
    <head>
        <title>Master PDF Benchmark Dashboard</title>
        <style>
            body { font-family: 'Outfit', sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; }
            .container { max-width: 1200px; margin: 0 auto; }
            h1 { font-size: 3rem; margin-bottom: 30px; background: linear-gradient(90deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
            .card { background: #1e293b; border-radius: 16px; padding: 24px; margin-bottom: 40px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border: 1px solid #334155; }
            h2 { color: #38bdf8; border-bottom: 1px solid #334155; padding-bottom: 12px; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { padding: 16px; text-align: left; border-bottom: 1px solid #334155; }
            th { font-weight: 600; color: #94a3b8; }
            .stars { color: #fbbf24; font-size: 1.2rem; }
            .badge { padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; }
            .badge-fast { background: #065f46; color: #34d399; }
            .badge-slow { background: #7f1d1d; color: #f87171; }
            .link-btn { color: #38bdf8; text-decoration: none; font-size: 0.9rem; border: 1px solid #38bdf8; padding: 4px 8px; border-radius: 4px; }
            .link-btn:hover { background: #38bdf8; color: #0f172a; }
            .overall-score { font-size: 2rem; color: #fbbf24; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📑 Master PDF Benchmarks (2025)</h1>
            <p>Benchmarking 6 libraries across 4 document categories.</p>
    """

    for category, methods in results.items():
        html_content += f"""
        <div class="card">
            <h2>Category: {category}</h2>
            <table>
                <thead>
                    <tr>
                        <th>Library</th>
                        <th>Rating</th>
                        <th>Speed</th>
                        <th>Chars</th>
                        <th>Output</th>
                    </tr>
                </thead>
                <tbody>
        """
        for name, data in methods.items():
            if data.get("status") != "Success":
                continue
            
            rating_val = weights.get(category, {}).get(name, 3)
            stars = "⭐" * rating_val
            
            # Speed badge
            speed_class = "badge-fast" if data["time"] < 1.0 else "badge-slow"
            
            # Relative path for the dashboard (assuming it's in the same folder as the output)
            relative_file = os.path.basename(data["file"])

            html_content += f"""
                <tr>
                    <td><strong>{name}</strong></td>
                    <td><span class="stars">{stars}</span></td>
                    <td><span class="badge {speed_class}">{data["time"]}s</span></td>
                    <td>{data["chars"]:,}</td>
                    <td><a href="benchmark/{relative_file}" class="link-btn" target="_blank">View Text</a></td>
                </tr>
            """
        html_content += "</tbody></table></div>"

    html_content += """
        </div>
    </body>
    </html>
    """

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"Master Dashboard generated: {report_path}")

if __name__ == "__main__":
    res_file = "/Volumes/SSD/tutorial/Full Stack Agentic AI Engineering /Code Work/langchain_project/pdftest/output/benchmark/results.json"
    dash_path = "/Volumes/SSD/tutorial/Full Stack Agentic AI Engineering /Code Work/langchain_project/pdftest/output/master_dashboard.html"
    generate_master_dashboard(res_file, dash_path)
