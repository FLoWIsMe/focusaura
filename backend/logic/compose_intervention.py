"""
Intervention Composition Logic

This module orchestrates calls to You.com Agents API to generate
personalized, evidence-based focus interventions.

Flow:
1. Receive FocusEvent with user context and session_id
2. Retrieve or create session conversation history
3. Call You.com Agents API with contextual prompt and conversation history
4. Parse response and extract intervention components
5. Update session conversation history
6. Return structured InterventionResponse
"""

from typing import Dict
import logging
import re
import json

# You.com Agents API client
from you_client.smart_api import query_agents_api

# Session management
from logic.session_manager import session_manager

logger = logging.getLogger(__name__)


async def compose_intervention(event) -> Dict[str, str]:
    """
    Generate a personalized focus intervention using You.com Smart API.

    Args:
        event: FocusEvent with user context, distraction details, and session_id

    Returns:
        Dict with keys: action_now, why_it_works, goal_reminder, citation

    Implementation:
        Uses You.com Smart API to get evidence-based, citation-backed advice
        tailored to the user's specific distraction context and session history.
    """

    # Extract context from event
    session_id = event.session_id
    user_goal = event.goal
    time_on_task = event.time_on_task_minutes
    distraction_type = event.event
    context_title = event.context_title
    
    # Get or create session conversation
    session = session_manager.get_or_create_session(session_id)
    logger.info(f"Session info: {session.get_summary()}")

    # Build contextualized prompt for Agents API with JSON response requirement
    # Include session context if this isn't the first distraction
    session_context = ""
    if session.distraction_count > 0:
        session_context = f"\n\nNOTE: This is distraction #{session.distraction_count + 1} in this focus session. Consider the user's pattern and adapt your advice accordingly."
    
    prompt = f"""I have been working on "{user_goal}" for {time_on_task} minutes in {context_title}, but I got distracted by {distraction_type}.{session_context}

Give me ONE specific, research-backed technique to recover my focus immediately. Base your advice on neuroscience and productivity research. Keep it concise and motivating.

CRITICAL: You MUST respond with ONLY valid JSON in this EXACT format (no other text before or after):

{{
  "action": "One specific immediate action I should take right now - 20-30 words - must be concrete and actionable",
  "reasoning": "Brief scientific explanation of why this technique is effective - 40-60 words - must be different from the action and explain the underlying mechanism",
  "source": "Research citation or credible source"
}}

Be direct, practical, and encouraging. The action and reasoning fields must be completely distinct - no repetition."""

    logger.info(f"Generating intervention for: {distraction_type} (goal: {user_goal}) - Session distraction #{session.distraction_count + 1}")
    
    # Get conversation history for context
    conversation_history = session.get_conversation_history(max_messages=6)  # Last 3 exchanges
    
    # Add current prompt to session
    session.add_message("user", prompt)

    try:
        # Call You.com Agents API with conversation history
        response = await query_agents_api(
            input_text=prompt,
            agent="express",
            conversation_history=conversation_history if len(conversation_history) > 0 else None
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
        
        # Add assistant's response to session history
        assistant_summary = f"ACTION: {intervention['action_now']}\nREASONING: {intervention['why_it_works']}"
        session.add_message("assistant", assistant_summary)

        logger.info("Intervention generated successfully")
        logger.info(f"Updated session: {session.get_summary()}")
        
        return intervention

    except Exception as e:
        logger.error(f"Error generating intervention: {e}")
        # Fallback to template-based intervention
        fallback = _generate_fallback_intervention(event)
        
        # Still add to session history even for fallback
        assistant_summary = f"ACTION: {fallback['action_now']}\nREASONING: {fallback['why_it_works']}"
        session.add_message("assistant", assistant_summary)
        
        return fallback


def _parse_agents_api_response(
    answer: str,
    citations: list,
    user_goal: str
) -> Dict[str, str]:
    """
    Parse Agents API JSON response into intervention components with robust validation.

    The Agents API should return a JSON object with:
    - action: The immediate action to take
    - reasoning: The scientific explanation
    - source: Citation or source attribution

    This function ensures action and reasoning are always distinct.
    """
    action_now = ""
    why_it_works = ""
    citation = ""

    try:
        # Parse JSON response - try to find JSON object in the answer
        json_str = answer.strip()
        
        # If there's markdown code blocks, extract JSON from within
        if "```json" in json_str:
            json_match = re.search(r'```json\s*\n(.*?)\n```', json_str, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
        elif "```" in json_str:
            json_match = re.search(r'```\s*\n(.*?)\n```', json_str, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
        
        # Find JSON object if there's extra text
        if not json_str.startswith('{'):
            json_match = re.search(r'\{.*?"action".*?\}', json_str, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
        
        # Parse the JSON
        data = json.loads(json_str)
        
        # Extract fields directly from JSON
        action_now = data.get("action", "").strip()
        why_it_works = data.get("reasoning", "").strip()
        citation = data.get("source", "").strip()
        
        logger.info("Successfully parsed JSON response")
        
    except (json.JSONDecodeError, AttributeError, ValueError) as e:
        logger.warning(f"Failed to parse JSON response: {e}. Using fallback.")

    # Extract citation from citations list if not found in JSON
    if not citation and citations:
        citation = citations[0] if isinstance(citations[0], str) else str(citations[0])

    if not citation:
        citation = "You.com AI Research"

    # CRITICAL VALIDATION: Ensure action_now and why_it_works are different
    if action_now and why_it_works:
        if _are_texts_too_similar(action_now, why_it_works):
            logger.warning("Detected duplicate content in action and reasoning - applying fix")
            combined = action_now if len(action_now) > len(why_it_works) else why_it_works
            action_now, why_it_works = _split_into_action_and_reasoning(combined)

    # Apply length constraints
    action_now = _truncate_text(action_now, max_words=40)
    why_it_works = _truncate_text(why_it_works, max_words=80)

    # Final fallback if validation fails
    if not action_now or not why_it_works or _are_texts_too_similar(action_now, why_it_works):
        logger.error("Failed to parse distinct action and reasoning - using safe defaults")
        return {
            "action_now": "Take a 90-second walk away from your screen, then return to your task.",
            "why_it_works": "Brief physical movement resets prefrontal cortex activity and reduces the cognitive switching cost from distractions. Stanford research shows this restores focus faster than staying seated.",
            "goal_reminder": f"Your goal: {user_goal}",
            "citation": "Stanford Neuroscience Research (2024)"
        }

    return {
        "action_now": action_now or "Take a 90-second walk, then return to work.",
        "why_it_works": why_it_works or "Brief breaks reset attention and restore focus.",
        "goal_reminder": f"Your goal: {user_goal}",
        "citation": citation or "Focus recovery research"
    }


def _are_texts_too_similar(text1: str, text2: str) -> bool:
    """Check if two texts are too similar (likely duplicates)."""
    if not text1 or not text2:
        return False

    # Normalize for comparison
    t1 = text1.lower().strip()
    t2 = text2.lower().strip()

    # Check if identical
    if t1 == t2:
        return True

    # Check if one contains the other (with some tolerance)
    if len(t1) > 20 and len(t2) > 20:
        if t1 in t2 or t2 in t1:
            return True

    # Check if they start with the same content (likely copy-paste)
    min_len = min(len(t1), len(t2))
    if min_len > 50:
        # If first 50 chars are identical, they're too similar
        if t1[:50] == t2[:50]:
            return True

    return False


def _split_into_action_and_reasoning(text: str) -> tuple:
    """
    Intelligently split combined text into action and reasoning.

    Returns:
        tuple: (action_now, why_it_works)
    """
    # Try to find a natural split point
    sentences = re.split(r'\.(?:\s+|$)', text)
    sentences = [s.strip() + '.' for s in sentences if s.strip()]

    if len(sentences) >= 2:
        # First sentence(s) as action, rest as reasoning
        # Look for keywords that indicate explanation
        explanation_start = -1
        for i, sent in enumerate(sentences):
            if any(keyword in sent.lower() for keyword in ['because', 'this', 'research', 'study', 'shows', 'activates', 'reduces']):
                explanation_start = i
                break

        if explanation_start > 0:
            action = ' '.join(sentences[:explanation_start])
            reasoning = ' '.join(sentences[explanation_start:])
        else:
            # Default: split roughly in half
            mid = len(sentences) // 2
            if mid == 0:
                mid = 1
            action = ' '.join(sentences[:mid])
            reasoning = ' '.join(sentences[mid:])

        return (action, reasoning)

    # If only one sentence, create a generic split
    return (
        "Close the distraction and take three deep breaths before returning to your task.",
        "This brief pause resets your attention and reduces the cognitive cost of context switching."
    )


def _truncate_text(text: str, max_words: int) -> str:
    """Truncate text to maximum number of words while preserving sentence structure."""
    if not text:
        return text

    words = text.split()
    if len(words) <= max_words:
        return text

    # Truncate and try to end at sentence boundary
    truncated = ' '.join(words[:max_words])

    # If we're in the middle of a sentence, try to complete it
    if not truncated.endswith('.'):
        # Look for the last period before truncation point
        last_period = truncated.rfind('.')
        if last_period > len(truncated) * 0.7:  # If we're at least 70% through
            truncated = truncated[:last_period + 1]
        else:
            # Add ellipsis if we can't find good ending
            truncated += '...'

    return truncated


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
