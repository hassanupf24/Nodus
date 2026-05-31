"""Input sanitization and prompt-injection detection."""

from __future__ import annotations

import re
from typing import Any

from shared.logging_config import get_logger

logger = get_logger(__name__)

# ── Known prompt-injection patterns ────────────────────────
_INJECTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?prior\s+(instructions|context)", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(a|an)\s+", re.IGNORECASE),
    re.compile(r"system\s*:\s*", re.IGNORECASE),
    re.compile(r"\[INST\]|\[/INST\]|<<SYS>>|<\|im_start\|>", re.IGNORECASE),
    re.compile(r"```\s*(system|admin|root)", re.IGNORECASE),
    re.compile(r"override\s+(safety|content)\s+(filter|policy)", re.IGNORECASE),
    re.compile(r"pretend\s+you\s+(are|have|can)", re.IGNORECASE),
    re.compile(r"act\s+as\s+(if|though)\s+you", re.IGNORECASE),
    re.compile(r"do\s+not\s+follow\s+(your|the)\s+(rules|guidelines)", re.IGNORECASE),
]

# Characters that shouldn't appear in user-facing text
_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


class InjectionDetected(Exception):
    """Raised when a likely prompt injection is detected."""

    def __init__(self, pattern: str, text_snippet: str) -> None:
        self.pattern = pattern
        self.text_snippet = text_snippet
        super().__init__(f"Prompt injection detected: pattern={pattern!r}")


def sanitize_text(text: str, max_length: int = 100_000) -> str:
    """Strip control characters and truncate excessively long inputs.

    Returns:
        Cleaned text.
    """
    text = _CONTROL_CHAR_RE.sub("", text)
    if len(text) > max_length:
        logger.warning("security.text_truncated", original_length=len(text), max_length=max_length)
        text = text[:max_length]
    return text


def check_prompt_injection(text: str, raise_on_detect: bool = True) -> bool:
    """Scan *text* for known prompt-injection patterns.

    Args:
        text: The user input to scan.
        raise_on_detect: If ``True``, raise :class:`InjectionDetected`;
            otherwise just return ``True``.

    Returns:
        ``True`` if injection detected, ``False`` otherwise.
    """
    for pattern in _INJECTION_PATTERNS:
        match = pattern.search(text)
        if match:
            snippet = text[max(0, match.start() - 30): match.end() + 30]
            logger.warning(
                "security.injection_detected",
                pattern=pattern.pattern,
                snippet=snippet,
            )
            if raise_on_detect:
                raise InjectionDetected(pattern=pattern.pattern, text_snippet=snippet)
            return True
    return False


def sanitize_filename(name: str) -> str:
    """Remove path-traversal characters from a filename."""
    name = name.replace("..", "").replace("/", "_").replace("\\", "_")
    name = re.sub(r"[^\w.\-]", "_", name)
    return name.strip("_") or "unnamed"


def validate_payload(payload: dict[str, Any], max_depth: int = 10) -> dict[str, Any]:
    """Recursively validate a JSON payload to prevent oversized nesting."""

    def _check(obj: Any, depth: int) -> Any:
        if depth > max_depth:
            raise ValueError(f"Payload nesting exceeds max depth of {max_depth}")
        if isinstance(obj, dict):
            return {k: _check(v, depth + 1) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_check(item, depth + 1) for item in obj]
        return obj

    return _check(payload, 0)  # type: ignore[return-value]
