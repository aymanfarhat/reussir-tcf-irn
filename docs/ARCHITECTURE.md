# Architecture

## Overview

The app is now a full-stack monorepo:

- `frontend/`: Nuxt 3 SSR frontend.
- `backend/`: Django 5.2 + DRF backend.
- `product_research/`: source exam research and question bank.

The frontend is the user-facing application. Django is the system of record, API surface, admin back office, grading engine, OpenAI integration point, and future Celery worker host.

## Request Flow

Browser requests go to Nuxt.

- Page requests render through Nuxt SSR.
- Browser API calls use same-origin `/api/*`.
- `frontend/server/api/[...path].ts` proxies those requests to Django `/api/*`.
- The proxy forwards cookies and `X-CSRFToken` for unsafe methods.
- JSON responses are camelized for Vue; Django remains snake_case internally.

This avoids browser-to-Django CORS and keeps authentication cookie handling centralized in Nuxt.

## Backend

Backend stack:

- Django 5.2
- Django REST Framework
- drf-spectacular OpenAPI docs
- Postgres through `DATABASE_URL`
- SQLite fallback for direct local tests when `DATABASE_URL` is absent
- Redis cache
- Celery configured for future background jobs
- Gunicorn for container runtime
- Django Admin

Important backend paths:

- `backend/tcf_irn/settings.py`
- `backend/tcf_irn/urls.py`
- `backend/simulations/api/`
- `backend/exams/`
- `backend/simulations/`
- `backend/grading/`
- `backend/media/`

API docs:

- `/api/schema/`
- `/api/docs/`

## Frontend

Frontend stack:

- Nuxt 3
- Vue 3 Composition API
- strict TypeScript
- Tailwind CSS 4
- Nitro server routes as BFF proxy

Important frontend paths:

- `frontend/pages/`
- `frontend/components/`
- `frontend/composables/`
- `frontend/server/api/[...path].ts`
- `frontend/server/utils/djangoProxy.ts`
- `frontend/assets/css/base.css`

The design system uses TCF-specific tokens and reusable classes:

- `.tcf-card`
- `.tcf-btn`
- `.tcf-input`
- `.tcf-badge`

## Services

Docker Compose local services:

- `frontend`: Nuxt dev server, port `3000`
- `web`: Django + Gunicorn, port `8000`
- `db`: Postgres 16
- `redis`: Redis 7
- `celery_worker`: prepared Celery worker
- `flower`: optional monitoring profile

Deploy override adds Caddy and makes frontend/backend/database services internal.

## Data And Media

Question-bank data is imported from `product_research/question_bank.json`.

Local generated files:

- oral uploads: `backend/media/oral_recordings/`
- question TTS cache: `backend/media/question_tts/`
- collected static: `backend/staticfiles/`

These are ignored by git and should be persisted as Docker volumes in deployed environments.

## Legacy Django Templates

The old Django templates remain in `backend/templates/` for transition safety, but the intended user-facing surface is Nuxt. New user-facing work should happen in `frontend/`.
