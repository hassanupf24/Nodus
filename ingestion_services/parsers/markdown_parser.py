import os
import re
from typing import Dict, Any

class MarkdownParser:
    """Parser that reads markdown files and extracts structural outlines."""

    def parse(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

            # Find markdown headers (e.g. # Title, ## Section)
            headers = re.findall(r"^(#{1,6})\s+(.+)$", text, re.MULTILINE)
            outline = [f"{len(h[0])} - {h[1].strip()}" for h in headers]

            metadata = {
                "title": os.path.basename(file_path),
                "format": "Markdown",
                "headers": outline
            }
            return {
                "text": text,
                "metadata": metadata
            }
        except Exception as e:
            raise RuntimeError(f"Error parsing Markdown file: {e}")
