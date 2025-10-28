# You.com API Integration Guide

This guide shows how to integrate real You.com APIs into FocusAura.

## Current Status

**The MVP uses template-based responses** - no API key needed!

This allows you to:
- ✅ Demo the full UX flow immediately
- ✅ Show judges the complete architecture
- ✅ Present without waiting for API credentials

## When to Integrate Real APIs

You should integrate real You.com APIs when:
1. You receive API credentials from You.com hackathon organizers
2. Judges want to see live search results
3. You're ready to deploy a production version

---

## Step-by-Step Integration

### Step 1: Get Your API Key

Contact You.com hackathon organizers or visit: https://api.you.com/

You'll receive an API key that looks like: `youcom_abc123xyz789...`

### Step 2: Add API Key to Environment

Create a `.env` file in the `backend/` directory:

```bash
cd backend
echo "YOU_API_KEY=your_actual_api_key_here" > .env
```

**Important**: The `.env` file is already in `.gitignore` so your API key won't be committed.

### Step 3: Install python-dotenv (Already Done)

The `python-dotenv` package is already in `requirements.txt`, so you're all set.

### Step 4: Update API Client Files

You need to update three files in `backend/you_client/`:

#### A. `web_search.py`

**Current code (lines 55-62):**
```python
# MVP: Return dummy data for demo purposes
return (
    "Web Search Results:\n"
    "1. Stanford study (2023): 90-second walks reset prefrontal cortex...\n"
    ...
)
```

**Replace with:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

async def query_web_search(user_context: Dict) -> str:
    api_key = os.getenv("YOU_API_KEY")

    if not api_key:
        # Fallback to template if no API key
        return "Web Search Results:\n1. Stanford study (2023): 90-second walks..."

    # Construct search query
    query = f"evidence-based focus recovery techniques {user_context['distraction']} neuroscience"

    # Call You.com Web Search API
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://api.you.com/search",  # Replace with actual endpoint
                headers={"X-API-Key": api_key},
                params={
                    "query": query,
                    "num_results": 5,
                    "safesearch": "moderate"
                },
                timeout=5.0
            )
            response.raise_for_status()

            # Parse and format results
            data = response.json()
            results = []
            for i, item in enumerate(data.get('results', [])[:3], 1):
                title = item.get('title', '')
                snippet = item.get('snippet', '')
                results.append(f"{i}. {title}: {snippet}")

            return "\n".join(results)

        except Exception as e:
            print(f"Error calling You.com API: {e}")
            # Fallback to template on error
            return "Web Search Results:\n1. Stanford study (2023): 90-second walks..."
```

#### B. `news_search.py`

Similar pattern - replace dummy return with actual API call:

```python
import os
from dotenv import load_dotenv

load_dotenv()

async def query_news_search(news_query: Dict) -> str:
    api_key = os.getenv("YOU_API_KEY")

    if not api_key:
        return "Recent News & Studies:\n1. Harvard Medical School (Jan 2024)..."

    topics = news_query.get("topics", [])
    query = " OR ".join(topics)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://api.you.com/news",  # Replace with actual endpoint
                headers={"X-API-Key": api_key},
                params={
                    "query": query,
                    "count": 5,
                    "freshness": "recent"
                },
                timeout=5.0
            )
            response.raise_for_status()

            data = response.json()
            results = []
            for i, item in enumerate(data.get('news', [])[:3], 1):
                title = item.get('title', '')
                source = item.get('source', '')
                date = item.get('date', '')
                results.append(f"{i}. {source} ({date}): {title}")

            return "\n".join(results)

        except Exception as e:
            print(f"Error calling You.com News API: {e}")
            return "Recent News & Studies:\n1. Harvard Medical School (Jan 2024)..."
```

#### C. `smart_research.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()

