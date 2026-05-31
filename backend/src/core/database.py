class DatabaseManager:
    def __init__(self) -> None:
        self.sqlite_path = "nodus_local.db"
        self.qdrant_path = "nodus_vectors"

    async def init_sqlite(self) -> None:
        """Initializes SQLite tables for Metadata, Graph, and Episodes."""
        pass
        
    async def init_qdrant(self) -> None:
        """Initializes embedded Qdrant collections."""
        pass
