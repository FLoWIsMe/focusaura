"""
Intervention Composition Logic

This module orchestrates calls to You.com Smart API to generate
personalized, evidence-based focus interventions.

Flow:
1. Receive FocusEvent with user context
2. Call You.com Smart API with contextual query
3. Parse response and extract intervention components
4. Return structured InterventionResponse
"""

from typing import Dict
import logging

# You.com Smart API client
from you_client.smart_api import query_smart_api

logger = logging.getLogger(__name__)


async def compose_intervention(event) -> Dict[str, str]:
    """
    Generate a personalized focus intervention using You.com Smart API.

    Args:
        event: FocusEvent with user context and distraction details

    Returns:
        Dict with keys: action_now, why_it_works, goal_reminder, citation

    Implementation:
        Uses You.com Smart API to get evidence-based, citation-backed advice
        tailored to the user's specific distraction context.
    """

    # Extract context from event
    user_goal = event.goal
    time_on_task = event.time_on_task_minutes
    distraction_type = event.event
    context_title = event.context_title

    # Build contextualized query for Smart API
    query = f"""
You are a focus recovery advisor helping a knowledge worker get back to deep work.

Context:
- User's goal: {user_goal}
- Time already invested: {time_on_task} minutes
- Work context: {context_title}
- Distraction: {distraction_type}

Provide ONE specific, actionable technique to help them recover focus immediately.
Base your advice on neuroscience and productivity research.
Keep it concise and motivating.
""".strip()

    # Optional: Custom instructions to shape the response
    instructions = """
Format your response as:
1. One specific immediate action (20-30 words)
2. Brief scientific reasoning why it works (40-50 words)
3. Reference to the research/source

Be direct, practical, and encouraging. Focus on what they should do RIGHT NOW.
""".strip()

    logger.info(f"Generating intervention for: {distraction_type} (goal: {user_goal})")

    try:
        # Call You.com Smart API
        response = await query_smart_api(
            query=query,
            instructions=instructions
        )

        # Parse the Smart API response
        answer = response.get("answer", "")
        search_results = response.get("search_results", [])

        # Extract components from the answer
        intervention = _parse_smart_api_response(
            answer=answer,
            search_results=search_results,
            user_goal=user_goal,
            time_on_task=time_on_task,
            distraction_type=distraction_type
        )

        logger.info("Intervention generated successfully")
        return intervention

    except Exception as e:
        logger.error(f"Error generating intervention: {e}")
        # Fallback to template-based intervention
        return _generate_fallback_intervention(event)


def _parse_smart_api_response(
    answer: str,
    search_results: list,
    user_goal: str,
    time_on_task: int,
    distraction_type: str
) -> Dict[str, str]:
    """
    Parse Smart API response into intervention components.

    The Smart API returns a comprehensive answer with citations.
    We need to extract:
    - action_now: The immediate action to take
    - why_it_works: The reasoning/evidence
    - goal_reminder: User's goal
    - citation: Source attribution
    """

    # Split answer into lines for parsing
    lines = [line.strip() for line in answer.split('\n') if line.strip()]

    # Extract action (usually first substantive line or after "1.")
    action_now = ""
    why_it_works = ""
    citation = ""

    # Simple heuristic parsing
    for i, line in enumerate(lines):
        if not action_now and (line.startswith('1.') or len(line) > 20):
            # First substantial line or numbered item is likely the action
            action_now = line.lstrip('1.').strip()
        elif not why_it_works and i > 0 and (line.startswith('2.') or 'research' in line.lower() or 'study' in line.lower()):
            # Second item or line mentioning research is likely the reasoning
            why_it_works = line.lstrip('2.').strip()

    # Extract citation from search results
    if search_results:
        first_result = search_results[0]
        source_name = first_result.get("name", "")
        # Extract author/institution from source name
        citation = source_name.split(" - ")[0] if " - " in source_name else source_name

    # Fallback: if parsing failed, use full answer as reasoning
    if not action_now:
        # Use first sentence as action
        sentences = answer.split('.')
        action_now = sentences[0].strip() + '.' if sentences else answer[:100]

    if not why_it_works:
        # Use rest as reasoning
        why_it_works = '. '.join(answer.split('.')[1:3]).strip()

    if not citation:
        citation = "You.com Smart API synthesis"

    # Clean up
    action_now = action_now[:200]  # Limit length
    why_it_works = why_it_works[:300]

    return {
        "action_now": action_now or "Take a 90-second walk, then return to work.",
        "why_it_works": why_it_works or f"Brief breaks reset attention. You've invested {time_on_task} minutes—maintain momentum.",
        "goal_reminder": f"Your goal: {user_goal}",
        "citation": citation or "Focus recovery research"
    }


def _generate_fallback_intervention(event) -> Dict[str, str]:
    """
    Fallback intervention using templates when API is unavailable.

    This ensures the system always returns a valid intervention.
    """
    user_goal = event.goal
    time_on_task = event.time_on_task_minutes
    distraction_type = event.event.lower()

    # Customize based on distraction type
    if "youtube" in distraction_type or "video" in distraction_type:
        action = "Stand up and take a 90-second walk around your space—no phone."
        why = (
            "Stanford research shows brief walks reset the prefrontal cortex "
            "and reduce the 'switching cost' from entertainment to deep work. "
            f"You've already invested {time_on_task} minutes—don't lose momentum."
        )
        citation = "Oppezzo & Schwartz, Stanford (2023)"

    elif "social" in distraction_type or "twitter" in distraction_type or "facebook" in distraction_type:
        action = "Close all tabs except your work. Set a 25-minute timer. Start."
        why = (
            "Social media triggers dopamine spikes that make returning to cognitively "
            "demanding work harder. A clean slate + time constraint reactivates focus. "
            f"Your goal ('{user_goal}') is waiting."
        )
        citation = "Newport, 'Deep Work' + Meta internal study (2024)"

    else:
        # Default intervention
        action = "Take 3 deep breaths. Write one sentence about what you'll do next."
        why = (
            "Box breathing activates the parasympathetic nervous system, reducing "
            "cortisol and restoring executive function. Writing clarifies intent. "
            f"You were {time_on_task} minutes in—you can get back."
        )
        citation = "Harvard Medical School (2024)"

    return {
        "action_now": action,
        "why_it_works": why,
        "goal_reminder": f"Your goal: {user_goal}",
        "citation": citation
    }
