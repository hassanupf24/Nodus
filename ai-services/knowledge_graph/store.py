"""SQLite-backed graph storage — nodes table, edges table, with FTS5."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

import aiosqlite

from knowledge_graph.schemas import Entity, EntityType, Relationship
from shared.logging_config import get_logger

logger = get_logger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS nodes (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    entity_type TEXT NOT NULL DEFAULT 'concept',
    description TEXT,
    properties  TEXT DEFAULT '{}',
    source      TEXT,
    created_at  REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS edges (
    id            TEXT PRIMARY KEY,
    source_id     TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    target_id     TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    relation_type TEXT NOT NULL,
    weight        REAL DEFAULT 1.0,
    properties    TEXT DEFAULT '{}',
    created_at    REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_nodes_name ON nodes(name);
CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(entity_type);
CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id);
CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id);
CREATE INDEX IF NOT EXISTS idx_edges_relation ON edges(relation_type);

-- Full-text search on node names and descriptions
CREATE VIRTUAL TABLE IF NOT EXISTS nodes_fts USING fts5(
    name, description, content=nodes, content_rowid=rowid
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS nodes_ai AFTER INSERT ON nodes BEGIN
    INSERT INTO nodes_fts(rowid, name, description)
    VALUES (new.rowid, new.name, new.description);
END;

CREATE TRIGGER IF NOT EXISTS nodes_ad AFTER DELETE ON nodes BEGIN
    INSERT INTO nodes_fts(nodes_fts, rowid, name, description)
    VALUES ('delete', old.rowid, old.name, old.description);
END;

CREATE TRIGGER IF NOT EXISTS nodes_au AFTER UPDATE ON nodes BEGIN
    INSERT INTO nodes_fts(nodes_fts, rowid, name, description)
    VALUES ('delete', old.rowid, old.name, old.description);
    INSERT INTO nodes_fts(rowid, name, description)
    VALUES (new.rowid, new.name, new.description);
END;
"""


