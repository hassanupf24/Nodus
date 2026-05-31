"""Async SQLite connection manager with connection pooling."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import aiosqlite

from shared.logging_config import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """Manages an async SQLite connection pool.

    Uses a simple semaphore-based pool:  we keep *max_connections* open
    aiosqlite connections in a queue and hand them out on demand.
    """

    def __init__(self, db_path: Path | str, max_connections: int = 5) -> None:
        self._db_path = Path(db_path)
        self._max_connections = max_connections
        self._pool: asyncio.Queue[aiosqlite.Connection] = asyncio.Queue(maxsize=max_connections)
        self._initialized = False
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """Create the database file (if needed) and fill the pool."""
        async with self._lock:
            if self._initialized:
                return
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            for _ in range(self._max_connections):
                conn = await aiosqlite.connect(str(self._db_path))
                conn.row_factory = aiosqlite.Row
                await conn.execute("PRAGMA journal_mode=WAL")
                await conn.execute("PRAGMA foreign_keys=ON")
                await conn.execute("PRAGMA busy_timeout=5000")
                self._pool.put_nowait(conn)
            self._initialized = True
            logger.info("database.initialized", path=str(self._db_path), pool_size=self._max_connections)

    async def acquire(self) -> aiosqlite.Connection:
        """Get a connection from the pool (blocks if none available)."""
        if not self._initialized:
            await self.initialize()
        return await self._pool.get()

    async def release(self, conn: aiosqlite.Connection) -> None:
        """Return a connection to the pool."""
        await self._pool.put(conn)

    async def execute(self, sql: str, params: tuple[Any, ...] | None = None) -> list[Any]:
        """Execute a query and return all rows."""
        conn = await self.acquire()
        try:
            cursor = await conn.execute(sql, params or ())
            rows = await cursor.fetchall()
            await conn.commit()
            return rows
        finally:
            await self.release(conn)

    async def execute_insert(self, sql: str, params: tuple[Any, ...] | None = None) -> int:
        """Execute an INSERT and return lastrowid."""
        conn = await self.acquire()
        try:
            cursor = await conn.execute(sql, params or ())
            await conn.commit()
            return cursor.lastrowid or 0
        finally:
            await self.release(conn)

    async def execute_many(self, sql: str, params_seq: list[tuple[Any, ...]]) -> None:
        """Execute the same statement with many param sets."""
        conn = await self.acquire()
        try:
            await conn.executemany(sql, params_seq)
            await conn.commit()
        finally:
            await self.release(conn)

    async def execute_script(self, script: str) -> None:
        """Execute a multi-statement SQL script."""
        conn = await self.acquire()
        try:
            await conn.executescript(script)
        finally:
            await self.release(conn)

    async def close(self) -> None:
        """Drain and close every connection in the pool."""
        while not self._pool.empty():
            conn = self._pool.get_nowait()
            await conn.close()
        self._initialized = False
        logger.info("database.closed", path=str(self._db_path))


# ── Convenience singleton ────────────────────────────────
_default_db: DatabaseManager | None = None


async def get_database(db_path: Path | str | None = None) -> DatabaseManager:
    """Return (and lazily create) the default DatabaseManager."""
    global _default_db  # noqa: PLW0603
    if _default_db is None:
        from shared.config import get_settings
        path = db_path or get_settings().sqlite_path
        _default_db = DatabaseManager(path)
        await _default_db.initialize()
    return _default_db
