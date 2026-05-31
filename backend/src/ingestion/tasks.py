class IngestionPipeline:
    def __init__(self) -> None:
        pass
        
    async def process_document(self, file_path: str) -> None:
        """Parses document, chunks text, and sends to vector store/graph."""
        pass

    async def extract_entities(self, text: str) -> None:
        """Passes text through LLM to extract entities for the Knowledge Graph."""
        pass
