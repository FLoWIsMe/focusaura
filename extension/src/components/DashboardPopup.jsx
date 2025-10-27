import React from 'react';

/**
 * DashboardPopup Component
 *
 * Displays user's current goal and focus recovery metrics.
 * Shows:
 * - Active goal
 * - Number of times focus was recovered
 * - Estimated minutes saved from interventions
 */
function DashboardPopup({
  goal,
  deadline,
  focusRecoveriesCount = 0,
  minutesSaved = 0
}) {

  if (!goal) {
    return (
      <div className="dashboard empty">
        <p className="empty-state">
          Set a goal above to start tracking your focus sessions.
        </p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <h3>Focus Dashboard</h3>

      <div className="dashboard-card">
        <div className="metric-row goal-row">
          <span className="metric-label">Current Goal:</span>
          <span className="metric-value goal-value">{goal}</span>
        </div>

        {deadline && (
          <div className="metric-row deadline-row">
            <span className="metric-label">Deadline:</span>
            <span className="metric-value">{deadline}</span>
          </div>
        )}

        <div className="metrics-grid">
          <div className="metric-box">
            <div className="metric-number">{focusRecoveriesCount}</div>
            <div className="metric-description">Focus Recoveries</div>
          </div>

          <div className="metric-box">
            <div className="metric-number">{minutesSaved}</div>
            <div className="metric-description">Minutes Saved</div>
          </div>
        </div>

        {focusRecoveriesCount > 0 && (
          <div className="encouragement">
            <p>
              🎯 Great work! You've recovered focus {focusRecoveriesCount} time
              {focusRecoveriesCount !== 1 ? 's' : ''} today.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default DashboardPopup;
