"""
You.com API Base Client

Provides common functionality for all You.com API clients:
- Request/response handling
- Retry logic with exponential backoff
- Error handling and fallbacks
- Logging and monitoring
"""

import httpx
import time
import logging
from typing import Dict, Any, Optional
from .config import config

# Configure logging
logging.basicConfig(level=logging.DEBUG if config.DEBUG else logging.INFO)
logger = logging.getLogger(__name__)


class YouAPIError(Exception):
    """Base exception for You.com API errors."""
    pass


class YouAPIClient:
    """Base client for You.com API interactions."""

    def __init__(self):
        self.config = config
        self.session = httpx.AsyncClient(
            timeout=config.API_TIMEOUT,
            headers=self._get_default_headers()
        )

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for API requests."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "FocusAura/0.1.0"
        }

        if config.has_api_key():
            headers["Authorization"] = f"Bearer {config.API_KEY}"

        return headers

    async def _make_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic and error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL to request
            **kwargs: Additional arguments to pass to httpx

        Returns:
            Response JSON as dict

        Raises:
            YouAPIError: If request fails after retries
        """
        last_error = None

        for attempt in range(config.MAX_RETRIES):
            try:
                if config.DEBUG:
                    logger.debug(f"API Request [{attempt + 1}/{config.MAX_RETRIES}]: {method} {url}")

                response = await self.session.request(method, url, **kwargs)

                if config.DEBUG:
                    logger.debug(f"API Response: Status {response.status_code}")

                # Success
                if response.status_code == 200:
                    return response.json()

                # Handle specific error codes
                if response.status_code == 401:
                    raise YouAPIError("Authentication failed: Invalid API key")
                elif response.status_code == 403:
                    raise YouAPIError("Forbidden: API key may not have required permissions")
                elif response.status_code == 429:
                    logger.warning(f"Rate limited, retrying in {config.RETRY_DELAY}s")
                    await self._sleep(config.RETRY_DELAY * (config.RETRY_BACKOFF ** attempt))
                    continue
                elif response.status_code >= 500:
                    logger.warning(f"Server error {response.status_code}, retrying...")
                    await self._sleep(config.RETRY_DELAY * (config.RETRY_BACKOFF ** attempt))
                    continue
                else:
                    raise YouAPIError(f"API returned status {response.status_code}: {response.text}")

            except httpx.TimeoutException as e:
                last_error = e
                logger.warning(f"Request timeout (attempt {attempt + 1}/{config.MAX_RETRIES})")
                if attempt < config.MAX_RETRIES - 1:
                    await self._sleep(config.RETRY_DELAY * (config.RETRY_BACKOFF ** attempt))

            except httpx.RequestError as e:
                last_error = e
                logger.warning(f"Request error: {e} (attempt {attempt + 1}/{config.MAX_RETRIES})")
                if attempt < config.MAX_RETRIES - 1:
                    await self._sleep(config.RETRY_DELAY * (config.RETRY_BACKOFF ** attempt))

            except YouAPIError:
                # Don't retry on authentication/permission errors
                raise

            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error: {e}")
                if attempt < config.MAX_RETRIES - 1:
                    await self._sleep(config.RETRY_DELAY)

        # All retries failed
        raise YouAPIError(f"API request failed after {config.MAX_RETRIES} attempts: {last_error}")

    async def _sleep(self, seconds: float):
        """Async sleep for retry delays."""
        import asyncio
        await asyncio.sleep(seconds)

    async def get(self, url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request."""
        return await self._make_request("GET", url, params=params)

    async def post(self, url: str, json: Optional[Dict] = None) -> Dict[str, Any]:
        """Make POST request."""
        return await self._make_request("POST", url, json=json)

    async def close(self):
        """Close the HTTP session."""
        await self.session.aclose()

    def __del__(self):
        """Cleanup on deletion."""
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.session.aclose())
        except:
            pass
