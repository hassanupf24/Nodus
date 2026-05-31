"""Query analyzer — parse, expand, and classify search queries."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class AnalyzedQuery:
    """Result of analysing a raw user query."""

    original: str
    normalized: str
    terms: list[str] = field(default_factory=list)
    intent: str = "search"  # search | question | navigation | command
    is_question: bool = False
    negations: list[str] = field(default_factory=list)
    filters_detected: dict[str, str] = field(default_factory=dict)
    expanded_terms: list[str] = field(default_factory=list)


_QUESTION_STARTERS = frozenset({
    "who", "what", "where", "when", "why", "how", "which",
    "is", "are", "was", "were", "do", "does", "did",
    "can", "could", "would", "should", "will",
})

_FILTER_PATTERN = re.compile(r"(\w+):([\w\-./]+)")
_NEGATION_PATTERN = re.compile(r"-(\w+)")
_STOPWORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "shall", "can", "it",
    "its", "this", "that", "these", "those",
})


def analyze_query(raw_query: str) -> AnalyzedQuery:
    """Parse a raw query string into structured components."""
    normalized = raw_query.strip().lower()
    result = AnalyzedQuery(original=raw_query, normalized=normalized)

    # Detect inline filters (e.g. source:readme.md)
    for match in _FILTER_PATTERN.finditer(normalized):
        result.filters_detected[match.group(1)] = match.group(2)
    # Remove filter tokens from the query
    clean = _FILTER_PATTERN.sub("", normalized).strip()

    # Detect negations (e.g. -python)
    for match in _NEGATION_PATTERN.finditer(clean):
        result.negations.append(match.group(1))
    clean = _NEGATION_PATTERN.sub("", clean).strip()

    # Tokenize
    tokens = re.findall(r"\w+", clean)
    result.terms = [t for t in tokens if t not in _STOPWORDS]

    # Intent detection
    first_word = tokens[0] if tokens else ""
    if first_word in _QUESTION_STARTERS or clean.endswith("?"):
        result.intent = "question"
        result.is_question = True
    elif first_word in {"go", "open", "show", "navigate", "find"}:
        result.intent = "navigation"

    # Simple synonym expansion
    expansion_map: dict[str, list[str]] = {
        "ml": ["machine learning"],
        "ai": ["artificial intelligence"],
        "db": ["database"],
        "js": ["javascript"],
        "ts": ["typescript"],
        "py": ["python"],
        "api": ["application programming interface"],
        "auth": ["authentication", "authorization"],
    }
    for term in result.terms:
        if term in expansion_map:
            result.expanded_terms.extend(expansion_map[term])

    return result
