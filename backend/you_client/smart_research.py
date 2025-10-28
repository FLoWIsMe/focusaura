"""
You.com Smart/Research API Client

This module queries You.com's Smart/Research API to synthesize
information from web search and news results into personalized,
context-aware advice for the user.

This is the "reasoning" layer that turns raw search results into
actionable micro-interventions tailored to the user's specific situation.

Supports dual-mode operation:
- Demo Mode: Returns template-based responses
- Live Mode: Calls real You.com RAG/Chat API

API Documentation: https://documentation.you.com/
"""

import logging
from typing import Dict
from .config import config
from .base_client import YouAPIClient, YouAPIError

logger = logging.getLogger(__name__)


async def query_smart_research(research_query: Dict) -> str:
    """
    Query You.com Smart/Research API for synthesized, personalized advice.

    Args:
        research_query: Dict containing:
            - user_context: User's goal, time on task, distraction type
            - web_findings: Results from web_search.py
            - recent_studies: Results from news_search.py
            - synthesis_prompt: Natural language prompt for synthesis

    Returns:
        String containing synthesized, personalized intervention advice

    Mode Behavior:
        - Demo Mode: Returns curated template responses
        - Live Mode: Calls You.com RAG/Chat API, falls back to templates on error
    """

    # Check mode
    if config.is_demo_mode():
        logger.info("Smart Research: Using demo mode (templates)")
        return _get_template_response(research_query)

    # Live mode - try real API
    if not config.has_api_key():
        logger.warning("Smart Research: Live mode but no API key - falling back to templates")
        return _get_template_response(research_query)

    # Extract context
    user_ctx = research_query.get("user_context", {})
    synthesis_prompt = research_query.get("synthesis_prompt", "")
    web_findings = research_query.get("web_findings", "")
    recent_studies = research_query.get("recent_studies", "")

    # Build comprehensive prompt for RAG
    full_prompt = f"""
{synthesis_prompt}

Context from web search:
{web_findings}

Recent research findings:
{recent_studies}

Please synthesize this information into a single, actionable recommendation
for this specific user's situation. Focus on the most effective immediate action.
    """.strip()

    logger.info("Smart Research: Querying You.com RAG/Chat API")

    try:
        client = YouAPIClient()
        
        # Try RAG endpoint first
        try:
            response = await client.post(
                config.RAG_ENDPOINT,
                json={
                    "query": full_prompt,
                    "context": {
                        "goal": user_ctx.get("goal", ""),
                        "time_on_task": user_ctx.get("time_on_task", 0),
                        "distraction": user_ctx.get("distraction", "")
                    }
                }
            )
        except:
            # Fall back to chat endpoint
            response = await client.post(
                config.CHAT_ENDPOINT,
                json={
                    "messages": [
                        {"role": "system", "content": "You are a focus recovery advisor helping knowledge workers get back to deep work."},
                        {"role": "user", "content": full_prompt}
                    ]
                }
            )

        # Extract synthesis from response
        synthesis = _extract_synthesis(response)
        logger.info("Smart Research: Successfully generated synthesis")
        return synthesis

    except YouAPIError as e:
        logger.error(f"Smart Research API error: {e} - falling back to templates")
        return _get_template_response(research_query)

    except Exception as e:
        logger.error(f"Smart Research unexpected error: {e} - falling back to templates")
        return _get_template_response(research_query)


def _extract_synthesis(response: Dict) -> str:
    """
    Extract synthesis text from API response.

    Handles multiple response formats (RAG vs Chat).
    """
    # Try RAG response format
    if "answer" in response:
        return f"Smart Synthesis (via You.com API):\n{response['answer']}"
    
    # Try chat response format
    if "choices" in response:
        choices = response.get("choices", [])
        if choices:
            message = choices[0].get("message", {})
            content = message.get("content", "")
            return f"Smart Synthesis (via You.com API):\n{content}"
    
    # Try direct message format
    if "message" in response:
        return f"Smart Synthesis (via You.com API):\n{response['message']}"
    
    logger.warning("Could not extract synthesis from API response")
    return "Smart Synthesis: Unable to parse API response"


def _get_template_response(research_query: Dict) -> str:
    """
    Return template-based response for demo mode or fallback.

    Customizes response based on user context.
    """
    user_ctx = research_query.get("user_context", {})
    time_on_task = user_ctx.get("time_on_task", 0)
    goal = user_ctx.get("goal", "your task")
    distraction = user_ctx.get("distraction", "")

    # Customize based on distraction and time investment
    if time_on_task >= 30:
        investment_note = f"You've already invested {time_on_task} minutes - that momentum is valuable."
    else:
        investment_note = "Getting back on track quickly will save you significant time."

    if "youtube" in distraction.lower() or "video" in distraction.lower():
        action = "a 90-second physical reset (walk or stretch) followed immediately by a 25-minute time-boxed work block"
        reasoning = "This combines Stanford's context-switch research (physical movement resets attention) with MIT's break duration findings"
    elif "social" in distraction.lower():
        action = "closing all tabs, setting a visible 25-minute timer, and writing one sentence about your next action"
        reasoning = "This creates a clean slate (reduces cognitive load from social media) and activates implementation intentions"
    else:
        action = "a 90-second physical reset followed by a clear, time-boxed work session"
        reasoning = "Brief physical activity resets the prefrontal cortex while time constraints activate focus"

    return (
        f"Smart Synthesis:\n"
        f"Given your context ('{goal}', {time_on_task} minutes invested), "
        f"the optimal recovery action is {action}. "
        f"{reasoning}. {investment_note}\n"
        "[Source: Synthesized from focus recovery research]"
    )
