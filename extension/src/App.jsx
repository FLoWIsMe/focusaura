import React, { useState, useEffect } from "react";
import GoalSetter from "./components/GoalSetter";
import DashboardPopup from "./components/DashboardPopup";
import FocusCard from "./components/FocusCard";
import SessionControl from "./components/SessionControl";

/**
 * Main App component for FocusAura extension popup.
 *
 * This is what users see when they click the extension icon.
 * Contains:
 * - Goal setting interface
 * - Session start/end controls
 * - Dashboard with recovery metrics
 * - Developer simulation button for testing
 */
function App() {
  // User's current goal
  const [goal, setGoal] = useState("");
  const [deadline, setDeadline] = useState("");

  // Session state
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [sessionStartTime, setSessionStartTime] = useState(null);
  const [totalSessionTime, setTotalSessionTime] = useState(0);

  // Recovery metrics
  const [focusRecoveriesCount, setFocusRecoveriesCount] = useState(0);
  const [minutesSaved, setMinutesSaved] = useState(0);

  // Intervention state
  const [currentIntervention, setCurrentIntervention] = useState(null);
  const [showFocusCard, setShowFocusCard] = useState(false);

  // Load saved goal, session state, and metrics from chrome.storage on mount
  useEffect(() => {
    loadStoredData();
  }, []);

  const loadStoredData = async () => {
    try {
      // Try to load from chrome.storage (will work in extension context)
      if (typeof chrome !== "undefined" && chrome.storage) {
        chrome.storage.local.get(
          [
            "goal",
            "deadline",
            "recoveries",
            "minutesSaved",
            "isSessionActive",
            "sessionStartTime",
            "totalSessionTime",
          ],
          (result) => {
            if (result.goal) setGoal(result.goal);
            if (result.deadline) setDeadline(result.deadline);
            if (result.recoveries) setFocusRecoveriesCount(result.recoveries);
            if (result.minutesSaved) setMinutesSaved(result.minutesSaved);
            if (result.isSessionActive) {
              setIsSessionActive(true);
              setSessionStartTime(result.sessionStartTime);
            }
            if (result.totalSessionTime)
              setTotalSessionTime(result.totalSessionTime);
          }
        );
      }
    } catch (error) {
      console.log("Running in dev mode, chrome.storage not available");
    }
  };

  const handleGoalSave = (newGoal, newDeadline) => {
    setGoal(newGoal);
    setDeadline(newDeadline);

    // Save to chrome.storage
    try {
      if (typeof chrome !== "undefined" && chrome.storage) {
        chrome.storage.local.set({ goal: newGoal, deadline: newDeadline });
      }
    } catch (error) {
      console.log("Running in dev mode, chrome.storage not available");
    }
  };

  /**
   * Start a new focus session.
   * Notifies background script to begin monitoring.
   */
  const handleStartSession = () => {
    if (!goal || goal.trim().length === 0) {
      console.error("Cannot start session without a goal");
      return;
    }

    const startTime = Date.now();
    setIsSessionActive(true);
    setSessionStartTime(startTime);

    // Save session state to storage
    try {
      if (typeof chrome !== "undefined" && chrome.storage) {
        chrome.storage.local.set({
          isSessionActive: true,
          sessionStartTime: startTime,
          sessionGoal: goal,
        });

        // Notify background script to start monitoring
        chrome.runtime.sendMessage(
          {
            type: "START_SESSION",
            goal: goal,
            startTime: startTime,
          },
          (response) => {
            console.log("✅ Session started:", response);
          }
        );
      }
    } catch (error) {
      console.log("Running in dev mode, chrome APIs not available");
    }

    console.log("🎯 Focus session started:", {
      goal,
      startTime: new Date(startTime).toISOString(),
    });
  };

  /**
   * End the current focus session.
   * Notifies background script to stop monitoring and records session duration.
   */
  const handleEndSession = () => {
    if (!isSessionActive || !sessionStartTime) {
      console.error("No active session to end");
      return;
    }

    const endTime = Date.now();
    const sessionDuration = Math.floor((endTime - sessionStartTime) / 1000); // in seconds
    const newTotalTime = totalSessionTime + sessionDuration;

    setIsSessionActive(false);
    setSessionStartTime(null);
    setTotalSessionTime(newTotalTime);

    // Save session state to storage
    try {
      if (typeof chrome !== "undefined" && chrome.storage) {
        chrome.storage.local.set({
          isSessionActive: false,
          sessionStartTime: null,
          totalSessionTime: newTotalTime,
        });

        // Notify background script to stop monitoring
        chrome.runtime.sendMessage(
          {
            type: "END_SESSION",
            duration: sessionDuration,
            endTime: endTime,
          },
          (response) => {
            console.log("✅ Session ended:", response);
          }
        );
      }
    } catch (error) {
      console.log("Running in dev mode, chrome APIs not available");
    }

    console.log("🛑 Focus session ended:", {
      duration: `${Math.floor(sessionDuration / 60)} minutes ${
        sessionDuration % 60
      } seconds`,
      totalTime: `${Math.floor(newTotalTime / 60)} minutes`,
    });
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
    console.log("🎬 Simulating distraction event...");

    // Build a realistic FocusEvent payload
    const focusEvent = {
      goal: goal || "Complete project documentation",
      context_title: "Project_Proposal.docx",
      context_app: "Google Docs",
      time_on_task_minutes: 42,
      event: "switched_to_youtube",
    };

    try {
      // Call FastAPI backend
      const response = await fetch("http://localhost:8000/intervention", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(focusEvent),
      });

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`);
      }

      const intervention = await response.json();
      console.log("✅ Intervention received:", intervention);

      // Show the FocusCard
      setCurrentIntervention(intervention);
      setShowFocusCard(true);
    } catch (error) {
      console.error("❌ Failed to get intervention:", error);

      // Fallback for demo if backend is down
      setCurrentIntervention({
        action_now: "Take a 90-second walk around your space—no phone.",
        why_it_works:
          "Stanford research shows brief walks reset the prefrontal cortex. You've already invested 42 minutes—don't lose momentum.",
        goal_reminder: `Your goal: ${goal || "Complete your task"}`,
        citation: "Oppezzo & Schwartz, Stanford (2023)",
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
      if (typeof chrome !== "undefined" && chrome.storage) {
        chrome.storage.local.set({
          recoveries: newRecoveryCount,
          minutesSaved: newMinutesSaved,
        });
      }
    } catch (error) {
      console.log("Running in dev mode, chrome.storage not available");
    }
  };

  const handleFocusLater = () => {
    setShowFocusCard(false);
  };

  /**
   * Reload the extension for quick development iteration.
   * Uses chrome.runtime.reload() API.
   */
  const reloadExtension = () => {
    try {
      if (typeof chrome !== "undefined" && chrome.runtime) {
        console.log("🔄 Reloading extension...");
        chrome.runtime.reload();
      } else {
        console.log("chrome.runtime not available (probably in dev mode)");
      }
    } catch (error) {
      console.error("Failed to reload extension:", error);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>FocusAura</h1>
        <p className="tagline">AI focus assistant powered by You.com</p>
      </header>

      <main className="app-main">
        {!isSessionActive && (
          <GoalSetter
            initialGoal={goal}
            initialDeadline={deadline}
            onSave={handleGoalSave}
          />
        )}

        <SessionControl
          isSessionActive={isSessionActive}
          onStartSession={handleStartSession}
          onEndSession={handleEndSession}
          sessionStartTime={sessionStartTime}
          goal={goal}
        />

        <DashboardPopup
          goal={goal}
          deadline={deadline}
          focusRecoveriesCount={focusRecoveriesCount}
          minutesSaved={minutesSaved}
          totalSessionTime={totalSessionTime}
        />

        {/* Developer demo button */}
        {/* <div className="dev-section"> */}
        {/* <button
            className="simulate-btn"
            onClick={simulateDistraction}
          >
            🎬 Simulate Distraction (Demo)
          </button>
          <p className="dev-note">
            For judges: This triggers the full intervention flow
          </p> */}

        {/* Quick reload button for development */}
        {/* <button
            className="reload-btn"
            onClick={reloadExtension}
            style={{
              marginTop: "10px",
              padding: "8px 16px",
              backgroundColor: "#6366f1",
              color: "white",
              border: "none",
              borderRadius: "6px",
              cursor: "pointer",
              fontSize: "13px",
            }}
          >
            🔄 Reload Extension
          </button> */}
        {/* </div> */}
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
