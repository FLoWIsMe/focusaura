import React from 'react';
import '../styles/card.css';

/**
 * FocusCard Component
 *
 * The core intervention UI that appears when a distraction is detected.
 * Displays science-backed advice in a calm, minimal overlay.
 *
 * This is the "moment of truth" for FocusAura—the micro-intervention
 * that helps users recover focus.
 */
function FocusCard({ intervention, onBack, onLater }) {

  if (!intervention) return null;

  const {
    action_now,
    why_it_works,
    goal_reminder,
    citation
  } = intervention;

  return (
    <div className="focus-card-overlay">
      <div className="focus-card">
        <div className="card-header">
          <h2 className="card-title">FocusAura</h2>
          <span className="powered-by">Powered by You.com</span>
        </div>

        <div className="card-body">
          {/* Primary action */}
          <div className="action-section">
            <h3 className="action-header">What to do right now:</h3>
            <p className="action-text">{action_now}</p>
          </div>

          {/* Scientific reasoning */}
          <div className="why-section">
            <h4 className="why-header">Why this works:</h4>
            <p className="why-text">{why_it_works}</p>
            {citation && (
              <p className="citation">
                <em>Source: {citation}</em>
              </p>
            )}
          </div>

          {/* Goal reminder */}
          <div className="reminder-section">
            <p className="reminder-text">{goal_reminder}</p>
          </div>
        </div>

        <div className="card-footer">
          <button
            className="btn-back"
            onClick={onBack}
          >
            I'm back ✓
          </button>
          <button
            className="btn-later"
            onClick={onLater}
          >
            Later
          </button>
        </div>
      </div>
    </div>
  );
}

export default FocusCard;
