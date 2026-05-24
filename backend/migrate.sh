#!/usr/bin/env bash
set -euo pipefail

uv run python manage.py migrate
uv run python manage.py import_question_bank "${QUESTION_BANK_PATH:-../product_research/question_bank.json}"
