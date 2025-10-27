/**
 * MonitorEngine
 *
 * This module contains logic for monitoring user activity and detecting
 * distraction events that should trigger interventions.
 *
 * For the MVP, monitoring is simulated via the "Simulate Distraction" button
 * in App.jsx. In production, this would use Chrome APIs to watch:
 * - Active tab changes
 * - Idle time detection
 * - Context switches from "work" to "distraction" sites
 *
 * TODO: Full implementation requires:
 * 1. chrome.tabs API integration
 * 2. chrome.idle API integration
 * 3. Site classification (work vs. distraction)
 * 4. Focus session state management
 */

/**
 * Start monitoring user activity for distraction events.
 *
 * TODO Implementation:
 * -------------------
 * 1. Register chrome.tabs.onActivated listener
 *    - Track when user switches tabs
 *    - Record time spent on each tab
 *    - Classify tabs as "work" or "distraction"
 *
 * 2. Register chrome.idle.onStateChanged listener
 *    - Detect when user goes idle
 *    - Trigger intervention if idle during work session
 *
 * 3. Maintain focus session state:
 *    - Start time of current task
 *    - Active work context (title, app)
 *    - Time on task counter
 *
 * 4. When shouldTriggerIntervention() returns true:
 *    - Build FocusEvent payload
 *    - Call backend /intervention endpoint
 *    - Show FocusCard overlay
 *
 * Example usage:
 * ```javascript
 * chrome.tabs.onActivated.addListener(async (activeInfo) => {
 *   const tab = await chrome.tabs.get(activeInfo.tabId);
 *   const state = getCurrentFocusState();
 *
 *   if (shouldTriggerIntervention(state, tab)) {
 *     const event = buildFocusEvent(state, tab);
 *     triggerIntervention(event);
 *   }
 * });
 * ```
 */
export function startMonitoring() {
  console.log('MonitorEngine: startMonitoring() called');
  console.log('TODO: Implement chrome.tabs and chrome.idle monitoring');

  // MVP: Monitoring is disabled. We use manual "Simulate Distraction" button instead.
  // This keeps the demo clean and controllable for judges.
}

/**
 * Determine if current user activity should trigger an intervention.
 *
 * TODO Implementation:
 * -------------------
 * Decision logic should consider:
 * 1. Was user in a "work" context for > 5 minutes?
 * 2. Did they switch to a known "distraction" site?
 *    - YouTube, Twitter, Reddit, news sites, etc.
 * 3. Have they been idle for > 10 minutes during work session?
 * 4. Rate limiting: Don't trigger more than once per 30 minutes
 *
 * @param {Object} state - Current focus session state
 * @param {string} state.currentTab - URL of active tab
 * @param {number} state.timeOnTask - Minutes on current task
 * @param {number} state.lastInterventionTime - Timestamp of last intervention
 *
 * @returns {boolean} - True if intervention should be triggered
 *
 * Example usage:
 * ```javascript
 * const state = {
 *   currentTab: 'https://www.youtube.com/watch',
 *   timeOnTask: 42,
 *   lastInterventionTime: Date.now() - (45 * 60 * 1000) // 45 min ago
 * };
 *
 * if (shouldTriggerIntervention(state)) {
 *   // Trigger intervention
 * }
 * ```
 */
export function shouldTriggerIntervention(state) {
  console.log('MonitorEngine: shouldTriggerIntervention() called with state:', state);
  console.log('TODO: Implement distraction detection logic');

  // MVP: Always return false. Interventions are triggered manually.
  return false;

  // TODO: Implement real logic:
  // const distractionSites = ['youtube.com', 'twitter.com', 'reddit.com'];
  // const isDistraction = distractionSites.some(site =>
  //   state.currentTab?.includes(site)
  // );
  // const hasMinimumFocus = state.timeOnTask >= 5;
  // const cooldownPassed = Date.now() - state.lastInterventionTime > 30 * 60 * 1000;
  // return isDistraction && hasMinimumFocus && cooldownPassed;
}

/**
 * Get the current focus session state.
 *
 * TODO: Implement state management using chrome.storage.local
 * to track ongoing focus sessions across extension lifecycle.
 */
export function getCurrentFocusState() {
  console.log('TODO: Implement focus state management');
  return {
    currentTab: null,
    timeOnTask: 0,
    lastInterventionTime: 0,
    workContext: {
      title: '',
      app: ''
    }
  };
}

/**
 * Site classification: Determine if a URL is a "work" or "distraction" site.
 *
 * TODO: Implement heuristics or let user configure custom lists.
 */
export function classifySite(url) {
  const distractionPatterns = [
    'youtube.com',
    'twitter.com',
    'facebook.com',
    'reddit.com',
    'instagram.com',
    'tiktok.com',
    'netflix.com'
  ];

  const workPatterns = [
    'docs.google.com',
    'github.com',
    'notion.so',
    'figma.com',
    'localhost'
  ];

  // TODO: Implement classification logic
  return 'unknown';
}
