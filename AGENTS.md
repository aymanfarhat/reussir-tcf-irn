# AGENTS.md

## Project Overview

This repository is a full-stack web app that helps students practice TCF IRN French oral and written production tasks in timed conditions.

The app lets learners run randomized simulations or targeted single-task practice, answer each selected prompt, and receive LLM-based grading feedback aligned with the task-specific rubrics in the imported question bank.

## Repository Layout

- `backend/`: Django 5.2 + DRF backend, API, admin, grading, import, media, future Celery workers.
- `frontend/`: Nuxt 3 + Vue 3 SSR frontend.
- `docs/`: architecture, API, business rules, and deployment docs.
- `product_research/`: source research files and `question_bank.json`.
- `REFACTOR.md`: full-stack refactor backlog and verification status.

The browser talks to Nuxt. Nuxt proxies `/api/*` to Django through a BFF route with cookie and CSRF forwarding.

## Commands

Root Docker stack:

```bash
cp .env.dev.example .env.dev
APP_ENV_FILE=.env.dev docker compose up -d --build
APP_ENV_FILE=.env.dev docker compose exec web /opt/venv/bin/python manage.py migrate
APP_ENV_FILE=.env.dev docker compose exec web /opt/venv/bin/python manage.py import_question_bank /product_research/question_bank.json
```

The compose files default to `.env.dev.example` so config validation works without local secrets. Use `APP_ENV_FILE=.env.dev` for real runtime commands.

Backend:

```bash
cd backend
uv sync
uv run python manage.py check
uv run python manage.py test
uv run python manage.py migrate
uv run python manage.py import_question_bank ../product_research/question_bank.json
```

Frontend:

```bash
cd frontend
npm install
npm run dev
npm run build
npm run lint
```

## Source Materials

Important research files:

- `product_research/EXAM_STRUCTURE.md`
- `product_research/QUESTION_BANK_GUIDANCE.md`
- `product_research/question_bank.json`
- `product_research/app.py`
- `product_research/index.html`

Treat the imported database rows seeded from `question_bank.json` as the production source of behavior. Do not edit research files unless explicitly requested.

## TCF IRN Scope

The product focuses on:

- `expression_orale`: oral production
- `expression_ecrite`: written production

Current bank shape:

- 60 questions total
- 10 questions per task number
- task numbers 1-3 for oral production
- task numbers 4-6 for written production

## Business Rules

- Oral simulations select one active question each for tasks 1, 2, and 3.
- Written simulations select one active question each for tasks 4, 5, and 6.
- Full simulations select one active question each for tasks 1 through 6.
- Practice mode selects one active question by optional task number and/or theme.
- Task navigation remains sequential.
- Opening a task starts its server-side deadline.
- The frontend timer is informative; the backend stores the late-submission flag.
- Written word limits are first-class validation and grading inputs.
- Oral responses may use browser recording, manual transcript, or OpenAI transcription.
- Question audio playback is AI-generated with OpenAI TTS and cached under `backend/media/question_tts/`.

## LLM Grading Rules

The grader follows the dynamic prompt strategy originally explored in `product_research/app.py`.

The grader prompt must include exam context, exact candidate prompt, timing/word constraints, expected structure, required elements, expected vocabulary and grammar, reference answers as examples, evaluation focus, rubric dimensions, level descriptors, score bands, automatic failure conditions, and candidate production.

Reference answers are examples, not canonical answers. The grader must not require the learner to match them.

Structured grading output must remain JSON. The `dimensions` field must remain a list of objects with `dimension_id`; do not convert it to an arbitrary-key dictionary because OpenAI strict structured outputs reject that schema.

After successful grading, the app requests a separate improved version of the learner's own response. This should preserve learner intent and personal facts, avoid copying reference answers, and target stronger B2-level French within the same task constraints.

Direct oral audio delivery feedback is optional. Browser recordings are `webm` and should not be sent to OpenAI direct audio feedback as `opus`; direct audio feedback currently supports `wav` and `mp3` only. Transcript-based grading should still continue.

## Development Notes

- Keep backend behavior in Django services/models/API serializers, not Vue.
- Keep frontend behavior task-local: timers, word counts, recording, question playback.
- Keep Django Admin editable for all exam/test/question/grading content.
- Use DRF API tests for backend behavior and Nuxt build/lint for frontend regressions.
- Do not commit runtime files: `.env.dev`, virtualenvs, SQLite DBs, media, static build output, Nuxt build output, or `node_modules`.