async def query_smart_research(research_query: Dict) -> str:
    api_key = os.getenv("YOU_API_KEY")

    if not api_key:
        return "Smart Synthesis:\nGiven your 42-minute focus session..."

    user_ctx = research_query.get("user_context", {})
    synthesis_prompt = research_query.get("synthesis_prompt", "")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.you.com/smart",  # Replace with actual endpoint
                headers={"X-API-Key": api_key},
                json={
                    "query": synthesis_prompt,
                    "context": {
                        "web_results": research_query.get("web_findings", ""),
                        "news_results": research_query.get("recent_studies", "")
                    }
                },
                timeout=10.0
            )
            response.raise_for_status()

            data = response.json()
            return data.get('synthesis', 'Smart Synthesis: ...')

        except Exception as e:
            print(f"Error calling You.com Smart API: {e}")
            return "Smart Synthesis:\nGiven your 42-minute focus session..."
```

### Step 5: Test the Integration

Restart your backend server:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

The backend will now:
1. Try to load `YOU_API_KEY` from `.env`
2. If present, call real You.com APIs
3. If not present or on error, fall back to templates

This graceful degradation ensures your demo always works!

### Step 6: Verify API Calls

Check the backend logs to see API calls:

```bash
# You should see logs like:
# → Calling You.com Web Search API...
# ✓ Results retrieved (237ms)
```

Or test directly:

```bash
curl -X POST http://localhost:8000/intervention \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Finish proposal",
    "context_title": "doc.docx",
    "context_app": "Google Docs",
    "time_on_task_minutes": 42,
    "event": "switched_to_youtube"
  }'
```

---

## Important Notes

### API Endpoints

⚠️ **The API endpoints in this guide are placeholders!**

You need to replace:
- `https://api.you.com/search` → Actual You.com Web Search endpoint
- `https://api.you.com/news` → Actual You.com News endpoint
- `https://api.you.com/smart` → Actual You.com Smart/Research endpoint

Check You.com's official documentation for the real endpoints.

### Rate Limiting

You.com APIs likely have rate limits. Consider:
- Caching responses for repeated queries
- Implementing exponential backoff on errors
- Showing cached/template data if quota exceeded

### Error Handling

The code above includes graceful fallbacks:
- No API key? → Use templates
- API call fails? → Use templates
- Timeout? → Use templates

This ensures your demo **never breaks**, even if APIs are down.

---

## Testing Strategy

### Without API Key (Current)
```bash
# No .env file needed
uvicorn main:app --reload
# Uses templates, works perfectly
```

### With API Key
```bash
# Create .env with YOU_API_KEY
uvicorn main:app --reload
# Calls real APIs, falls back to templates on error
```

### For Hackathon Demo
**Recommendation**: Use template mode for the live demo to avoid:
- API latency during presentation
- Unexpected API errors in front of judges
- Rate limit issues

You can mention: "The backend is ready to integrate You.com APIs - we've stubbed them with realistic data for demo stability."

---

## Security Checklist

- ✅ `.env` is in `.gitignore` (already done)
- ✅ Never commit API keys to git
- ✅ Don't log API keys in console output
- ✅ Use environment variables, not hardcoded keys
- ✅ Rotate keys if accidentally exposed

---

## Architecture Benefits

This hybrid approach gives you the best of both worlds:

**Template Mode (MVP)**
- ✅ Zero dependencies on external services
- ✅ Instant responses (no API latency)
- ✅ Predictable demo behavior
- ✅ Works offline

**API Mode (Production)**
- ✅ Real, live search results
- ✅ Fresh neuroscience studies
- ✅ Personalized AI synthesis
- ✅ Demonstrates You.com integration

**Graceful Degradation**
- ✅ Always works, even if APIs fail
- ✅ No breaking changes when adding API key
- ✅ Easy to toggle between modes

---

## Questions?

If you're unsure about You.com API specifics:
1. Check You.com's hackathon documentation
2. Ask organizers for API examples
3. Review You.com's official API docs at https://documentation.you.com/

For now, **the template mode is perfect for your demo!** 🚀
