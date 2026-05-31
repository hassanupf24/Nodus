import os
from typing import Dict, Any

class HTMLParser:
    """Parser using BeautifulSoup to strip HTML styling and extract body text."""

    def parse(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            from bs4 import BeautifulSoup
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            soup = BeautifulSoup(content, "html.parser")
            
            # Kill script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text()

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = "\n".join(chunk for chunk in chunks if chunk)

            metadata = {
                "title": soup.title.string if soup.title else os.path.basename(file_path),
                "format": "HTML"
            }
            return {
                "text": clean_text,
                "metadata": metadata
            }

        except ImportError:
            return {
                "text": f"[HTML Library missing: bs4. Unable to clean file {file_path}]",
                "metadata": {"title": os.path.basename(file_path)}
            }
        except Exception as e:
            raise RuntimeError(f"Error parsing HTML file: {e}")
