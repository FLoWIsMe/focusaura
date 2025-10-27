# FocusAura Loom Demo Script

**Duration**: 90 seconds
**Goal**: Show judges the full intervention flow in action

---

## Pre-Recording Setup

- [ ] Backend running: `uvicorn main:app --reload`
- [ ] Extension loaded in Chrome (dev mode)
- [ ] Terminal visible with clean prompt
- [ ] Browser tab: Open on a "work" context (e.g., Google Docs)
- [ ] Second browser tab: YouTube ready to switch to
- [ ] Audio: Clear, minimal background noise
- [ ] Screen: 1920x1080, hide desktop clutter

---

## Shot 1: The Setup (10 seconds)

**Visual**: Chrome with FocusAura extension open

**Narration**:
"This is FocusAura. I'm working on my project proposal—deadline is 3 PM."

**Actions**:
1. Click extension icon
2. Show Goal Setter with goal: "Finish Section 2 by 3 PM"
3. Show Dashboard: 0 recoveries, 0 minutes saved

---

## Shot 2: The Distraction (5 seconds)

**Visual**: Switch from Google Docs to YouTube tab

**Narration**:
"I get distracted—switch to YouTube."

**Actions**:
1. Click to YouTube tab
2. Pause briefly (simulate browsing)

---

## Shot 3: The Trigger (10 seconds)

**Visual**: Click extension icon, hit "Simulate Distraction" button

**Narration**:
"FocusAura detects the distraction and triggers an intervention."

**Actions**:
1. Click extension icon
2. Click "Simulate Distraction" button
3. **Cut to terminal view**

---

## Shot 4: Backend Processing (15 seconds)

**Visual**: Terminal showing API call logs

**Narration**:
"The backend calls You.com's APIs in parallel—Web Search, News, and Smart Research—to synthesize a personalized intervention."

**Actions**:
1. Show terminal output:
   ```
   → Calling You.com Web Search API...
   → Calling You.com News API...
   → Calling You.com Smart/Research API...
   → Intervention generated: 'Take a 90-second walk...'
   ```
2. Highlight the 521ms total latency

---

## Shot 5: The Intervention (20 seconds)

**Visual**: FocusCard appears in bottom-right corner

**Narration**:
"And here's the intervention. Not generic advice—personalized, science-backed guidance."

**Actions**:
1. **Cut back to browser**
2. FocusCard slides in
3. Highlight each section:
   - "What to do right now: Take a 90-second walk"
   - "Why this works: Stanford research shows..."
   - "Your goal: Finish Section 2 by 3 PM"
   - Citation at bottom

---

## Shot 6: Recovery (10 seconds)

**Visual**: Click "I'm back" button

**Narration**:
"I take the walk, come back, click 'I'm back'—and my focus is recovered."

**Actions**:
1. Click "I'm back" button
2. FocusCard dismisses
3. Open extension popup
4. Show Dashboard updated:
   - Recoveries: 1
   - Minutes saved: 6

---

## Shot 7: The Vision (20 seconds)

**Visual**: Split-screen: Extension + Terminal + Architecture diagram

**Narration**:
"FocusAura is a showcase of You.com's vision: search that reasons and acts in real time, precisely when you need it most. This is agentic search—proactive, personalized, and privacy-preserving."

**Actions**:
1. Show architecture diagram (if ready)
2. Highlight You.com logo
3. End card: "FocusAura | Built with You.com APIs"

---

## Post-Recording Checklist

- [ ] Add captions for accessibility
- [ ] Include "Built for You.com Hackathon 2025" title card
- [ ] Add background music (subtle, non-intrusive)
- [ ] Export at 1080p, 30fps
- [ ] Upload to Loom or YouTube (unlisted)
- [ ] Add link to README.md and pitch deck

---

## Bonus: B-Roll Shots (Optional)

- Terminal with logs scrolling
- Extension popup transitions
- Code snippets from key files
- You.com API documentation page
- GitHub repo stats

---

**Total Duration**: ~90 seconds
**Key Message**: Real-time, personalized interventions powered by You.com's intelligence APIs
