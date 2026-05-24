FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 8000

CMD ["gunicorn", "--workers=2", "--timeout=300", "--bind=0.0.0.0:8000", "tcf_irn.wsgi:application"]
