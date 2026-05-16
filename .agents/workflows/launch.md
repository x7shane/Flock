---
description: Launch the Flock development server (backend + frontend)
---

## Launch Flock Locally

The FastAPI backend serves the frontend as static files on port 8000.

// turbo
1. Activate the virtualenv and start uvicorn:
```bash
cd /home/shades/Documents/Claude_Projects/Flock/backend && source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. Open the app in the browser:
   - Frontend: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

## Stop the server
Press `Ctrl+C` in the terminal running uvicorn.

## Check the branch
```bash
git -C /home/shades/Documents/Claude_Projects/Flock branch
```
All UI work is on `feature/sage-stone-ui-integration`.
