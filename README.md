# TCF IRN Practice

Full-stack practice app for timed TCF IRN oral and written production simulations.

## Architecture

- `frontend/`: Nuxt 3 + Vue 3 SSR frontend. Browser traffic goes through Nuxt.
- `backend/`: Django 5.2 + DRF backend. Django owns data, grading, OpenAI calls, admin, and API behavior.
- `product_research/`: source question bank and research prototype.
- `docs/`: architecture, API, deployment, and business-rule documentation.

Nuxt uses a BFF proxy: browser calls `/api/*` on the Nuxt server, and Nitro forwards to Django `/api/*` with session cookies and CSRF headers.

## Local Development

Create local env from the template:

```bash
cp .env.dev.example .env.dev
```

Run the stack:

```bash
APP_ENV_FILE=.env.dev docker compose up -d --build
APP_ENV_FILE=.env.dev docker compose exec web /opt/venv/bin/python manage.py migrate
APP_ENV_FILE=.env.dev docker compose exec web /opt/venv/bin/python manage.py import_question_bank /product_research/question_bank.json
```

Useful URLs:

- Frontend: http://127.0.0.1:3000
- Backend API: http://localhost:8000/api/
- API docs: http://localhost:8000/api/docs/
- Django Admin: http://localhost:8000/admin/
- Flower: `APP_ENV_FILE=.env.dev docker compose --profile monitoring up flower`

`docker compose` defaults to `.env.dev.example` so config validation works in a fresh clone. Use `APP_ENV_FILE=.env.dev` whenever you want your local secrets and OpenAI key loaded into containers.

## Direct Commands

Backend:

```bash
cd backend
uv sync
uv run python manage.py check
uv run python manage.py test
uv run python manage.py migrate
```

Frontend:

```bash
cd frontend
npm install
npm run dev
npm run build
```

## Runtime Notes

- Postgres is the Docker/runtime database.
- SQLite remains a fallback for direct local backend tests when `DATABASE_URL` is absent.
- Redis and Celery are configured, but grading still runs synchronously for now.
- Generated media, question TTS cache, node modules, virtualenvs, and local env files are ignored.
