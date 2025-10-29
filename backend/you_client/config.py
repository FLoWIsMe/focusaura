"""
You.com API Configuration

Centralized configuration management for You.com API integration.
Supports dual-mode operation: demo (templates) vs live (real APIs).
"""

import os
from typing import Literal
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class YouAPIConfig:
    """Configuration for You.com API integration."""

    # API Credentials
    API_KEY: str = os.getenv("YOU_API_KEY", "")

    # Mode: "demo" (templates) or "live" (real API calls)
    MODE: Literal["demo", "live"] = os.getenv("YOU_API_MODE", "demo")  # type: ignore

    # API Endpoints (based on You.com API documentation)
    # Smart API is the main endpoint for RAG-powered responses
    SMART_API_URL: str = "https://chat-api.you.com/smart"

    # Legacy endpoints (may not be accessible with all API keys)
    BASE_URL: str = "https://api.ydc-index.io"
    SEARCH_ENDPOINT: str = f"{BASE_URL}/search"
    NEWS_ENDPOINT: str = f"{BASE_URL}/news"

    # Timeouts
    API_TIMEOUT: float = float(os.getenv("YOU_API_TIMEOUT", "10"))

    # Caching
    CACHE_ENABLED: bool = os.getenv("YOU_API_CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL: int = int(os.getenv("YOU_API_CACHE_TTL", "300"))

    # Logging
    DEBUG: bool = os.getenv("YOU_API_DEBUG", "false").lower() == "true"

    # Retry Logic
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0  # seconds
    RETRY_BACKOFF: float = 2.0  # exponential backoff multiplier

    @classmethod
    def is_demo_mode(cls) -> bool:
        """Check if running in demo mode (templates)."""
        return cls.MODE.lower() == "demo"

    @classmethod
    def is_live_mode(cls) -> bool:
        """Check if running in live mode (real APIs)."""
        return cls.MODE.lower() == "live"

    @classmethod
    def has_api_key(cls) -> bool:
        """Check if API key is configured."""
        return bool(cls.API_KEY and len(cls.API_KEY) > 0)

    @classmethod
    def get_mode_description(cls) -> str:
        """Get human-readable mode description."""
        if cls.is_demo_mode():
            return "Demo Mode (Template Responses)"
        elif cls.is_live_mode() and cls.has_api_key():
            return "Live Mode (Real You.com APIs)"
        else:
            return "Live Mode (No API Key - Fallback to Templates)"

    @classmethod
    def validate(cls) -> dict:
        """Validate configuration and return status."""
        status = {
            "mode": cls.MODE,
            "mode_description": cls.get_mode_description(),
            "api_key_configured": cls.has_api_key(),
            "cache_enabled": cls.CACHE_ENABLED,
            "debug": cls.DEBUG,
            "ready_for_live_mode": cls.has_api_key() and cls.is_live_mode(),
        }

        # Add warnings
        warnings = []
        if cls.is_live_mode() and not cls.has_api_key():
            warnings.append("Live mode enabled but no API key configured - will fall back to templates")
        if cls.has_api_key() and cls.is_demo_mode():
            warnings.append("API key configured but running in demo mode - not making real API calls")

        status["warnings"] = warnings
        return status


# Export singleton config
config = YouAPIConfig()
