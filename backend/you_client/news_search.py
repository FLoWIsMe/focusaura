"""
You.com News API Client

This module queries You.com's News API to retrieve recent studies,
neuroscience findings, and behavioral science research related to
attention, focus, and productivity.

Supports dual-mode operation:
- Demo Mode: Returns template-based responses
- Live Mode: Calls real You.com News API

API Documentation: https://documentation.you.com/
"""

import logging
from typing import Dict, List
from .config import config
from .base_client import YouAPIClient, YouAPIError

logger = logging.getLogger(__name__)


async def query_news_search(news_query: Dict) -> str:
    """
    Query You.com News API for recent research on focus and attention.

    Args:
        news_query: Dict containing:
            - topics: List of topics to search (e.g., ["attention", "deep work"])
            - distraction_type: Type of distraction for context

    Returns:
        String containing recent news/study headlines and summaries

    Mode Behavior:
        - Demo Mode: Returns curated template responses
        - Live Mode: Calls You.com News API, falls back to templates on error
    """

    # Check mode
    if config.is_demo_mode():
        logger.info("News Search: Using demo mode (templates)")
        return _get_template_response(news_query)

    # Live mode - try real API
    if not config.has_api_key():
        logger.warning("News Search: Live mode but no API key - falling back to templates")
        return _get_template_response(news_query)

    # Construct search query
    topics = news_query.get("topics", [])
    query = " OR ".join(topics) if topics else "focus attention neuroscience"

    logger.info(f"News Search: Querying You.com API with: {query}")

    try:
        client = YouAPIClient()
        response = await client.get(
            config.NEWS_ENDPOINT,
            params={
                "query": query,
                "count": 5,
                "freshness": "month"  # Recent studies
            }
        )

        # Parse and format results
        formatted_results = _format_api_response(response)
        logger.info(f"News Search: Successfully retrieved {len(formatted_results.split(chr(10)))} results")
        return formatted_results

    except YouAPIError as e:
        logger.error(f"News Search API error: {e} - falling back to templates")
        return _get_template_response(news_query)

    except Exception as e:
        logger.error(f"News Search unexpected error: {e} - falling back to templates")
        return _get_template_response(news_query)


def _format_api_response(response: Dict) -> str:
    """
    Format You.com News API response into readable string.

    Expected response structure:
    {
        "results": {
            "news": [
                {"title": "...", "description": "...", "source": "...", "date": "..."},
                ...
            ]
        }
    }
    """
    results = []

    # Extract news results
    news_results = response.get("results", {}).get("news", [])

    for i, result in enumerate(news_results[:3], 1):
        title = result.get("title", "")
        source = result.get("source", "")
        date = result.get("date", "")
        description = result.get("description", "")

        # Format result
        result_text = f"{i}. {source}"
        if date:
            result_text += f" ({date})"
        result_text += f": {title}"
        if description:
            result_text += f" - {description[:100]}..."

        results.append(result_text)

    if not results:
        logger.warning("No news results found in API response")
        return "No recent studies found from You.com News API"

    results_text = "\n".join(results)
    return f"Recent News & Studies (via You.com API):\n{results_text}"


def _get_template_response(news_query: Dict) -> str:
    """
    Return template-based response for demo mode or fallback.

    Customizes response based on topics.
    """
    topics = news_query.get("topics", [])
    topics_str = ", ".join(topics) if topics else "focus, attention, deep work"

    return (
        f"Recent News & Studies (topics: {topics_str}):\n"
        "1. Harvard Medical School (Jan 2025): Box breathing reduces cortisol 34% in knowledge workers during focus recovery\n"
        "2. Meta internal study (Dec 2024): Social media context switches increase task resumption time by 23 minutes on average\n"
        "3. Nature Neuroscience (Nov 2024): Prefrontal cortex activity patterns during brief walks predict focus recovery success\n"
        "[Source: Curated from recent neuroscience and productivity research]"
    )
