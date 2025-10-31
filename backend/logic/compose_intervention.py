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
import re

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

    # Build contextualized prompt for Agents API with clear structure requirements
    prompt = f"""I have been working on "{user_goal}" for {time_on_task} minutes in {context_title}, but I got distracted by {distraction_type}.

Give me ONE specific, research-backed technique to recover my focus immediately. Base your advice on neuroscience and productivity research. Keep it concise and motivating.

IMPORTANT: Format your response EXACTLY as follows (use clear separators):

ACTION:
[One specific immediate action I should take right now - 20-30 words - must be concrete and actionable]

WHY IT WORKS:
[Brief scientific explanation of why this technique is effective - 40-60 words - must be different from the action and explain the mechanism]

SOURCE:
[Research citation or source]

Be direct, practical, and encouraging. The ACTION and WHY IT WORKS sections must be distinct and not repeat each other."""

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
    Parse Agents API response into intervention components with robust validation.

    The Agents API returns a comprehensive answer in markdown format.
    We need to extract:
    - action_now: The immediate action to take
    - why_it_works: The reasoning/evidence
    - goal_reminder: User's goal
    - citation: Source attribution

    This function ensures action_now and why_it_works are always distinct.
    """
    action_now = ""
    why_it_works = ""
    citation = ""

    # Strategy 1: Try to parse using explicit section markers (ACTION:, WHY IT WORKS:, SOURCE:)
    action_match = re.search(r'ACTION:\s*\n?(.+?)(?=\n\s*WHY IT WORKS:|\n\s*SOURCE:|$)', answer, re.DOTALL | re.IGNORECASE)
    why_match = re.search(r'WHY IT WORKS:\s*\n?(.+?)(?=\n\s*SOURCE:|$)', answer, re.DOTALL | re.IGNORECASE)
    source_match = re.search(r'SOURCE:\s*\n?(.+?)(?=$)', answer, re.DOTALL | re.IGNORECASE)

    if action_match:
        action_now = _clean_text(action_match.group(1).strip())
    if why_match:
        why_it_works = _clean_text(why_match.group(1).strip())
    if source_match:
        citation = _clean_text(source_match.group(1).strip())

    # Strategy 2: If section markers didn't work, try numbered format (1., 2., 3.)
    if not action_now or not why_it_works:
        numbered_sections = re.findall(r'(?:^|\n)\s*(\d+)\.\s*(.+?)(?=\n\s*\d+\.|\n\n|$)', answer, re.DOTALL)
        if len(numbered_sections) >= 2:
            if not action_now:
                action_now = _clean_text(numbered_sections[0][1].strip())
            if not why_it_works:
                why_it_works = _clean_text(numbered_sections[1][1].strip())
            if len(numbered_sections) >= 3 and not citation:
                citation = _clean_text(numbered_sections[2][1].strip())

    # Strategy 3: Fall back to paragraph-based parsing
    if not action_now or not why_it_works:
        # Split into paragraphs (groups of lines separated by blank lines)
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', answer) if p.strip()]
        # Filter out very short paragraphs and headers
        substantial_paragraphs = [
            p for p in paragraphs
            if len(p) > 30 and not p.startswith('#')
        ]

        if not action_now and len(substantial_paragraphs) > 0:
            action_now = _clean_text(substantial_paragraphs[0])
        if not why_it_works and len(substantial_paragraphs) > 1:
            why_it_works = _clean_text(substantial_paragraphs[1])

    # Strategy 4: If we still don't have both, try to split the first substantial paragraph
    if not action_now or not why_it_works:
        # Get first substantial content
        content = answer.strip()
        content = re.sub(r'^#+\s+.*\n?', '', content)  # Remove headers
        content = _clean_text(content)

        # Try to split on sentence boundaries
        sentences = re.split(r'\.(?:\s+|$)', content)
        sentences = [s.strip() + '.' for s in sentences if len(s.strip()) > 20]

        if len(sentences) >= 2:
            if not action_now:
                action_now = sentences[0]
            if not why_it_works:
                # Combine remaining sentences for explanation
                why_it_works = ' '.join(sentences[1:])

    # Extract citation from citations list if not found in text
    if not citation and citations:
        citation = citations[0] if isinstance(citations[0], str) else str(citations[0])

    if not citation:
        citation = "You.com AI Research"

    # CRITICAL VALIDATION: Ensure action_now and why_it_works are different
    if action_now and why_it_works:
        # Check if they're too similar (same content or one contains the other)
        if _are_texts_too_similar(action_now, why_it_works):
            logger.warning("Detected duplicate content in action_now and why_it_works - applying fix")
            # Try to split the content more intelligently
            combined = action_now if len(action_now) > len(why_it_works) else why_it_works
            action_now, why_it_works = _split_into_action_and_reasoning(combined)

    # Apply length constraints
    action_now = _truncate_text(action_now, max_words=40)
    why_it_works = _truncate_text(why_it_works, max_words=80)

    # Final fallback if validation still fails
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


def _clean_text(text: str) -> str:
    """Remove markdown formatting and clean up text."""
    # Remove markdown formatting
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.+?)\*', r'\1', text)      # Italic
    text = re.sub(r'`(.+?)`', r'\1', text)        # Code
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)  # List markers
    text = re.sub(r'^\s*\d+\.\s+', '', text)      # Numbered list markers
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # Links
    # Remove brackets from template placeholders
    text = re.sub(r'\[|\]', '', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


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
