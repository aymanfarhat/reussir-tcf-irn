# API Reference

The Django backend exposes DRF endpoints under `/api/`. The Nuxt frontend calls same-origin `/api/*`; its BFF proxy forwards to Django and maps snake_case responses to camelCase for Vue.

## Auth

- `GET /api/auth/csrf/`: set/read CSRF token.
- `GET /api/auth/me/`: current authenticated user.
- `POST /api/auth/login/`: `{ "username": "...", "password": "..." }`.
- `POST /api/auth/signup/`: `{ "username": "...", "password": "...", "password2": "..." }`.
- `POST /api/auth/logout/`.

## Simulation

- `GET /api/test-definitions/`
- `GET /api/practice-options/`
- `GET /api/sessions/`
- `POST /api/sessions/start/`: `{ "mode": "full" | "oral" | "written" }`
- `POST /api/practice/start/`: `{ "task_number": 4, "theme": "travail" }`
- `GET /api/sessions/{uuid}/`
- `DELETE /api/sessions/{uuid}/`
- `GET /api/sessions/{uuid}/report/`

## Attempts

- `GET /api/sessions/{uuid}/attempts/{order}/`
- `POST /api/sessions/{uuid}/attempts/{order}/submit/`
- `GET /api/sessions/{uuid}/attempts/{order}/grade/`
- `POST /api/sessions/{uuid}/attempts/{order}/retry-grade/`: re-run grading for the saved submitted answer/transcript. Returns `400` if the task has not been submitted or has no saved production.
- `GET /api/sessions/{uuid}/attempts/{order}/question-audio/`

Written submit accepts JSON:

```json
{ "answer_text": "..." }
```

Oral submit accepts multipart form data:

- `transcript_text`
- `audio_file`

## Generated Docs

- Schema: `/api/schema/`
- Swagger UI: `/api/docs/`
