/**
 * Background Service Worker for FocusAura
 * 
 * This runs continuously in the background and monitors user activity.
 * Service workers are the Manifest V3 way to handle background tasks.
 */

console.log('🚀 FocusAura background service worker loaded');

// Track focus state and session state
let focusState = {
  currentTab: null,
  currentUrl: null,
  timeOnTask: 0,
  lastInterventionTime: 0,
  workContext: {
    title: '',
    app: ''
  }
};

// Session management state
let sessionState = {
  isActive: false,
  goal: null,
  startTime: null
};

// Load session state from storage on startup
chrome.storage.local.get(['isSessionActive', 'sessionGoal', 'sessionStartTime'], (result) => {
  if (result.isSessionActive) {
    sessionState.isActive = true;
    sessionState.goal = result.sessionGoal;
    sessionState.startTime = result.sessionStartTime;
    console.log('📋 Restored active session:', sessionState);
  }
});

/**
 * Site classification: Determine if a URL is "work" or "distraction"
 */
function classifySite(url) {
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

  for (const pattern of distractionPatterns) {
    if (url.includes(pattern)) {
      return 'distraction';
    }
  }

  for (const pattern of workPatterns) {
    if (url.includes(pattern)) {
      return 'work';
    }
  }

  return 'unknown';
}

/**
 * Show a Chrome notification
 */
function showNotification(title, message, type = 'basic') {
  chrome.notifications.create({
    type: 'basic',
    iconUrl: chrome.runtime.getURL("3119338.png"),
    title: title,
    message: message,
    priority: 1
  });
}

// Track recently opened intervention tabs to prevent infinite loops
let recentInterventions = new Set();

/**
 * Open intervention page for distraction site
 */
function openInterventionPage(hostname, url, tabId) {
  // Prevent multiple interventions for the same tab within 5 seconds
  if (recentInterventions.has(tabId)) {
    console.log('Intervention already opened for this tab recently');
    return;
  }
  
  recentInterventions.add(tabId);
  setTimeout(() => recentInterventions.delete(tabId), 5000);
  
  setTimeout(() => {
    chrome.tabs.create({
      url: chrome.runtime.getURL(`intervention.html?site=${encodeURIComponent(hostname)}&url=${encodeURIComponent(url)}&tabId=${tabId}`)
    }).catch(error => {
      console.error('Failed to open intervention tab:', error);
    });
  }, 100);
}

/**
 * Monitor tab switches (only if session is active)
 */
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  // Only monitor if a session is active
  if (!sessionState.isActive) {
    return;
  }

  try {
    const tab = await chrome.tabs.get(activeInfo.tabId);
    
    // Skip if this is an intervention page itself
    if (tab.url && tab.url.includes('intervention.html')) {
      console.log('Skipping intervention page itself');
      return;
    }
    
    const classification = classifySite(tab.url);
    
    console.log('🔄 Tab switched:', {
      tabId: activeInfo.tabId,
      url: tab.url,
      title: tab.title,
      classification: classification,
      sessionActive: sessionState.isActive,
      timestamp: new Date().toISOString()
    });

    // Update state
    focusState.currentTab = activeInfo.tabId;
    focusState.currentUrl = tab.url;

    // Show intervention page for distraction sites
    if (classification === 'distraction') {
      const hostname = new URL(tab.url).hostname;
      
      // Open intervention page
      openInterventionPage(hostname, tab.url, activeInfo.tabId);
      
      showNotification(
        '⚠️ Distraction Detected',
        `Switched to ${hostname} - Stay focused on: ${sessionState.goal}`
      );
    } else if (classification === 'work') {
      showNotification(
        '✅ Work Mode',
        `Focused on ${new URL(tab.url).hostname}`
      );
    }

  } catch (error) {
    console.error('Error in tab activation listener:', error);
  }
});

/**
 * Monitor tab URL updates (navigation within same tab - only if session is active)
 */
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  // Only monitor if a session is active
  if (!sessionState.isActive) {
    return;
  }

  if (changeInfo.url) {
    // Skip if this is an intervention page itself
    if (changeInfo.url.includes('intervention.html')) {
      console.log('Skipping intervention page itself');
      return;
    }
    
    const classification = classifySite(changeInfo.url);
    
    console.log('🌐 Tab URL updated:', {
      tabId,
      url: changeInfo.url,
      title: tab.title,
      classification: classification,
      sessionActive: sessionState.isActive,
      timestamp: new Date().toISOString()
    });

    // Show intervention page for navigation to distraction sites
    if (classification === 'distraction') {
      const hostname = new URL(changeInfo.url).hostname;
      
      // Open intervention page
      openInterventionPage(hostname, changeInfo.url, tabId);
      
      showNotification(
        '⚠️ Distraction Site',
        `Navigated to ${hostname} - Remember your goal: ${sessionState.goal}`
      );
    }
  }
});

/**
 * Monitor idle state changes
 * Check every 300 seconds (5 minutes)
 */
chrome.idle.setDetectionInterval(300);

chrome.idle.onStateChanged.addListener((newState) => {
  console.log('💤 Idle state changed:', {
    state: newState,
    timestamp: new Date().toISOString()
  });

  if (newState === 'idle') {
    console.log('User has gone idle (inactive for 300+ seconds)');
    showNotification(
      '💤 You\'ve Gone Idle',
      'You\'ve been inactive for 5 minutes'
    );
  } else if (newState === 'active') {
    console.log('User is back active');
    showNotification(
      '👋 Welcome Back',
      'You\'re active again!'
    );
  } else if (newState === 'locked') {
    console.log('User has locked their screen');
  }
});

/**
 * Listen for messages from popup or content scripts
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('📨 Message received:', message);

  if (message.type === 'GET_FOCUS_STATE') {
    sendResponse({ focusState, sessionState });
  } 
  else if (message.type === 'START_SESSION') {
    // Start monitoring session
    sessionState.isActive = true;
    sessionState.goal = message.goal;
    sessionState.startTime = message.startTime;
    
    console.log('🎯 Session started:', sessionState);
    
    showNotification(
      '🎯 Focus Session Started',
      `Let's focus on: ${message.goal}`
    );
    
    sendResponse({ success: true, sessionState });
  }
  else if (message.type === 'END_SESSION') {
    // Stop monitoring session
    const duration = Math.floor(message.duration / 60);
    
    sessionState.isActive = false;
    sessionState.goal = null;
    sessionState.startTime = null;
    
    console.log('🛑 Session ended after', duration, 'minutes');
    
    showNotification(
      '🛑 Focus Session Ended',
      `Great work! You focused for ${duration} minutes.`
    );
    
    sendResponse({ success: true, duration });
  }
  else if (message.type === 'TRIGGER_INTERVENTION') {
    showNotification(
      '🎯 Focus Intervention',
      'Time to get back on track!'
    );
    sendResponse({ success: true });
  }

  return true; // Keep channel open for async response
});

console.log('✅ Background monitoring started');
console.log('🔍 Watching for tab switches, URL changes, and idle state');

