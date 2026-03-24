"""Lightweight token helpers for web quiz URLs."""

from __future__ import annotations

import base64


TOKEN_PREFIX = "mcqpy:"


def encode_quiz_token(url: str) -> str:
    """Encode a public bundle URL as an obfuscated token."""

    payload = base64.urlsafe_b64encode(url.encode("utf-8")).decode("ascii").rstrip("=")
    return f"{TOKEN_PREFIX}{payload}"


def decode_quiz_token(token: str) -> str:
    """Decode an obfuscated token back into the underlying public URL."""

    if not token.startswith(TOKEN_PREFIX):
        raise ValueError("Token must start with 'mcqpy:'.")

    payload = token[len(TOKEN_PREFIX) :]
    padding = "=" * (-len(payload) % 4)
    try:
        return base64.urlsafe_b64decode(payload + padding).decode("utf-8")
    except Exception as exc:  # pragma: no cover - defensive
        raise ValueError("Invalid token payload.") from exc
