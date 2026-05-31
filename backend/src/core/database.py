import aiosqlite
import logging
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, sqlite_path: str = "nodus_local.db", qdrant_path: str = "nodus_vectors") -> None:
        self.sqlite_path = sqlite_path
        self.qdrant_path = qdrant_path
        self.qdrant_client = AsyncQdrantClient(path=self.qdrant_path)
        self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")

    async def init_sqlite(self) -> None:
        """Initializes SQLite tables for Metadata, Graph, and Episodes."""
        logger.info(f"Initializing SQLite database at {self.sqlite_path}")
        async with aiosqlite.connect(self.sqlite_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    attributes JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS episodes (
                    id TEXT PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    event_type TEXT NOT NULL,
                    summary TEXT,
                    context JSON
                );
            """)
            await db.commit()
        logger.info("SQLite tables created successfully.")
        
    async def init_qdrant(self) -> None:
        """Initializes embedded Qdrant collections."""
        logger.info(f"Initializing Qdrant at {self.qdrant_path}")
        collection_name = "nodus_memory"
        
        # Check if collection exists
        if not await self.qdrant_client.collection_exists(collection_name):
            # all-MiniLM-L6-v2 has dimension 384
            await self.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
            logger.info(f"Created Qdrant collection: {collection_name}")
        else:
            logger.info(f"Qdrant collection {collection_name} already exists.")

    async def save_episode(self, episode_id: str, timestamp: str, event_type: str, summary: str, context: str) -> None:
        """Saves an episode to SQLite."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            await db.execute(
                "INSERT INTO episodes (id, timestamp, event_type, summary, context) VALUES (?, ?, ?, ?, ?)",
                (episode_id, timestamp, event_type, summary, context)
            )
            await db.commit()