class GraphStore:
    """SQLite-backed knowledge graph with FTS5 full-text search."""

    def __init__(self, db_path: Path | str) -> None:
        self._db_path = Path(db_path)
        self._conn: aiosqlite.Connection | None = None

    async def initialize(self) -> None:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(str(self._db_path))
        self._conn.row_factory = aiosqlite.Row
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.execute("PRAGMA foreign_keys=ON")
        await self._conn.executescript(_SCHEMA)
        await self._conn.commit()
        logger.info("graph_store.initialized", path=str(self._db_path))

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()
            self._conn = None

    @property
    def conn(self) -> aiosqlite.Connection:
        assert self._conn is not None, "GraphStore not initialized"
        return self._conn

    # ── Nodes (entities) ──────────────────────────────────

    async def add_entity(self, entity: Entity) -> str:
        eid = entity.id or str(uuid.uuid4())
        import time
        await self.conn.execute(
            """INSERT OR REPLACE INTO nodes (id, name, entity_type, description, properties, source, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                eid,
                entity.name,
                entity.entity_type.value,
                entity.description,
                json.dumps(entity.properties),
                entity.source,
                time.time(),
            ),
        )
        await self.conn.commit()
        return eid

    async def get_entity(self, entity_id: str) -> Entity | None:
        cursor = await self.conn.execute("SELECT * FROM nodes WHERE id = ?", (entity_id,))
        row = await cursor.fetchone()
        if not row:
            return None
        return self._row_to_entity(row)

    async def find_entities(self, name: str | None = None, entity_type: str | None = None, limit: int = 50) -> list[Entity]:
        conditions: list[str] = []
        params: list[Any] = []
        if name:
            conditions.append("name LIKE ?")
            params.append(f"%{name}%")
        if entity_type:
            conditions.append("entity_type = ?")
            params.append(entity_type)
        where = " AND ".join(conditions) if conditions else "1=1"
        cursor = await self.conn.execute(
            f"SELECT * FROM nodes WHERE {where} ORDER BY created_at DESC LIMIT ?",
            (*params, limit),
        )
        rows = await cursor.fetchall()
        return [self._row_to_entity(r) for r in rows]

    async def search_entities(self, query: str, limit: int = 20) -> list[Entity]:
        """Full-text search over entity names and descriptions."""
        cursor = await self.conn.execute(
            """SELECT nodes.* FROM nodes_fts
               JOIN nodes ON nodes.rowid = nodes_fts.rowid
               WHERE nodes_fts MATCH ?
               LIMIT ?""",
            (query, limit),
        )
        rows = await cursor.fetchall()
        return [self._row_to_entity(r) for r in rows]

    async def delete_entity(self, entity_id: str) -> bool:
        cursor = await self.conn.execute("DELETE FROM nodes WHERE id = ?", (entity_id,))
        await self.conn.commit()
        return cursor.rowcount > 0

    # ── Edges (relationships) ─────────────────────────────

    async def add_relationship(self, rel: Relationship) -> str:
        rid = rel.id or str(uuid.uuid4())
        import time
        await self.conn.execute(
            """INSERT OR REPLACE INTO edges (id, source_id, target_id, relation_type, weight, properties, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                rid,
                rel.source_id,
                rel.target_id,
                rel.relation_type,
                rel.weight,
                json.dumps(rel.properties),
                time.time(),
            ),
        )
        await self.conn.commit()
        return rid

    async def get_relationships(
        self, entity_id: str, relation_type: str | None = None, direction: str = "both"
    ) -> list[Relationship]:
        conditions: list[str] = []
        params: list[Any] = []

        if direction in ("out", "both"):
            conditions.append("source_id = ?")
            params.append(entity_id)
        if direction in ("in", "both"):
            conditions.append("target_id = ?")
            params.append(entity_id)

        where = " OR ".join(conditions)
        if relation_type:
            where = f"({where}) AND relation_type = ?"
            params.append(relation_type)

        cursor = await self.conn.execute(
            f"SELECT * FROM edges WHERE {where}", params
        )
        rows = await cursor.fetchall()
        return [self._row_to_relationship(r) for r in rows]

    async def delete_relationship(self, rel_id: str) -> bool:
        cursor = await self.conn.execute("DELETE FROM edges WHERE id = ?", (rel_id,))
        await self.conn.commit()
        return cursor.rowcount > 0

    # ── Graph queries ─────────────────────────────────────

    async def get_neighbors(self, entity_id: str, max_depth: int = 1, limit: int = 50) -> dict[str, Any]:
        """BFS to find neighbors up to *max_depth* hops away."""
        visited_nodes: dict[str, dict[str, Any]] = {}
        visited_edges: list[dict[str, Any]] = []
        queue: list[tuple[str, int]] = [(entity_id, 0)]
        seen: set[str] = {entity_id}

        while queue and len(visited_nodes) < limit:
            current_id, depth = queue.pop(0)
            entity = await self.get_entity(current_id)
            if entity:
                visited_nodes[current_id] = {
                    "id": current_id,
                    "name": entity.name,
                    "entity_type": entity.entity_type.value,
                    "description": entity.description,
                }

            if depth >= max_depth:
                continue

            rels = await self.get_relationships(current_id)
            for rel in rels:
                visited_edges.append({
                    "source": rel.source_id,
                    "target": rel.target_id,
                    "relation_type": rel.relation_type,
                    "weight": rel.weight,
                })
                neighbor_id = rel.target_id if rel.source_id == current_id else rel.source_id
                if neighbor_id not in seen:
                    seen.add(neighbor_id)
                    queue.append((neighbor_id, depth + 1))

        return {
            "nodes": list(visited_nodes.values()),
            "edges": visited_edges,
        }

    async def find_path(self, from_id: str, to_id: str, max_depth: int = 5) -> list[str] | None:
        """BFS shortest path between two entities."""
        if from_id == to_id:
            return [from_id]

        queue: list[tuple[str, list[str]]] = [(from_id, [from_id])]
        seen: set[str] = {from_id}

        while queue:
            current, path = queue.pop(0)
            if len(path) > max_depth:
                break

            rels = await self.get_relationships(current)
            for rel in rels:
                neighbor = rel.target_id if rel.source_id == current else rel.source_id
                if neighbor == to_id:
                    return path + [neighbor]
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    async def stats(self) -> dict[str, int]:
        """Return counts of nodes and edges."""
        n = await self.conn.execute("SELECT COUNT(*) FROM nodes")
        e = await self.conn.execute("SELECT COUNT(*) FROM edges")
        return {
            "nodes": (await n.fetchone())[0],
            "edges": (await e.fetchone())[0],
        }

    # ── Helpers ───────────────────────────────────────────

    @staticmethod
    def _row_to_entity(row: Any) -> Entity:
        return Entity(
            id=row["id"],
            name=row["name"],
            entity_type=EntityType(row["entity_type"]),
            description=row["description"],
            properties=json.loads(row["properties"]) if row["properties"] else {},
            source=row["source"],
        )

    @staticmethod
    def _row_to_relationship(row: Any) -> Relationship:
        return Relationship(
            id=row["id"],
            source_id=row["source_id"],
            target_id=row["target_id"],
            relation_type=row["relation_type"],
            weight=row["weight"],
            properties=json.loads(row["properties"]) if row["properties"] else {},
        )


# ── Singleton ─────────────────────────────────────────────
_store: GraphStore | None = None


async def get_graph_store() -> GraphStore:
    global _store  # noqa: PLW0603
    if _store is None:
        from shared.config import get_settings
        _store = GraphStore(get_settings().graph_db_path)
        await _store.initialize()
    return _store
