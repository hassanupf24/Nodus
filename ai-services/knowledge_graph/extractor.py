"""Entity extractor — uses local LLM to extract entities and relationships from text."""

from __future__ import annotations

import json
import re
from typing import Any

from knowledge_graph.schemas import Entity, EntityType, Relationship
from shared.logging_config import get_logger

logger = get_logger(__name__)

_EXTRACTION_PROMPT = """Extract all named entities and their relationships from the following text.

Return a JSON object with two arrays:
1. "entities": each with "name", "entity_type" (person/organization/concept/topic/location/event/technology/other), "description" (1 sentence)
2. "relationships": each with "source" (entity name), "target" (entity name), "relation_type" (e.g. "works_at", "related_to", "mentions", "uses", "created_by")

Text:
---
{text}
---

Return ONLY valid JSON, no markdown fences, no explanation."""


class EntityExtractor:
    """Extract entities and relationships from text using the local LLM."""

    def __init__(self, model: str = "llama3.2", temperature: float = 0.1) -> None:
        self._model = model
        self._temperature = temperature

    async def extract(self, text: str, source: str | None = None) -> dict[str, list]:
        """Extract entities and relationships from *text* via LLM.

        Returns dict with ``entities`` and ``relationships`` keys.
        """
        from llm_runtime.ollama_client import OllamaClient
        from shared.config import get_settings

        client = OllamaClient(
            base_url=get_settings().ollama_base_url,
            timeout=get_settings().request_timeout,
        )

        prompt = _EXTRACTION_PROMPT.format(text=text[:4000])  # Truncate to fit context

        try:
            result = await client.generate(
                model=self._model,
                prompt=prompt,
                stream=False,
                temperature=self._temperature,
                max_tokens=2048,
            )
            raw_text = result.get("response", "") if isinstance(result, dict) else ""
            parsed = self._parse_extraction(raw_text)
        except Exception as exc:
            logger.warning("extractor.llm_failed", error=str(exc))
            parsed = self._rule_based_extract(text)
        finally:
            await client.close()

        entities: list[Entity] = []
        relationships: list[Relationship] = []

        entity_name_to_id: dict[str, str] = {}

        for e in parsed.get("entities", []):
            try:
                etype = EntityType(e.get("entity_type", "concept").lower())
            except ValueError:
                etype = EntityType.OTHER
            entity = Entity(
                name=e["name"],
                entity_type=etype,
                description=e.get("description"),
                source=source,
            )
            entities.append(entity)
            entity_name_to_id[entity.name.lower()] = entity.id or entity.name

        for r in parsed.get("relationships", []):
            src_name = r.get("source", "").lower()
            tgt_name = r.get("target", "").lower()
            src_id = entity_name_to_id.get(src_name, src_name)
            tgt_id = entity_name_to_id.get(tgt_name, tgt_name)
            relationships.append(
                Relationship(
                    source_id=src_id,
                    target_id=tgt_id,
                    relation_type=r.get("relation_type", "related_to"),
                )
            )

        logger.info(
            "extractor.completed",
            entities=len(entities),
            relationships=len(relationships),
        )
        return {"entities": entities, "relationships": relationships}

    @staticmethod
    def _parse_extraction(raw: str) -> dict[str, Any]:
        """Attempt to parse JSON from potentially noisy LLM output."""
        # Try direct parse
        raw = raw.strip()
        # Strip markdown fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        # Try to find JSON object in the text
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        logger.warning("extractor.parse_failed", raw_length=len(raw))
        return {"entities": [], "relationships": []}

    @staticmethod
    def _rule_based_extract(text: str) -> dict[str, list[dict[str, str]]]:
        """Fallback: basic regex-based entity extraction for when LLM is unavailable."""
        entities: list[dict[str, str]] = []
        seen: set[str] = set()

        # Capitalized phrases (likely proper nouns)
        for match in re.finditer(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b", text):
            name = match.group(1)
            if name.lower() not in seen and len(name) > 2:
                seen.add(name.lower())
                entities.append({
                    "name": name,
                    "entity_type": "concept",
                    "description": f"Extracted from text: {name}",
                })

        return {"entities": entities[:50], "relationships": []}
