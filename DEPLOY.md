# Deployment Guide

This repository ships with a deploy-shape Docker Compose override and Caddy.

## 1. Prepare Environment

Create `.env.dev` on the server from `.env.dev.example` and set production values:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=0`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `DATABASE_URL`
- `POSTGRES_*`
- `REDIS_URL`
- `OPENAI_API_KEY`
- `DOMAIN_NAME`
- `ACME_EMAIL`

## 2. Start Services

```bash
APP_ENV_FILE=.env.dev docker compose -f docker-compose.yml -f docker-compose.deploy.yml up -d --build
APP_ENV_FILE=.env.dev docker compose exec web /opt/venv/bin/python manage.py migrate
APP_ENV_FILE=.env.dev docker compose exec web /opt/venv/bin/python manage.py import_question_bank /product_research/question_bank.json
APP_ENV_FILE=.env.dev docker compose exec web /opt/venv/bin/python manage.py createsuperuser
```

The compose files default to `.env.dev.example` for validation. Set `APP_ENV_FILE=.env.dev` for real local, staging, or production runs.

## 3. Public Routing

Caddy routes:

- `/` to Nuxt
- `/api/*` to Django
- `/admin/*` to Django
- `/static/*` from the shared static volume
- `/media/*` from the shared media volume

## 4. Operational Notes

- Keep `backend_media`, `backend_static`, `postgres_data`, `redis_data`, `caddy_data`, and `caddy_config` volumes persistent.
- Run database backups from the `db` service.
- Flower is opt-in through the `monitoring` profile and should not be exposed publicly.
- Celery workers are prepared for future async grading/background jobs; current grading remains sync.
