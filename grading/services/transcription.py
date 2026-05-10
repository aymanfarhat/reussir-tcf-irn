from __future__ import annotations

from django.conf import settings
from openai import OpenAI


def transcribe_audio_file(path: str) -> str:
    if not settings.OPENAI_API_KEY:
        return ""

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    with open(path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model=settings.OPENAI_TRANSCRIPTION_MODEL,
            file=audio_file,
            response_format="text",
            language=settings.OPENAI_TRANSCRIPTION_LANGUAGE or None,
            prompt=(
                "Transcribe the French answer exactly as spoken. "
                "Preserve hesitations when meaningful, but do not translate."
            ),
        )

    if isinstance(transcription, str):
        return transcription.strip()
    return transcription.text.strip()
