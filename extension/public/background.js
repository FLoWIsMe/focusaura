/**
 * Background Service Worker for FocusAura
 * 
 * This runs continuously in the background and monitors user activity.
 * Service workers are the Manifest V3 way to handle background tasks.
 */

console.log('🚀 FocusAura background service worker loaded');

// Track focus state
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

/**
 * Monitor tab switches
 */
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  try {
    const tab = await chrome.tabs.get(activeInfo.tabId);
    const classification = classifySite(tab.url);
    
    console.log('🔄 Tab switched:', {
      tabId: activeInfo.tabId,
      url: tab.url,
      title: tab.title,
      classification: classification,
      timestamp: new Date().toISOString()
    });

    // Update state
    focusState.currentTab = activeInfo.tabId;
    focusState.currentUrl = tab.url;

    // Show intervention page for distraction sites
    if (classification === 'distraction') {
      const hostname = new URL(tab.url).hostname;
      
      // Open intervention page in a new tab with error handling
      // setTimeout(() => {
      //   chrome.tabs.create({
      //     url: chrome.runtime.getURL(`intervention.html?site=${encodeURIComponent(hostname)}&url=${encodeURIComponent(tab.url)}`)
      //   }).catch(error => {
      //     console.error('Failed to open intervention tab:', error);
      //   });
      // }, 100);
      
      showNotification(
        '⚠️ Distraction Detected',
        `Switched to ${hostname}`
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
 * Monitor tab URL updates (navigation within same tab)
 */
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.url) {
    const classification = classifySite(changeInfo.url);
    
    console.log('🌐 Tab URL updated:', {
      tabId,
      url: changeInfo.url,
      title: tab.title,
      classification: classification,
      timestamp: new Date().toISOString()
    });

    // Show intervention page for navigation to distraction sites
    if (classification === 'distraction') {
      const hostname = new URL(changeInfo.url).hostname;
      
      // Open intervention page in a new tab with error handling
      // setTimeout(() => {
      //   chrome.tabs.create({
      //     url: chrome.runtime.getURL(`intervention.html?site=${encodeURIComponent(hostname)}&url=${encodeURIComponent(changeInfo.url)}`)
      //   }).catch(error => {
      //     console.error('Failed to open intervention tab:', error);
      //   });
      // }, 100);
      
      showNotification(
        '⚠️ Distraction Site',
        `Navigated to ${hostname}`
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
    sendResponse(focusState);
  } else if (message.type === 'TRIGGER_INTERVENTION') {
    showNotification(
      '🎯 Focus Intervention',
      'Time to get back on track!'
    );
  }

  return true; // Keep channel open for async response
});

console.log('✅ Background monitoring started');
console.log('🔍 Watching for tab switches, URL changes, and idle state');

