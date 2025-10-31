"""
Session Conversation Manager

Maintains conversation history for each focus session,
allowing the AI to provide contextual interventions based on
the user's session history.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ConversationMessage:
    """Represents a single message in the conversation."""
    
    def __init__(self, role: str, content: str):
        self.role = role  # "user" or "assistant"
        self.content = content
        self.timestamp = datetime.now()


class SessionConversation:
    """Manages conversation history for a single focus session."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages: List[ConversationMessage] = []
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.distraction_count = 0
        
    def add_message(self, role: str, content: str):
        """Add a message to the conversation history."""
        message = ConversationMessage(role, content)
        self.messages.append(message)
        self.last_activity = datetime.now()
        
        if role == "user":
            self.distraction_count += 1
            
    def get_conversation_history(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """
        Get recent conversation history for context.
        
        Returns:
            List of message dicts with 'role' and 'content'
        """
        recent_messages = self.messages[-max_messages:]
        return [
            {"role": msg.role, "content": msg.content}
            for msg in recent_messages
        ]
    
    def get_summary(self) -> str:
        """Get a summary of the session for logging."""
        return (
            f"Session {self.session_id}: "
            f"{self.distraction_count} distractions, "
            f"{len(self.messages)} messages, "
            f"active for {(datetime.now() - self.created_at).seconds}s"
        )


class SessionManager:
    """Global manager for all active sessions."""
    
    def __init__(self):
        self.sessions: Dict[str, SessionConversation] = {}
        self.session_timeout_minutes = 60  # Clean up inactive sessions after 1 hour
        
    def get_or_create_session(self, session_id: str) -> SessionConversation:
        """Get existing session or create new one."""
        if session_id not in self.sessions:
            logger.info(f"Creating new conversation session: {session_id}")
            self.sessions[session_id] = SessionConversation(session_id)
        else:
            logger.info(f"Using existing conversation session: {session_id}")
            
        return self.sessions[session_id]
    
    def cleanup_old_sessions(self):
        """Remove sessions that have been inactive for too long."""
        now = datetime.now()
        timeout = timedelta(minutes=self.session_timeout_minutes)
        
        expired_sessions = [
            sid for sid, session in self.sessions.items()
            if now - session.last_activity > timeout
        ]
        
        for sid in expired_sessions:
            logger.info(f"Cleaning up expired session: {sid}")
            del self.sessions[sid]
            
    def get_session_info(self) -> Dict:
        """Get info about all active sessions."""
        return {
            "active_sessions": len(self.sessions),
            "sessions": [
                {
                    "session_id": session.session_id,
                    "distraction_count": session.distraction_count,
                    "message_count": len(session.messages),
                    "created_at": session.created_at.isoformat(),
                    "last_activity": session.last_activity.isoformat()
                }
                for session in self.sessions.values()
            ]
        }


# Global session manager instance
session_manager = SessionManager()

