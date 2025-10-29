# FocusAura Docker Setup

Quick guide for running FocusAura backend with Docker Compose.

## Prerequisites

- Docker Desktop installed ([download](https://www.docker.com/products/docker-desktop/))
- Your You.com API key

## Quick Start

### 1. Set up environment variables

Make sure your `backend/.env` file exists with your API key:

```bash
# backend/.env
YOU_API_KEY=your-you-api-key-here
YOU_API_MODE=live
YOU_API_DEBUG=true
```

### 2. Start the backend

```bash
# From the project root directory
docker compose up
```

Or run in detached mode (background):

```bash
docker compose up -d
```

### 3. Test the API

The backend will be available at `http://localhost:8000`

```bash
# Health check
curl http://localhost:8000/health

# Test intervention endpoint
curl -X POST http://localhost:8000/intervention \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Finish writing page 1",
    "context_title": "Project_Proposal.docx",
    "context_app": "Google Docs",
    "time_on_task_minutes": 42,
    "event": "switched_to_youtube"
  }'
```

## Docker Commands

### Start services
```bash
docker compose up
```

### Stop services
```bash
docker compose down
```

### Rebuild after code changes
```bash
docker compose up --build
```

### View logs
```bash
docker compose logs -f backend
```

### Restart service
```bash
docker compose restart backend
```

### Run with specific environment variables
```bash
YOU_API_MODE=demo docker compose up
```

## Development Mode

The compose.yml is configured for development with:
- **Hot reload**: Code changes automatically reload the server
- **Volume mounts**: Your local code is mounted into the container
- **Debug mode**: Detailed API logging enabled

## Production Deployment

For production, create a `compose.prod.yml`:

```yaml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: focusaura-backend-prod
    ports:
      - "8000:8000"
    environment:
      - YOU_API_MODE=live
      - YOU_API_DEBUG=false
    env_file:
      - ./backend/.env
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
    restart: always
```

Then run:
```bash
docker compose -f compose.prod.yml up -d
```

## Troubleshooting

### Port already in use
If port 8000 is already in use, stop the local uvicorn server:
```bash
pkill -f uvicorn
```

### Can't connect to API
Check if the container is running:
```bash
docker compose ps
docker compose logs backend
```

### Environment variables not loading
Make sure `backend/.env` exists and contains valid values:
```bash
cat backend/.env
```

### Rebuild from scratch
```bash
docker compose down
docker compose build --no-cache
docker compose up
```

## Network Configuration

The backend runs on a dedicated bridge network (`focusaura-network`) for isolation.

To connect other services:
```yaml
services:
  another-service:
    networks:
      - focusaura-network
```

## Health Checks

The backend includes health checks that:
- Run every 30 seconds
- Hit the `/health` endpoint
- Mark container unhealthy after 3 failed attempts
- Allow 10 seconds startup time

View health status:
```bash
docker compose ps
```
