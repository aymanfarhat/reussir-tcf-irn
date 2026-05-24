# REFACTOR.md

Status key: `[done]`, `[in_progress]`, `[pending]`, `[blocked]`.

## Epic 0: Repository Reshape

- `[done]` Confirm backend repo is clean.
- `[done]` Promote `app/.git` to root Git history.
- `[done]` Rename tracked Django app files into `backend/`.
- `[done]` Add root `.gitignore` for runtime files, sample inspiration folder, node modules, media, local envs.
- `[done]` Update root docs and path references.

## Epic 1: Backend Platform

- `[done]` Add backend Dockerfile using `uv`.
- `[done]` Add Postgres database settings via `DATABASE_URL`.
- `[done]` Add Redis cache settings.
- `[done]` Add Celery app configuration.
- `[done]` Add Gunicorn runtime command.
- `[done]` Verify migrations and import command against Docker Postgres.

## Epic 2: DRF API

- `[done]` Add DRF and OpenAPI settings.
- `[done]` Add auth API endpoints.
- `[done]` Add exam/test/practice serializers.
- `[done]` Add session/history/report serializers.
- `[done]` Add task attempt submit/detail/grade serializers.
- `[done]` Add audio streaming endpoint compatibility.
- `[done]` Preserve ownership and sequential navigation checks.
- `[done]` Add DRF API tests for current user flows.

## Epic 3: Nuxt Foundation

- `[done]` Scaffold `frontend/` with Nuxt 3, TypeScript, Tailwind 4, lint/format/build scripts.
- `[done]` Add BFF proxy utility with cookie and CSRF forwarding.
- `[done]` Add generic auth/session/test/task/report BFF proxy route.
- `[done]` Add multipart and audio-stream proxy handling.
- `[done]` Add app layout, route middleware, flash handling, and session bootstrap.

## Epic 4: Design System

- `[done]` Port the reusable UI-kit pattern from the sample using TCF IRN tokens.
- `[done]` Build shared form, card, badge, button, and score components.
- `[done]` Add score ring component for task/report scores.
- `[done]` Add internal `/ui-kit` page for visual QA.
- `[done]` Keep existing color semantics for oral, written, warning, error, and success states.

## Epic 5: Frontend Feature Parity

- `[done]` Rebuild login and signup.
- `[done]` Rebuild dashboard and simulation start.
- `[done]` Rebuild targeted practice.
- `[done]` Rebuild history with delete and task result links.
- `[done]` Rebuild written task page with timer and word count.
- `[done]` Rebuild oral task page with timer, question playback, recording, transcript fallback.
- `[done]` Rebuild task feedback page with score, dimensions, audio feedback, examples, improved response, personal best.
- `[done]` Rebuild final report.
- `[pending]` Remove or stop routing to legacy Django product templates after extended manual parity testing.

## Epic 6: Compose And Deployment Docs

- `[done]` Add root `docker-compose.yml`.
- `[done]` Add `docker-compose.deploy.yml`.
- `[done]` Add `Caddyfile`.
- `[done]` Add `.env.dev.example`.
- `[done]` Add `DEPLOY.md`.
- `[done]` Update architecture/API docs.
- `[done]` Add `backend/AGENTS.md` and `frontend/AGENTS.md`.

## Epic 7: Verification

- `[done]` Run backend Django checks.
- `[done]` Run backend simulation/API tests.
- `[done]` Run full backend test suite after final docs/frontend changes.
- `[done]` Run frontend lint and build.
- `[done]` Run full Docker Compose stack.
- `[done]` Smoke-test Nuxt pages, BFF CSRF/signup/session creation, written task submit, grading, API docs, and Postgres import.
- `[done]` Browser smoke-test signup, dashboard, written test start, written answer submit, task feedback, examples, improved response, next-task link, and authenticated hard-load of history.
- `[done]` Verify history delete through the Nuxt BFF/API.
- `[pending]` Complete browser-level smoke testing for oral recording/question audio, report navigation, and admin; the in-app browser runtime hung during extended click testing after the initial smoke passed.
- `[done]` Verify no root/sample/runtime files are accidentally tracked.
