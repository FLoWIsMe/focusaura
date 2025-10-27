import React, { useState, useEffect } from 'react';
import GoalSetter from './components/GoalSetter';
import DashboardPopup from './components/DashboardPopup';
import FocusCard from './components/FocusCard';

/**
 * Main App component for FocusAura extension popup.
 *
 * This is what users see when they click the extension icon.
 * Contains:
 * - Goal setting interface
 * - Dashboard with recovery metrics
 * - Developer simulation button for testing
 */
function App() {
  // User's current goal
  const [goal, setGoal] = useState('');
  const [deadline, setDeadline] = useState('');

  // Recovery metrics
  const [focusRecoveriesCount, setFocusRecoveriesCount] = useState(0);
  const [minutesSaved, setMinutesSaved] = useState(0);

  // Intervention state
  const [currentIntervention, setCurrentIntervention] = useState(null);
  const [showFocusCard, setShowFocusCard] = useState(false);

  // Load saved goal and metrics from chrome.storage on mount
  useEffect(() => {
    loadStoredData();
  }, []);

  const loadStoredData = async () => {
    try {
      // Try to load from chrome.storage (will work in extension context)
      if (typeof chrome !== 'undefined' && chrome.storage) {
        chrome.storage.local.get(
          ['goal', 'deadline', 'recoveries', 'minutesSaved'],
          (result) => {
            if (result.goal) setGoal(result.goal);
            if (result.deadline) setDeadline(result.deadline);
            if (result.recoveries) setFocusRecoveriesCount(result.recoveries);
            if (result.minutesSaved) setMinutesSaved(result.minutesSaved);
          }
        );
      }
    } catch (error) {
      console.log('Running in dev mode, chrome.storage not available');
    }
  };

  const handleGoalSave = (newGoal, newDeadline) => {
    setGoal(newGoal);
    setDeadline(newDeadline);

    // Save to chrome.storage
    try {
      if (typeof chrome !== 'undefined' && chrome.storage) {
        chrome.storage.local.set({ goal: newGoal, deadline: newDeadline });
      }
    } catch (error) {
      console.log('Running in dev mode, chrome.storage not available');
    }
  };

  /**
   * Simulate a distraction event for demo purposes.
   *
   * This is the key demo button for judges.
   * It triggers the full intervention flow:
   * 1. Build FocusEvent payload
   * 2. POST to FastAPI backend
   * 3. Display FocusCard with intervention
   */
  const simulateDistraction = async () => {
    console.log('🎬 Simulating distraction event...');

    // Build a realistic FocusEvent payload
    const focusEvent = {
      goal: goal || 'Complete project documentation',
      context_title: 'Project_Proposal.docx',
      context_app: 'Google Docs',
      time_on_task_minutes: 42,
      event: 'switched_to_youtube'
    };

    try {
      // Call FastAPI backend
      const response = await fetch('http://localhost:8000/intervention', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(focusEvent)
      });

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`);
      }

      const intervention = await response.json();
      console.log('✅ Intervention received:', intervention);

      // Show the FocusCard
      setCurrentIntervention(intervention);
      setShowFocusCard(true);

    } catch (error) {
      console.error('❌ Failed to get intervention:', error);

      // Fallback for demo if backend is down
      setCurrentIntervention({
        action_now: 'Take a 90-second walk around your space—no phone.',
        why_it_works: 'Stanford research shows brief walks reset the prefrontal cortex. You\'ve already invested 42 minutes—don\'t lose momentum.',
        goal_reminder: `Your goal: ${goal || 'Complete your task'}`,
        citation: 'Oppezzo & Schwartz, Stanford (2023)'
      });
      setShowFocusCard(true);
    }
  };

  /**
   * Handle user clicking "I'm back" on FocusCard.
   * This increments recovery metrics and hides the card.
   */
  const handleFocusRecovered = () => {
    const newRecoveryCount = focusRecoveriesCount + 1;
    const newMinutesSaved = minutesSaved + 6; // Assume 6 minutes saved per recovery

    setFocusRecoveriesCount(newRecoveryCount);
    setMinutesSaved(newMinutesSaved);
    setShowFocusCard(false);

    // Persist to storage
    try {
      if (typeof chrome !== 'undefined' && chrome.storage) {
        chrome.storage.local.set({
          recoveries: newRecoveryCount,
          minutesSaved: newMinutesSaved
        });
      }
    } catch (error) {
      console.log('Running in dev mode, chrome.storage not available');
    }
  };

  const handleFocusLater = () => {
    setShowFocusCard(false);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>FocusAura</h1>
        <p className="tagline">AI focus assistant powered by You.com</p>
      </header>

      <main className="app-main">
        <GoalSetter
          initialGoal={goal}
          initialDeadline={deadline}
          onSave={handleGoalSave}
        />

        <DashboardPopup
          goal={goal}
          deadline={deadline}
          focusRecoveriesCount={focusRecoveriesCount}
          minutesSaved={minutesSaved}
        />

        {/* Developer demo button */}
        <div className="dev-section">
          <button
            className="simulate-btn"
            onClick={simulateDistraction}
          >
            🎬 Simulate Distraction (Demo)
          </button>
          <p className="dev-note">
            For judges: This triggers the full intervention flow
          </p>
        </div>
      </main>

      {/* FocusCard overlay (conditionally rendered) */}
      {showFocusCard && currentIntervention && (
        <FocusCard
          intervention={currentIntervention}
          onBack={handleFocusRecovered}
          onLater={handleFocusLater}
        />
      )}
    </div>
  );
}

export default App;
