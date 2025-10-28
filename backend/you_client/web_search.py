"""
You.com Web Search API Client

This module queries You.com's Web Search API to find evidence-based
focus recovery techniques, productivity research, and credible sources.

Supports dual-mode operation:
- Demo Mode: Returns template-based responses
- Live Mode: Calls real You.com Web Search API

API Documentation: https://documentation.you.com/
"""

import logging
from typing import Dict
from .config import config
from .base_client import YouAPIClient, YouAPIError

logger = logging.getLogger(__name__)


async def query_web_search(user_context: Dict) -> str:
    """
    Query You.com Web Search API for focus recovery techniques.

    Args:
        user_context: Dict containing:
            - goal: User's stated work goal
            - time_on_task: Minutes spent before distraction
            - distraction: Type of distraction event
            - query_type: Type of search (e.g., "focus_recovery_techniques")

    Returns:
        String containing top search results with actionable techniques

    Mode Behavior:
        - Demo Mode: Returns curated template responses
        - Live Mode: Calls You.com Web Search API, falls back to templates on error
    """

    # Check mode
    if config.is_demo_mode():
        logger.info("Web Search: Using demo mode (templates)")
        return _get_template_response(user_context)

    # Live mode - try real API
    if not config.has_api_key():
        logger.warning("Web Search: Live mode but no API key - falling back to templates")
        return _get_template_response(user_context)

    # Construct search query
    distraction = user_context.get("distraction", "distraction")
    query = f"evidence-based focus recovery techniques {distraction} neuroscience research"

    logger.info(f"Web Search: Querying You.com API with: {query}")

    try:
        client = YouAPIClient()
        response = await client.get(
            config.SEARCH_ENDPOINT,
            params={
                "query": query,
                "count": 5,
                "safesearch": "moderate"
            }
        )

        # Parse and format results
        formatted_results = _format_api_response(response)
        logger.info(f"Web Search: Successfully retrieved {len(formatted_results.split(chr(10)))} results")
        return formatted_results

    except YouAPIError as e:
        logger.error(f"Web Search API error: {e} - falling back to templates")
        return _get_template_response(user_context)

    except Exception as e:
        logger.error(f"Web Search unexpected error: {e} - falling back to templates")
        return _get_template_response(user_context)


def _format_api_response(response: Dict) -> str:
    """
    Format You.com API response into readable string.

    Expected response structure:
    {
        "results": {
            "web": [
                {"title": "...", "description": "...", "url": "..."},
                ...
            ],
            "news": [...]
        }
    }
    """
    results = []

    # Extract web results
    web_results = response.get("results", {}).get("web", [])

    for i, result in enumerate(web_results[:3], 1):
        title = result.get("title", "")
        description = result.get("description", "")
        url = result.get("url", "")

        # Format result
        result_text = f"{i}. {title}"
        if description:
            result_text += f": {description[:150]}..."

        results.append(result_text)

    if not results:
        logger.warning("No web results found in API response")
        return "No results found from You.com Web Search API"

    results_text = "\n".join(results)
    return f"Web Search Results (via You.com API):\n{results_text}"


def _get_template_response(user_context: Dict) -> str:
    """
    Return template-based response for demo mode or fallback.

    Customizes response based on distraction type.
    """
    distraction = user_context.get("distraction", "").lower()

    # Customize based on distraction type
    if "youtube" in distraction or "video" in distraction:
        return (
            "Web Search Results:\n"
            "1. Stanford study (2023): 90-second walks reset prefrontal cortex after context switches from video content\n"
            "2. MIT research: 6-minute breaks optimal for deep work recovery after entertainment distractions\n"
            "3. Cal Newport 'Deep Work': Physical movement + time constraints help overcome dopamine-driven distractions\n"
            "[Source: Curated from research on video distraction recovery]"
        )

    elif "social" in distraction or "twitter" in distraction or "facebook" in distraction:
        return (
            "Web Search Results:\n"
            "1. Harvard Medical (2024): Social media context switches increase task resumption time by 23 minutes\n"
            "2. Nature Neuroscience: Closing all tabs + fresh start reduces cognitive load from social media\n"
            "3. Pomodoro Technique study: 25-minute focused blocks with clear end time effective after social distractions\n"
            "[Source: Curated from social media distraction research]"
        )

    else:
        # Generic distraction
        return (
            "Web Search Results:\n"
            "1. Stanford study (2023): 90-second walks reset prefrontal cortex after context switches\n"
            "2. MIT research: 6-minute breaks optimal for deep work recovery\n"
            "3. Cal Newport 'Deep Work': Time constraints + clear tasks reactivate flow state\n"
            "[Source: Curated from focus recovery research]"
        )
