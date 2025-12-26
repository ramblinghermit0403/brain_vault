---
description: Get the current status and features of the application
---

This workflow helps you understand the current state of the Brain Vault application by examining its core components.

1. **Backend Analysis**
   - Read `backend/app/routers/` to identify available API endpoints and core features (e.g., Ingestion, Retrieval, Memory, Chat).
   - Check `backend/app/main.py` to see how routers are registered.

2. **Frontend Analysis**
   - Read `frontend/src/views/` to see the primary user interface modules (e.g., Dashboard, Inbox, Editor, Map).
   - Read `frontend/src/stores/` to understand the data flow and state management.

3. **Domain Model Analysis**
   - Read `backend/app/models/` to understand the data entities and relationships.

4. **Progress Tracking**
   - Check `<appDataDir>/brain/<conversation-id>/task.md` (if it exists) to see the progress of the most recent task.
   - Check for any `implementation_plan.md` or `walkthrough.md` files in the brain directory.

5. **Summary**
   - Synthesize the findings into a report covering:
     - **Major Features**: List established functionalities.
     - **Current Task**: Describe what is currently being worked on or verified.
     - **Overall Health**: Mention any known issues (e.g., database malformation, build errors).
