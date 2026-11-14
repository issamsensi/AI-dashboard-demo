"""Application configuration helpers.

This module centralizes paths, provider selection, and model defaults so the demo
can be extended later without threading environment lookups through every layer.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
DATABASE_DIR = ROOT_DIR / "database"
DB_PATH = DATABASE_DIR / "ecommerce.db"


@dataclass(frozen=True)
class AIConfig:
    """Resolved AI provider settings."""

    provider: str
    model: str
    api_key: str | None
    base_url: str | None


def get_ai_config() -> AIConfig:
    """Return the current model configuration.

    Groq is the default because it is fast for tool-calling demos, but the app
    can switch to Mistral by setting `AI_PROVIDER=mistral`.
    """

    provider = os.getenv("AI_PROVIDER", "groq").strip().lower()
    if provider not in {"groq", "mistral"}:
        provider = "groq"

    if provider == "mistral":
        return AIConfig(
            provider=provider,
            model=os.getenv("MISTRAL_MODEL", "mistral-large-latest"),
            api_key=os.getenv("MISTRAL_API_KEY"),
            base_url=os.getenv("MISTRAL_BASE_URL", "https://api.mistral.ai/v1"),
        )

    return AIConfig(
        provider=provider,
        model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        api_key=os.getenv("GROQ_API_KEY"),
        base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
    )
