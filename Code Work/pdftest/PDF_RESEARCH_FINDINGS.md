# 🔬 PDF Extraction: 2025 Ground Truth & Strategy

## 🏁 The Research Landscape
After testing 6 libraries and performing a technical audit, here is the state-of-the-art for PDF extraction in 2025.

### 🏆 Top Local Pick: Docling (Linux Foundation AI & Data)
*   **Status**: Community project (not IBM-proprietary).
*   **Strength**: ~97.9% accuracy in complex tables. Layout fidelity for RAG.
*   **Weakness**: Resource intensive. **Known production issue**: Can hang indefinitely/silently on certain PDFs.
*   **OCR**: Supports Tesseract/RapidOCR but can struggle with poor quality image-based PDFs.

### ⚡ Speed & Pre-processing: PyMuPDF (Fitz)
*   **Strength**: Fastest possible extraction. supports JSON/HTML.
*   **Weakness**: Naive extraction (struggles with complex table logic).
*   **Role**: Best for initial filtering and high-volume pre-processing.

### ☁️ Cloud Contenders (The "High Accuracy" alternatives)
*   **LlamaParse**: Paid Cloud API (not local). Best for "messy" documents if budget allows.
*   **Mistral OCR**: PDF-first, fast, and excellent for multimodal RAG (returns images).
*   **Unstructured.io**: Enterprise standard. Lowest hallucination rates (0.027).

---

## 🔧 Comparison Matrix 2025
| Situation | Use This | Why? |
| :--- | :--- | :--- |
| **Research / Complex Layouts** | **Docling** | Layout fidelity, TableFormer support |
| **High-volume / Metadata** | **PyMuPDF** | Fastest, zero AI overhead |
| **Scanned / Fallback** | **Tesseract** | True local OCR fallback |
| **Cloud-based / Max Accuracy** | **LlamaParse** | LLM-powered, cloud-scaled (Paid) |
| **Batch Pipelines + Images** | **Mistral OCR** | Fast, affordable multimodal support |
| **Enterprise Production** | **Unstructured.io**| Best hallucination control, SOC 2 |

---

## 🎯 Final Verdict for Agentic Pipeline
1.  **Primary Ingestion**: **Docling**, but **MUST** be wrapped in a timeout + fallback handler to prevent silent hangs.
2.  **Fast Path**: Use **PyMuPDF** for simple text-heavy docs to save compute.
3.  **OCR Route**: Route scanned PDFs through **Tesseract** locally or **Mistral OCR** if cloud is an option.
4.  **Scaling**: Evaluate **Unstructured.io** or **Reducto** if production accuracy needs exceed local Docling capabilities.
