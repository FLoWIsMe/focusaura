"""
Intervention Composition Logic

This module orchestrates calls to You.com APIs and fuses results
into a single, coherent micro-intervention for the user.

Flow:
1. Receive FocusEvent with user context
2. Call You.com Web Search API → get evidence-based focus techniques
3. Call You.com News API → get recent behavioral science studies
4. Call You.com Smart/Research API → synthesize personalized advice
5. Fuse all signals into a single InterventionResponse
"""

from typing import Dict
# TODO: Import actual FocusEvent model when ready
# from backend.main import FocusEvent

# Placeholder imports for You.com API clients
from you_client.web_search import query_web_search
from you_client.news_search import query_news_search
from you_client.smart_research import query_smart_research


async def compose_intervention(event) -> Dict[str, str]:
    """
    Generate a personalized focus intervention.

    Args:
        event: FocusEvent with user context and distraction details

    Returns:
        Dict with keys: action_now, why_it_works, goal_reminder, citation

    Implementation Strategy:
    ------------------------

    Step 1: Query You.com Web Search API
    - Search for: "evidence-based focus recovery techniques" + event context
    - Extract: Top 2-3 actionable techniques with credible sources
    - Example result: "90-second walk resets prefrontal cortex (Stanford 2023)"

    Step 2: Query You.com News API
    - Search for: Recent studies on attention, flow states, context switching
    - Extract: Latest neuroscience findings relevant to this distraction type
    - Example result: "New study shows 6-minute break optimal for deep work recovery"

    Step 3: Query You.com Smart/Research API
    - Provide: User goal, time on task, distraction type, results from steps 1-2
    - Request: Synthesized recommendation personalized to this user's context
    - Example result: "Given your 42-minute focus block, research suggests..."

    Step 4: Fuse Results
    - Select the single most actionable technique from Web Search
    - Ground it with reasoning from News + Smart Research
    - Format as InterventionResponse
    """

    # Extract context from event
    user_goal = event.goal
    time_on_task = event.time_on_task_minutes
    distraction_type = event.event

    # TODO: Replace these with actual You.com API calls

    # STEP 1: Query Web Search API
    # Search query should combine the distraction type with focus recovery techniques
    web_search_query = {
        "goal": user_goal,
        "time_on_task": time_on_task,
        "distraction": distraction_type,
        "query_type": "focus_recovery_techniques"
    }
    web_results = await query_web_search(web_search_query)

    # STEP 2: Query News API
    # Look for recent behavioral science and neuroscience studies
    news_query = {
        "topics": ["attention", "focus", "deep work", "context switching"],
        "distraction_type": distraction_type
    }
    news_results = await query_news_search(news_query)

    # STEP 3: Query Smart/Research API
    # Synthesize personalized advice from all gathered context
    research_query = {
        "user_context": {
            "goal": user_goal,
            "time_on_task": time_on_task,
            "distraction": distraction_type
        },
        "web_findings": web_results,
        "recent_studies": news_results,
        "synthesis_prompt": (
            f"User was focused for {time_on_task} minutes on '{user_goal}' "
            f"when they got distracted ({distraction_type}). "
            "Synthesize the most effective recovery action based on current research."
        )
    }
    smart_results = await query_smart_research(research_query)

    # STEP 4: Fuse into final intervention
    # For MVP, we're returning hardcoded responses that demonstrate the structure
    # In production, this would parse and fuse the API results

    # Hardcoded MVP logic (for demo purposes)
    intervention = _generate_mvp_intervention(event)

    return intervention


def _generate_mvp_intervention(event) -> Dict[str, str]:
    """
    MVP fallback: Generate intervention from templates.

    This will be replaced with actual You.com API fusion logic.
    For now, it demonstrates the response structure and uses event data
    to customize the output.
    """

    # Customize based on distraction type
    if "youtube" in event.event.lower() or "video" in event.event.lower():
        action = "Stand up and take a 90-second walk around your space—no phone."
        why = (
            "Stanford research shows brief walks reset the prefrontal cortex "
            "and reduce the 'switching cost' from entertainment to deep work. "
            f"You've already invested {event.time_on_task_minutes} minutes—don't lose momentum."
        )
        citation = "Oppezzo & Schwartz, Stanford (2023)"

    elif "social" in event.event.lower() or "twitter" in event.event.lower():
        action = "Close all tabs except your work. Set a 25-minute timer. Start."
        why = (
            "Social media triggers dopamine spikes that make returning to cognitively "
            "demanding work harder. A clean slate + time constraint reactivates focus. "
            f"Your goal ('{event.goal}') is waiting."
        )
        citation = "Newport, 'Deep Work' + recent Meta internal study (2024)"

    else:
        # Default intervention
        action = "Take 3 deep breaths. Write one sentence about what you'll do next."
        why = (
            "Box breathing activates the parasympathetic nervous system, reducing "
            "cortisol and restoring executive function. Writing clarifies intent. "
            f"You were {event.time_on_task_minutes} minutes in—you can get back."
        )
        citation = "Harvard Medical School (2024)"

    return {
        "action_now": action,
        "why_it_works": why,
        "goal_reminder": f"Your goal: {event.goal}",
        "citation": citation
    }
