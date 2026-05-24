# Backend AGENTS.md

## Purpose

`backend/` is the Django system of record for the TCF IRN practice app. It owns:

- imported exam/question/rubric data
- simulation sessions and task attempts
- grading, improved responses, transcription, audio feedback, and question TTS
- DRF API endpoints
- Django Admin
- future Celery task execution

## Commands

```bash
uv sync
uv run python manage.py check
uv run python manage.py test
uv run python manage.py migrate
uv run python manage.py import_question_bank ../product_research/question_bank.json
```

In Docker, the question bank is mounted at `/product_research/question_bank.json`.

## API

DRF endpoints live under `simulations/api/` and are mounted at `/api/`.

Keep business behavior in existing services where possible:

- `simulations.services.start_session`
- `simulations.services.navigation`
- `simulations.services.scoring`
- `simulations.services.question_audio`
- `grading.services.*`

Do not duplicate grading or question-selection rules in serializers.

## Runtime

- Postgres is configured through `DATABASE_URL`.
- SQLite remains fallback for direct local tests.
- Redis is configured for cache/Celery.
- Celery is configured but grading is still synchronous.
- Local media and generated question TTS files live under `backend/media/`.
