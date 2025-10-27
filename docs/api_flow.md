# FocusAura API Flow

This document explains how data flows through the FocusAura system, from distraction detection to intervention delivery.

## High-Level Flow

```
User Activity → Chrome Extension → FastAPI Backend → You.com APIs → Response → FocusCard UI
```

## Detailed Step-by-Step Flow

### 1. Distraction Detection (Extension)

The Chrome extension monitors user activity:

- **Tab Switching**: Detects when user switches from "work" context to "distraction" site (e.g., Google Docs → YouTube)
- **Idle Time**: Detects extended idle periods during work sessions
- **Context Tracking**: Records time spent on task, current work context, and user's stated goal

When a distraction is detected, the extension builds a `FocusEvent` payload:

```json
{
  "goal": "Finish Section 2 by 3 PM",
  "context_title": "Project_Proposal.docx",
  "context_app": "Google Docs",
  "time_on_task_minutes": 42,
  "event": "switched_to_youtube"
}
```

### 2. Backend Processing (FastAPI)

The extension POSTs the `FocusEvent` to `http://localhost:8000/intervention`.

The FastAPI backend:

1. Validates the incoming data using Pydantic models
2. Calls `compose_intervention(event)` in `logic/compose_intervention.py`
3. Returns structured JSON response

### 3. You.com API Orchestration

The `compose_intervention()` function orchestrates three parallel API calls:

#### A. Web Search API Call
- **Purpose**: Find evidence-based focus recovery techniques
- **Query**: "focus recovery techniques after distraction neuroscience"
- **Output**: Top 3-5 credible sources with actionable advice
- **Example**: "Stanford study shows 90-second walks reset prefrontal cortex"

#### B. News API Call
- **Purpose**: Retrieve recent behavioral science studies
- **Query**: Topics like "attention", "deep work", "context switching"
- **Output**: Headlines and summaries from last 6 months
- **Example**: "Harvard Medical (Jan 2024): Box breathing reduces cortisol 34%"

#### C. Smart/Research API Call
- **Purpose**: Synthesize personalized advice from all gathered context
- **Input**: User context + Web Search results + News results
- **Output**: Single, coherent recommendation tailored to this user's situation
- **Example**: "Given your 42-minute focus block, research suggests a 90-second physical reset..."

### 4. Intervention Composition

The backend fuses results from all three APIs into a single `InterventionResponse`:

```json
{
  "action_now": "Stand up and take a 90-second walk—no phone.",
  "why_it_works": "Stanford research shows brief walks reset the prefrontal cortex and reduce switching cost from entertainment to deep work. You've already invested 42 minutes—don't lose momentum.",
  "goal_reminder": "Your goal: Finish Section 2 by 3 PM",
  "citation": "Oppezzo & Schwartz, Stanford (2023)"
}
```

### 5. FocusCard Display (Extension)

The extension receives the intervention and displays it in a floating card overlay:

- **Visual Design**: Glassmorphism effect, bottom-right position, non-intrusive
- **Content**: Action, reasoning, goal reminder, citation
- **Interaction**: Two buttons ("I'm back" / "Later")

### 6. Recovery Tracking

When user clicks "I'm back":

- Recovery count increments
- Minutes saved estimate updates (+6 minutes per recovery)
- Card dismisses
- Metrics persist to `chrome.storage.local`

## Privacy Model

**What we DO NOT send:**
- Raw document text
- Screenshots
- Keystroke content
- URLs with sensitive query params

**What we DO send:**
- Abstract context: e.g., "user worked 42 minutes on 'strategy doc'"
- User's stated goal
- Distraction event type

This minimal data model enables powerful interventions while respecting privacy.

## Performance Targets

- **Total latency**: < 1 second from distraction event to card display
- **Backend response time**: < 500ms for /intervention endpoint
- **You.com API calls**: Run in parallel to minimize latency

## Error Handling

- If You.com APIs fail, backend falls back to template-based interventions
- If backend is unreachable, extension shows generic recovery message
- All errors logged for debugging but don't interrupt user experience

---

This architecture demonstrates You.com's mission: **search → reason → act** in real time, precisely when the user needs it most.
