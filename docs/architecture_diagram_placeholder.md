# FocusAura Architecture Diagram

This document describes the architecture diagram we will create for the final pitch deck and GitHub README.

## Diagram Elements

### Box 1: Chrome Extension (Frontend)
- **Color**: Purple gradient (#667eea → #764ba2)
- **Components**:
  - Goal Setter UI
  - Dashboard with metrics
  - Monitor Engine (tab/idle detection)
  - FocusCard overlay renderer
- **Icon**: Chrome logo + brain icon

### Box 2: FastAPI Backend
- **Color**: Green (#2ecc71)
- **Components**:
  - `/intervention` endpoint
  - Pydantic validation layer
  - `compose_intervention()` orchestrator
- **Icon**: Python logo + API symbol

### Box 3: You.com Intelligence Layer
- **Color**: You.com brand color (blue)
- **Components**:
  - Web Search API client
  - News API client
  - Smart/Research API client
- **Icon**: You.com logo + magnifying glass

### Arrows & Data Flow

**Arrow 1**: Extension → Backend
- **Label**: `POST /intervention`
- **Data**: FocusEvent JSON payload
- **Style**: Solid line, purple

**Arrow 2**: Backend → You.com (3 parallel calls)
- **Label A**: "Web Search: focus techniques"
- **Label B**: "News: recent studies"
- **Label C**: "Smart: synthesize advice"
- **Style**: Three parallel dashed lines, green → blue

**Arrow 3**: You.com → Backend
- **Label**: "Fused intervention data"
- **Style**: Solid line, blue → green

**Arrow 4**: Backend → Extension
- **Label**: InterventionResponse JSON
- **Style**: Solid line, green → purple

**Arrow 5**: Extension → User
- **Label**: "FocusCard overlay display"
- **Style**: Thick arrow, purple, points to user icon

### Additional Elements

**User Icon**: Human silhouette at top center
- Shows distraction event (YouTube icon) triggering the flow

**Data Privacy Badge**: Small shield icon
- Label: "Only abstract context sent, never raw content"

**Performance Metric**: Clock icon
- Label: "< 500ms total latency"

**Recovery Loop**: Curved arrow from User back to Extension
- Label: "User clicks 'I'm back' → metrics updated"

## Diagram Style

- **Tool**: Use Figma, Excalidraw, or draw.io
- **Style**: Clean, modern, hackathon-ready
- **Layout**: Horizontal left-to-right flow
- **Color scheme**: Match FocusAura brand (purple gradients)
- **Font**: Sans-serif, professional

## Annotations for Judges

Include small text annotations:
1. "Real-time API orchestration"
2. "Privacy-preserving context model"
3. "Evidence-based interventions"
4. "Agentic search: proactive, not reactive"

---

**File to create**: `architecture_diagram.png` or `architecture_diagram.svg`

**Place in**: `/docs/` and embed in README.md
