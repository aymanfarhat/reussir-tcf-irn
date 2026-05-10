# TCF IRN App

Django web app for helping students complete timed TCF IRN oral and written simulations, then receive structured grading feedback.

## Development

Install or sync dependencies:

```bash
uv sync
```

Optional local `.env`:

```bash
OPENAI_API_KEY=sk-...
OPENAI_GRADING_MODEL=gpt-5.5
OPENAI_IMPROVEMENT_MODEL=gpt-5.5
OPENAI_AUDIO_GRADING_MODEL=gpt-audio
OPENAI_TRANSCRIPTION_MODEL=gpt-4o-mini-transcribe
OPENAI_TRANSCRIPTION_LANGUAGE=fr
```

Run database migrations:

```bash
uv run python manage.py migrate
```

Import the question bank:

```bash
uv run python manage.py import_question_bank ../product_research/question_bank.json
```

Start the development server:

```bash
uv run python manage.py runserver
```

Run tests:

```bash
uv run python manage.py test
```

When `OPENAI_API_KEY` is not set, grading uses a local development stub so the end-to-end simulator remains testable. Set the key to use OpenAI for transcription, structured grading, improved response rewrites, and optional audio-aware oral delivery feedback.

The main dashboard starts full oral/written simulations. `/practice/` starts a single targeted task by task type and theme while reusing the same timed task pages, grading, reports, and history.
