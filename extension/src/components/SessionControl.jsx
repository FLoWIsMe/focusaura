import React, { useState, useEffect } from 'react';

/**
 * SessionControl Component
 * 
 * Manages focus sessions with start/end controls and live timer.
 * Features:
 * - Start/End session buttons
 * - Live session timer
 * - Session statistics
 * - Visual feedback for active sessions
 */
function SessionControl({ 
  isSessionActive, 
  onStartSession, 
  onEndSession,
  sessionStartTime,
  goal 
}) {
  const [elapsedTime, setElapsedTime] = useState(0);

  // Update elapsed time every second when session is active
  useEffect(() => {
    let interval = null;
    
    if (isSessionActive && sessionStartTime) {
      interval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - sessionStartTime) / 1000);
        setElapsedTime(elapsed);
      }, 1000);
    } else {
      setElapsedTime(0);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isSessionActive, sessionStartTime]);

  // Format elapsed time as HH:MM:SS
  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
    return `${minutes}:${String(secs).padStart(2, '0')}`;
  };

  // Prevent starting session without a goal
  const canStartSession = goal && goal.trim().length > 0;

  if (isSessionActive) {
    return (
      <div className="session-control active">
        <div className="session-header">
          <div className="status-indicator">
            <span className="pulse-dot"></span>
            <span className="status-text">Session Active</span>
          </div>
        </div>

        <div className="session-timer">
          <div className="timer-display">{formatTime(elapsedTime)}</div>
          <div className="timer-label">Focus Time</div>
        </div>

        <button 
          className="end-session-btn" 
          onClick={onEndSession}
        >
          🛑 End Session
        </button>

        <div className="session-info">
          <p className="info-text">
            💡 FocusAura is monitoring your activity
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="session-control inactive">
      <div className="session-header">
        <h3>Focus Session</h3>
      </div>

      {!canStartSession ? (
        <div className="session-placeholder">
          <p className="placeholder-text">
            ⬆️ Set a goal above to start a focus session
          </p>
        </div>
      ) : (
        <>
          <div className="session-ready">
            <p className="ready-text">
              Ready to start focusing on: <strong>{goal}</strong>
            </p>
          </div>

          <button 
            className="start-session-btn" 
            onClick={onStartSession}
          >
            ▶️ Start Focus Session
          </button>

          <div className="session-info">
            <p className="info-text">
              FocusAura will monitor for distractions and help you stay on track.
            </p>
          </div>
        </>
      )}
    </div>
  );
}

export default SessionControl;

