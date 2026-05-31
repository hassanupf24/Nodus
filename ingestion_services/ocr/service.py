import os
from typing import Dict, Any

class OCRService:
    """Service that runs optical character recognition over images."""

    def extract_text(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image not found: {file_path}")

        try:
            from PIL import Image
            import pytesseract
            img = Image.open(file_path)
            return pytesseract.image_to_string(img)
        except ImportError:
            return f"[OCR library pytesseract/Pillow missing. Unable to read text from image {file_path}]"
        except Exception as e:
            return f"Error executing OCR: {e}"
