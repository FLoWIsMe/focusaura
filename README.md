# FocusAura

FocusAura is an Chrome extension with AI focus assistants that watches for distraction events (like switching tabs mid-work session) and responds with personalized, science-backed micro-interventions powered by http://you.com's real-time intelligence APIs.

When you drift, FocusAura catches you—gently—and shows you exactly what to do next, backed by live research and actionable advice.

## Architecture

```
Chrome Extension (React)
    ↓
    [Distraction Event: user got distracted]
    ↓
FastAPI Backend
    ↓
    [Calls You.com APIs in parallel]
    ├─→ Web Search API (evidence-based focus techniques)
    ├─→ News API (recent neuroscience studies)
    └─→ Smart/Research API (personalized synthesis)
    ↓
Chrome Extension
    └─→ Shows overlay with nudge
```

## Quick Start
### Running Locally

**Option 1: Docker**

```bash
# From project root
docker compose up
```

Backend runs at `http://localhost:8000`. See [DOCKER.md](DOCKER.md) for full Docker documentation.

**Option 2: Chrome Extension Mode**

**Step 1 - Start Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Step 2 - Build Extension:**
```bash
cd extension
npm install
npm run build
cp public/manifest.json dist/
cp public/icon*.png dist/ 2>/dev/null || true
```

**Step 3 - Load in Chrome:**
1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top-right corner)
3. Click "Load unpacked"
4. Select the `extension/dist` folder
5. Click the FocusAura extension icon in your Chrome toolbar

---

### Testing the Demo

1. **Set a goal** 
2. Click **"Save Goal"**
3. Click the yellow **"🎬 Simulate Distraction (Demo)"** button
4. Watch it appear with personalized interventions.

## Security & Privacy Positioning

**FocusAura does NOT capture or transmit:**
- Raw document text
- Screenshots
- Keystroke content
- URLs with sensitive query params

**FocusAura ONLY sends:**
- Abstract context: e.g., "user worked 42 minutes on 'strategy doc', then switched to YouTube"
- User's stated goal: e.g., "Finish Section 2 by 3 PM"

This minimal data model enables powerful interventions while respecting user privacy.

## Why This Matters for You.com

FocusAura is a living showcase of You.com's mission: **search → reason → act** in real time, for a single human, at the moment they need it most.

Traditional search is pull-based: you go to the engine. FocusAura is push-based: the engine comes to you, precisely when your brain needs a reset, with research-backed advice synthesized from the entire web in under 500ms.

This is the future of agentic search—context-aware, proactive, and human-centered.

## Tech Stack

- **Frontend**: React 18 + Vite, Chrome Extension Manifest V3
- **Backend**: Python 3.11+, FastAPI, Pydantic
- **Intelligence**: You.com Web Search API, News API, Smart/Research API
- **Styling**: Custom CSS with glassmorphism effects

## MVP Scope (Hackathon Build)

✅ Goal-setting UI
✅ Dashboard with recovery metrics
✅ Simulated distraction trigger
✅ FastAPI `/intervention` endpoint
✅ Structured You.com API client stubs
✅ FocusCard overlay with intervention display

🚧 Real-time tab monitoring (stubbed for demo)
🚧 Chrome idle detection (stubbed for demo)
🚧 Persistent storage / user accounts (out of scope)

---

Built for the You.com Hackathon 2025 🚀
