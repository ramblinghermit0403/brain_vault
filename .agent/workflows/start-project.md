---
description: starts the development server for the project
---

open 3 terminal windows

run the commands

1) cd backend
   venv/scripts/activate
   uvicorn app.main:app --reload

2)cd backend
  venv/scripts/activate
  celery -A app.celery_app worker --loglevel=info -P solo

3)cd frontend
  npm run dev


