"""
FocusAura FastAPI Backend

This service receives distraction events from the Chrome extension,
calls You.com APIs to generate evidence-based interventions,
and returns structured guidance to help users recover focus.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from logic.compose_intervention import compose_intervention
from logic.session_manager import session_manager
from you_client.config import config as you_config

app = FastAPI(
    title="FocusAura API",
    description="AI focus assistant backend powered by You.com intelligence",
    version="0.1.0"
)

# CORS configuration for Chrome extension development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",  # Vite default port
        "chrome-extension://*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class FocusEvent(BaseModel):
    """
    Represents a distraction event detected by the extension.

    Fields:
        session_id: Unique identifier for the current focus session
        goal: User's stated objective (e.g., "Finish project proposal by 3 PM")
        context_title: Title of the work context (e.g., "Project_Proposal.docx")
        context_app: Application or site user was working in (e.g., "Google Docs")
        time_on_task_minutes: How long user was focused before distraction
        event: Type of distraction (e.g., "switched_to_youtube", "idle_timeout")
    """
    session_id: str = Field(..., description="Unique ID for this focus session")
    goal: str = Field(..., description="User's current work goal")
    context_title: str = Field(..., description="Title of work context")
    context_app: str = Field(..., description="Application or site name")
    time_on_task_minutes: int = Field(..., ge=0, description="Minutes on task before distraction")
    event: str = Field(..., description="Distraction event type")


class InterventionResponse(BaseModel):
    """
    Structured intervention returned to the extension.

    This is the "micro-intervention" that appears in the FocusCard overlay.
    """
    action_now: str = Field(..., description="Immediate action to take (1 sentence)")
    why_it_works: str = Field(..., description="Scientific reasoning (1-2 sentences)")
    goal_reminder: str = Field(..., description="User's goal, restated")
    citation: str = Field(..., description="Source attribution for advice")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "FocusAura API",
        "status": "running",
        "message": "Ready to generate focus interventions"
    }


@app.post("/intervention", response_model=InterventionResponse)
async def create_intervention(event: FocusEvent):
    """
    Generate a personalized focus intervention based on distraction context.

    This endpoint:
    1. Receives a FocusEvent from the Chrome extension
    2. Calls compose_intervention() which orchestrates You.com API calls
    3. Returns a structured InterventionResponse with actionable guidance

    In production, this would call:
    - You.com Web Search API for focus technique evidence
    - You.com News API for recent behavioral science studies
    - You.com Smart/Research API to synthesize personalized advice
    """
    try:
        intervention = await compose_intervention(event)
        return intervention
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate intervention: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """
    Detailed health check for monitoring.

    Returns:
        - Service status
        - API mode (demo vs live)
        - Configuration validation
        - Warnings (if any)
    """
    config_status = you_config.validate()

    return {
        "status": "healthy",
        "service": "FocusAura API",
        "mode": config_status["mode"],
        "mode_description": config_status["mode_description"],
        "api_key_configured": config_status["api_key_configured"],
        "ready_for_live_mode": config_status["ready_for_live_mode"],
        "cache_enabled": config_status["cache_enabled"],
        "warnings": config_status["warnings"],
        "apis": {
            "you_web_search": "ready",
            "you_news": "ready",
            "you_smart_research": "ready"
        }
    }


@app.get("/sessions")
async def get_sessions():
    """
    Get information about all active focus sessions.
    
    Returns:
        - Number of active sessions
        - Details for each session (distraction count, message count, etc.)
    """
    # Clean up old sessions before reporting
    session_manager.cleanup_old_sessions()
    
    return session_manager.get_session_info()


@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """
    Clear a specific session's conversation history.
    
    This is useful for testing or when a user wants to start fresh.
    """
    if session_id in session_manager.sessions:
        del session_manager.sessions[session_id]
        return {"status": "success", "message": f"Session {session_id} cleared"}
    else:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
