import React, { useState } from 'react';

/**
 * GoalSetter Component
 *
 * Allows users to set their current work goal and deadline.
 * This context is used to personalize interventions.
 */
function GoalSetter({ initialGoal = '', initialDeadline = '', onSave }) {
  const [goal, setGoal] = useState(initialGoal);
  const [deadline, setDeadline] = useState(initialDeadline);
  const [isEditing, setIsEditing] = useState(!initialGoal);

  const handleSave = () => {
    if (goal.trim()) {
      onSave(goal, deadline);
      setIsEditing(false);

      // Also save to chrome.storage for persistence
      try {
        if (typeof chrome !== 'undefined' && chrome.storage) {
          chrome.storage.local.set({ goal, deadline }, () => {
            console.log('Goal saved to chrome.storage');
          });
        }
      } catch (error) {
        console.log('Dev mode: chrome.storage not available');
      }
    }
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  if (!isEditing && goal) {
    return (
      <div className="goal-setter saved">
        <div className="goal-display">
          <h3>Your Focus Goal</h3>
          <p className="goal-text">{goal}</p>
          {deadline && <p className="deadline-text">Due: {deadline}</p>}
          <button className="edit-btn" onClick={handleEdit}>
            Edit Goal
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="goal-setter">
      <h3>Set Your Focus Goal</h3>
      <div className="input-group">
        <label htmlFor="goal-input">What are you trying to finish?</label>
        <input
          id="goal-input"
          type="text"
          placeholder="e.g., Finish Section 2 of proposal"
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
        />
      </div>

      <div className="input-group">
        <label htmlFor="deadline-input">When do you need it done?</label>
        <input
          id="deadline-input"
          type="text"
          placeholder="e.g., Today at 3 PM"
          value={deadline}
          onChange={(e) => setDeadline(e.target.value)}
        />
      </div>

      <button
        className="save-btn"
        onClick={handleSave}
        disabled={!goal.trim()}
      >
        Save Goal
      </button>
    </div>
  );
}

export default GoalSetter;
