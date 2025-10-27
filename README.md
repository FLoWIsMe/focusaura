# FocusAura

**AI focus assistant that senses distraction and brings you back into flow.**

## Overview

FocusAura is an intelligent Chrome extension that watches for distraction events (like switching to YouTube mid-work session) and responds with personalized, science-backed micro-interventions powered by You.com's real-time intelligence APIs.

When you drift, FocusAura catches you—gently—and shows you exactly what to do next, backed by live research and actionable advice.

## Architecture

```
Chrome Extension (React)
    ↓
    [Distraction Event: user switched to youtube.com]
    ↓
FastAPI Backend
    ↓
    [Calls You.com APIs in parallel]
    ├─→ Web Search API (evidence-based focus techniques)
    ├─→ News API (recent neuroscience studies)
    └─→ Smart/Research API (personalized synthesis)
    ↓
    [Fused intervention returned as JSON]
    ↓
Chrome Extension
    └─→ Shows FocusCard overlay with nudge
```

## Local Development

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The FastAPI server will run on `http://localhost:8000`. Visit `/docs` for the interactive API documentation.

### Extension Setup

```bash
cd extension
npm install
npm run dev
```

Then load the extension in Chrome:
1. Navigate to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `extension/dist` folder (generated after build)

For development, you can test the intervention flow using the "Simulate Distraction" button in the popup UI.

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
