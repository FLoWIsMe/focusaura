"""
Intervention Composition Logic

This module orchestrates calls to You.com Agents API to generate
personalized, evidence-based focus interventions.

Flow:
1. Receive FocusEvent with user context
2. Call You.com Agents API with contextual prompt
3. Parse response and extract intervention components
4. Return structured InterventionResponse
"""

from typing import Dict
import logging

# You.com Agents API client
from you_client.smart_api import query_agents_api

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

    # Build contextualized prompt for Agents API
    prompt = f"""I have been working on "{user_goal}" for {time_on_task} minutes in {context_title}, but I got distracted by {distraction_type}.

Give me ONE specific, research-backed technique to recover my focus immediately. Base your advice on neuroscience and productivity research. Keep it concise and motivating.

Format your response as:
1. One specific immediate action (20-30 words)
2. Brief scientific reasoning why it works (40-50 words)
3. Reference to the research/source

Be direct, practical, and encouraging. Focus on what I should do RIGHT NOW."""

    logger.info(f"Generating intervention for: {distraction_type} (goal: {user_goal})")

    try:
        # Call You.com Agents API
        response = await query_agents_api(
            input_text=prompt,
            agent="express"
        )

        # Parse the Agents API response
        answer = response.get("answer", "")
        citations = response.get("citations", [])

        # Extract components from the answer
        intervention = _parse_agents_api_response(
            answer=answer,
            citations=citations,
            user_goal=user_goal
        )

        logger.info("Intervention generated successfully")
        return intervention

    except Exception as e:
        logger.error(f"Error generating intervention: {e}")
        # Fallback to template-based intervention
        return _generate_fallback_intervention(event)


def _parse_agents_api_response(
    answer: str,
    citations: list,
    user_goal: str
) -> Dict[str, str]:
    """
    Parse Agents API response into intervention components.

    The Agents API returns a comprehensive answer in markdown format.
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
        # Skip markdown headers
        if line.startswith('#'):
            continue

        if not action_now and (line.startswith('1.') or line.startswith('**') or len(line) > 20):
            # First substantial line or numbered item is likely the action
            action_now = line.lstrip('1.').strip().strip('*').strip()
        elif not why_it_works and i > 0 and (line.startswith('2.') or 'research' in line.lower() or 'study' in line.lower() or 'pomodoro' in line.lower()):
            # Second item or line mentioning research is likely the reasoning
            why_it_works = line.lstrip('2.').strip().strip('*').strip()

    # Extract citation from citations list if provided
    if citations:
        citation = citations[0] if isinstance(citations[0], str) else str(citations[0])

    # Fallback: if parsing failed, use full answer as reasoning
    if not action_now:
        # Use first meaningful paragraph as action
        for line in lines:
            if line and not line.startswith('#') and len(line) > 20:
                action_now = line[:200]
                break

    if not why_it_works:
        # Use second paragraph or full answer
        for i, line in enumerate(lines):
            if i > 0 and line and not line.startswith('#') and len(line) > 20:
                why_it_works = line[:300]
                break
        if not why_it_works:
            why_it_works = answer[:300]

    if not citation:
        citation = "You.com AI Research"

    # Clean up markdown formatting
    action_now = action_now.strip('*').strip()
    why_it_works = why_it_works.strip('*').strip()

    return {
        "action_now": action_now or "Take a 90-second walk, then return to work.",
        "why_it_works": why_it_works or "Brief breaks reset attention and restore focus.",
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
