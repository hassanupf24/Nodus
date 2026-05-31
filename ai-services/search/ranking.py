"""Ranking engine — reciprocal rank fusion, temporal boosting, recency weighting."""

from __future__ import annotations

import math
import time
from typing import Any


def reciprocal_rank_fusion(
    ranked_lists: list[list[dict[str, Any]]],
    k: int = 60,
    id_key: str = "id",
) -> list[dict[str, Any]]:
    """Merge multiple ranked result lists using Reciprocal Rank Fusion (RRF).

    RRF score for document d = Σ  1 / (k + rank_i(d))

    Args:
        ranked_lists: Each inner list is a ranked search result (best first).
                      Each item must have an *id_key* field.
        k: Smoothing constant (default 60, per the original RRF paper).
        id_key: Key to identify unique documents.

    Returns:
        Merged list sorted by RRF score (highest first).
    """
    scores: dict[str, float] = {}
    docs: dict[str, dict[str, Any]] = {}

    for results in ranked_lists:
        for rank, doc in enumerate(results):
            doc_id = str(doc[id_key])
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
            if doc_id not in docs:
                docs[doc_id] = doc

    merged = []
    for doc_id, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        entry = {**docs[doc_id], "rrf_score": round(score, 6)}
        merged.append(entry)

    return merged


def temporal_boost(
    results: list[dict[str, Any]],
    half_life_days: float = 30.0,
    timestamp_key: str = "created_at",
    score_key: str = "score",
) -> list[dict[str, Any]]:
    """Apply exponential time-decay boosting to search results.

    Recent documents get a higher boost; older ones decay toward zero.

    Args:
        results: Search results, each with a timestamp and a score.
        half_life_days: Days until the boost halves.
        timestamp_key: Payload key containing a UNIX timestamp.
        score_key: Key containing the original score.
    """
    now = time.time()
    decay = math.log(2) / (half_life_days * 86400)

    boosted = []
    for r in results:
        ts = r.get("payload", {}).get(timestamp_key) or r.get(timestamp_key) or now
        age_seconds = max(0.0, now - float(ts))
        boost = math.exp(-decay * age_seconds)
        original_score = r.get(score_key, 0.0)
        r["boosted_score"] = round(original_score * (0.7 + 0.3 * boost), 6)
        boosted.append(r)

    boosted.sort(key=lambda x: x["boosted_score"], reverse=True)
    return boosted


def recency_weighted_score(
    score: float,
    created_at: float,
    weight: float = 0.2,
    max_age_days: float = 365.0,
) -> float:
    """Blend a relevance score with a recency factor.

    Args:
        score: Original relevance score (0–1).
        created_at: UNIX timestamp of the document.
        weight: How much recency influences the final score (0–1).
        max_age_days: Documents older than this get zero recency bonus.

    Returns:
        Blended score.
    """
    age_days = (time.time() - created_at) / 86400
    recency = max(0.0, 1.0 - age_days / max_age_days)
    return round(score * (1 - weight) + recency * weight, 6)
