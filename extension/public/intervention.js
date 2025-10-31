/**
 * Intervention Page Script
 * Handles fetching AI-powered interventions from backend
 */

// Get URL parameters
const urlParams = new URLSearchParams(window.location.search);
const site = urlParams.get('site');
const url = urlParams.get('url');
const distractionTabId = parseInt(urlParams.get('tabId'), 10);

// Load session data and fetch AI intervention
chrome.storage.local.get(['sessionGoal', 'isSessionActive', 'sessionStartTime', 'sessionId'], (result) => {
  // Display distraction site
  const siteElement = document.getElementById('distraction-site');
  siteElement.textContent = site || 'Unknown Site';

  // Display goal
  const goalElement = document.getElementById('goal-text');
  const userGoal = result.sessionGoal || 'Stay focused on your work';
  goalElement.textContent = userGoal;

  // Get session ID or create temporary one
  const currentSessionId = result.sessionId || `intervention_${Date.now()}`;

  // Show stats if session is active
  let focusTimeMinutes = 0;
  if (result.isSessionActive && result.sessionStartTime) {
    focusTimeMinutes = Math.floor((Date.now() - result.sessionStartTime) / 60000);
    document.getElementById('focus-time').textContent = focusTimeMinutes + 'm';
    document.getElementById('stats-section').style.display = 'flex';
  }

  // Call backend API for AI intervention (not awaited, runs independently)
  fetchAIIntervention(currentSessionId, userGoal, site, url, focusTimeMinutes);
});

// Fetch AI-powered intervention from backend
async function fetchAIIntervention(sessionId, goal, distractionSite, distractionUrl, timeOnTask) {
  const interventionSection = document.getElementById('ai-intervention-section');
  
  console.log('🔄 Fetching AI intervention from backend...', {
    sessionId,
    goal,
    distractionSite,
    timeOnTask
  });
  
  try {
    const response = await fetch('http://localhost:8000/intervention', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
        goal: goal,
        context_title: distractionSite,
        context_app: 'Chrome',
        time_on_task_minutes: timeOnTask,
        event: `distraction_${distractionSite}`
      })
    });

    console.log('📡 Response received:', response.status);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('✅ Intervention data:', data);
    
    // Display AI intervention
    interventionSection.innerHTML = `
      <div class="ai-intervention">
        <div class="ai-label">
          🤖 AI-Powered Intervention
        </div>
        <div class="ai-content">
          <div class="action-now">
            ${data.action_now}
          </div>
          <div class="why-it-works">
            <strong>Why this works:</strong> ${data.why_it_works}
          </div>
          <div class="citation">
            📚 ${data.citation}
          </div>
        </div>
      </div>
    `;
  } catch (error) {
    console.error('Failed to fetch AI intervention:', error);
    
    // Show error message with fallback
    interventionSection.innerHTML = `
      <div class="error-message">
        ⚠️ Could not connect to AI service. Using default intervention.
      </div>
      <div class="ai-intervention">
        <div class="ai-label">
          💡 Quick Focus Tip
        </div>
        <div class="ai-content">
          <div class="action-now">
            Take 3 deep breaths, close this tab, and write one sentence about what you'll do next.
          </div>
          <div class="why-it-works">
            <strong>Why this works:</strong> Deep breathing activates your parasympathetic nervous system, reducing stress hormones and restoring executive function. Writing clarifies intent and creates commitment.
          </div>
          <div class="citation">
            📚 Harvard Medical School (2024)
          </div>
        </div>
      </div>
    `;
  }
}

// Close button - close the distraction tab and this intervention tab
document.getElementById('close-btn').addEventListener('click', () => {
  if (distractionTabId && !isNaN(distractionTabId)) {
    // Close the distraction tab
    chrome.tabs.remove(distractionTabId, () => {
      // Then close this intervention tab
      chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
        if (tabs[0]) {
          chrome.tabs.remove(tabs[0].id);
        }
      });
    });
  } else {
    // Just close this tab if we don't have the distraction tab ID
    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
      if (tabs[0]) {
        chrome.tabs.remove(tabs[0].id);
      }
    });
  }
});

// Continue button - just close this intervention tab
document.getElementById('continue-btn').addEventListener('click', () => {
  chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
    if (tabs[0]) {
      chrome.tabs.remove(tabs[0].id);
    }
  });
});

// Track this distraction
chrome.storage.local.get(['distractionCount'], (result) => {
  const count = (result.distractionCount || 0) + 1;
  chrome.storage.local.set({ distractionCount: count });
  document.getElementById('distractions').textContent = count;
});

