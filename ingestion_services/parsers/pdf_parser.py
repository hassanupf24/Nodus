import os
from typing import Dict, Any

class PDFParser:
    """Parser using PyMuPDF (fitz) to extract clean text from PDF documents."""

    def parse(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            full_text = []
            metadata = {
                "title": doc.metadata.get("title", "") or os.path.basename(file_path),
                "author": doc.metadata.get("author", ""),
                "pages": len(doc),
                "format": "PDF"
            }

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text().strip()
                if not text:
                    # Try OCR if no text found
                    try:
                        from PIL import Image
                        import pytesseract
                        import io
                        
                        pix = page.get_pixmap()
                        img_bytes = pix.tobytes("png")
                        img = Image.open(io.BytesIO(img_bytes))
                        ocr_text = pytesseract.image_to_string(img)
                        text = ocr_text.strip()
                    except Exception as e:
                        text = f"[OCR Failed: {e}]"
                
                if text:
                    full_text.append(text)

            doc.close()
            return {
                "text": "\n".join(full_text),
                "metadata": metadata
            }

        except ImportError:
            # Fallback simple text read if library is missing
            return {
                "text": f"[PDF Library missing: fitz. Unable to parse binary file {file_path}]",
                "metadata": {"title": os.path.basename(file_path), "pages": 0}
            }
        except Exception as e:
            raise RuntimeError(f"Error parsing PDF file: {e}")
