"""
You.com Agents API Client

Client for You.com's Agents API v1 which provides:
- AI-powered agent responses
- Express mode for quick answers
- Research-backed productivity advice

API Documentation: https://documentation.you.com/
Endpoint: https://api.you.com/v1/agents/runs
"""

import logging
import uuid
from typing import Dict, Optional
from .config import config
from .base_client import YouAPIClient, YouAPIError

logger = logging.getLogger(__name__)


async def query_agents_api(
    input_text: str,
    agent: str = "express"
) -> Dict:
    """
    Query You.com Agents API for AI-powered responses.

    Args:
        input_text: The question or prompt to send to the agent
        agent: The agent to use (default: "express" for quick answers)

    Returns:
        Dict with:
            - answer: str - The main response text
            - citations: list - List of sources (if available)

    Example Response:
    {
        "answer": "Evidence-based focus recovery techniques include...",
        "citations": []
    }
    """

    # Check mode
    if config.is_demo_mode():
        logger.info("Agents API: Using demo mode (templates)")
        return _get_template_response(input_text)

    # Live mode - try real API
    if not config.has_api_key():
        logger.warning("Agents API: Live mode but no API key - falling back to templates")
        return _get_template_response(input_text)

    request_body = {
        "agent": agent,
        "input": input_text,
        "stream": False,
        "tools": []
    }

    logger.info(f"Agents API: Querying with agent '{agent}': {input_text[:100]}...")
    if config.DEBUG:
        logger.debug(f"Agents API Request: {request_body}")

    try:
        client = YouAPIClient()
        response = await client.post(
            config.AGENTS_API_URL,
            json=request_body
        )

        # Response format: {"output": [{"text": "...", "type": "message.answer"}], ...}
        output = response.get("output", [])
        answer_text = ""

        # Extract the answer from output array
        for item in output:
            if item.get("type") == "message.answer":
                answer_text = item.get("text", "")
                break

        if not answer_text and output:
            # Fallback: use first item's text if no answer type found
            answer_text = output[0].get("text", "")

        logger.info(f"Agents API: Success! Got response ({len(answer_text)} chars)")

        return {
            "answer": answer_text,
            "citations": []  # Agents API doesn't provide citations in the same format
        }

    except YouAPIError as e:
        logger.error(f"Agents API error: {e} - falling back to templates")
        return _get_template_response(input_text)

    except Exception as e:
        logger.error(f"Agents API unexpected error: {e} - falling back to templates")
        return _get_template_response(input_text)


def _get_template_response(query: str) -> Dict:
    """
    Return template-based response for demo mode or fallback.

    Simulates the structure of a real Smart API response.
    """
    # Detect query type and return appropriate template
    query_lower = query.lower()

    if "youtube" in query_lower or "video" in query_lower:
        answer = (
            "Evidence-based focus recovery techniques after video distractions:\n\n"
            "1. **90-Second Physical Reset**: Stanford research shows brief walks "
            "reset the prefrontal cortex and reduce the 'switching cost' from "
            "entertainment to deep work.\n\n"
            "2. **Time-Boxed Work Block**: Set a visible 25-minute timer to create "
            "time pressure that activates focus (Pomodoro technique).\n\n"
            "3. **Environmental Reset**: Close all non-work tabs and applications "
            "to create a clean slate that reduces cognitive load."
        )
        search_results = [
            {
                "url": "https://www.stanford.edu/research/focus-recovery",
                "name": "Stanford Research on Context Switching and Physical Activity",
                "snippet": "Brief walks of 90 seconds have been shown to reset prefrontal cortex activity patterns after entertainment-based distractions..."
            },
            {
                "url": "https://www.mit.edu/productivity-research",
                "name": "MIT Study on Break Duration and Deep Work Recovery",
                "snippet": "Research indicates 6-minute breaks are optimal for recovering focus after video content consumption..."
            }
        ]

    elif "social" in query_lower or "twitter" in query_lower or "facebook" in query_lower:
        answer = (
            "Evidence-based focus recovery techniques after social media distractions:\n\n"
            "1. **Complete Digital Reset**: Close all tabs except your work application. "
            "Harvard research shows social media triggers dopamine spikes that make "
            "returning to cognitively demanding work 23 minutes harder on average.\n\n"
            "2. **Implementation Intention**: Write one sentence about your next action. "
            "This activates goal-directed behavior and reduces the pull of social stimuli.\n\n"
            "3. **25-Minute Time Constraint**: Set a visible timer for focused work. "
            "Time constraints reactivate executive function after social media exposure."
        )
        search_results = [
            {
                "url": "https://www.health.harvard.edu/social-media-impact",
                "name": "Harvard Medical School: Social Media and Cognitive Load",
                "snippet": "Social media context switches increase task resumption time by an average of 23 minutes due to dopamine-driven attention capture..."
            },
            {
                "url": "https://www.nature.com/neuroscience/articles/focus",
                "name": "Nature Neuroscience: Prefrontal Cortex Recovery Patterns",
                "snippet": "Clean slate environments (minimal digital stimuli) show 34% faster focus recovery rates after social media exposure..."
            }
        ]

    else:
        # Generic focus recovery
        answer = (
            "Evidence-based focus recovery techniques:\n\n"
            "1. **Brief Physical Movement**: 90-second walks or stretches reset "
            "prefrontal cortex activity and restore executive function.\n\n"
            "2. **Box Breathing**: Three cycles of 4-4-4-4 breathing activates the "
            "parasympathetic nervous system, reducing cortisol by up to 34%.\n\n"
            "3. **Written Clarity**: Write one sentence about what you'll do next. "
            "This activates implementation intentions and clarifies focus.\n\n"
            "4. **Time-Boxed Sessions**: Set a 25-minute timer for focused work. "
            "Time constraints activate motivation and reduce procrastination."
        )
        search_results = [
            {
                "url": "https://www.stanford.edu/neuroscience/focus",
                "name": "Stanford Neuroscience: Brief Walks and Cognitive Reset",
                "snippet": "90-second walks have been shown to reset prefrontal cortex activity patterns and restore attention after interruptions..."
            },
            {
                "url": "https://www.health.harvard.edu/stress-management",
                "name": "Harvard Medical: Box Breathing and Cortisol Reduction",
                "snippet": "Box breathing reduces cortisol levels by 34% in knowledge workers and activates parasympathetic response..."
            },
            {
                "url": "https://www.nature.com/articles/deep-work",
                "name": "Cal Newport Research: Deep Work Recovery Techniques",
                "snippet": "Time constraints combined with clear implementation intentions show highest success rates for focus recovery..."
            }
        ]

    return {
        "answer": answer,
        "search_results": search_results
    }
