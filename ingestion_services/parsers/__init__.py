import os
from typing import Dict, Any

class ParserRegistry:
    """Registry matching file extensions to custom parser modules."""

    @staticmethod
    def get_parser(file_path: str) -> Any:
        _, ext = os.path.splitext(file_path)
        ext = ext.lower().replace(".", "")
        
        if ext == "pdf":
            from ingestion_services.parsers.pdf_parser import PDFParser
            return PDFParser()
        elif ext in ("docx", "doc"):
            from ingestion_services.parsers.docx_parser import DOCXParser
            return DOCXParser()
        elif ext in ("html", "htm"):
            from ingestion_services.parsers.html_parser import HTMLParser
            return HTMLParser()
        elif ext == "md":
            from ingestion_services.parsers.markdown_parser import MarkdownParser
            return MarkdownParser()
        elif ext in ("wav", "mp3", "m4a", "ogg", "flac"):
            from ingestion_services.parsers.speech_parser import SpeechParser
            return SpeechParser()
        else:
            # Default fallback for simple txt/csv etc.
            from ingestion_services.parsers.text_parser import TextParser
            return TextParser()
