import os
from typing import Dict, Any

class TextParser:
    """Parser that reads plain text files with automatic encoding fallback."""

    def parse(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        encodings = ["utf-8", "latin-1", "cp1252"]
        text = ""
        success = False

        for enc in encodings:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    text = f.read()
                success = True
                break
            except UnicodeDecodeError:
                continue

        if not success:
            # Final fallback, read binary and strip non-ascii
            with open(file_path, "rb") as f:
                binary = f.read()
            text = binary.decode("ascii", errors="ignore")

        metadata = {
            "title": os.path.basename(file_path),
            "format": "TXT"
        }
        return {
            "text": text,
            "metadata": metadata
        }
