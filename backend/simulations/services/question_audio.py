from __future__ import annotations

import hashlib
import os
import uuid
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings
from django.utils.text import slugify
from openai import OpenAI
from openai import OpenAIError

from exams.models import Question


CONTENT_TYPES = {
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    "opus": "audio/ogg",
    "aac": "audio/aac",
    "flac": "audio/flac",
    "pcm": "audio/L16",
}


class QuestionAudioUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class QuestionAudioFile:
    path: Path
    content_type: str


def get_or_create_question_audio(question: Question) -> QuestionAudioFile:
    if question.section_source_id != "expression_orale":
        raise QuestionAudioUnavailable("Question audio is only available for oral tasks.")

    audio_path = question_audio_cache_path(question)
    audio_format = normalized_audio_format()
    content_type = CONTENT_TYPES.get(audio_format, "application/octet-stream")
    if audio_path.exists() and audio_path.stat().st_size > 0:
        return QuestionAudioFile(path=audio_path, content_type=content_type)

    if not settings.OPENAI_API_KEY:
        raise QuestionAudioUnavailable(
            "Question audio is unavailable because OPENAI_API_KEY is not configured."
        )

    prompt_text = build_question_audio_input(question)
    if not prompt_text:
        raise QuestionAudioUnavailable("Question audio is unavailable for an empty prompt.")

    audio_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = audio_path.parent / f".{audio_path.name}.{uuid.uuid4().hex}.tmp"

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        with client.audio.speech.with_streaming_response.create(
            model=settings.OPENAI_TTS_MODEL,
            voice=settings.OPENAI_TTS_VOICE,
            input=prompt_text,
            instructions=settings.OPENAI_TTS_INSTRUCTIONS,
            response_format=audio_format,
        ) as response:
            response.stream_to_file(tmp_path)
        os.replace(tmp_path, audio_path)
    except OpenAIError as exc:
        tmp_path.unlink(missing_ok=True)
        raise QuestionAudioUnavailable(
            "Question audio generation failed. Please try again later."
        ) from exc
    except OSError as exc:
        tmp_path.unlink(missing_ok=True)
        raise QuestionAudioUnavailable(
            "Question audio cache could not be written. Please try again later."
        ) from exc

    return QuestionAudioFile(path=audio_path, content_type=content_type)


def question_audio_cache_path(question: Question) -> Path:
    audio_format = normalized_audio_format()
    cache_hash = question_audio_cache_hash(question)
    question_slug = slugify(question.source_id) or f"question-{question.pk}"
    model_slug = slugify(settings.OPENAI_TTS_MODEL) or "tts-model"
    voice_slug = slugify(str(settings.OPENAI_TTS_VOICE)) or "voice"
    return (
        Path(settings.MEDIA_ROOT)
        / "question_tts"
        / model_slug
        / voice_slug
        / f"{question_slug}-{cache_hash}.{audio_format}"
    )


def question_audio_cache_hash(question: Question) -> str:
    material = "\n".join(
        [
            "tcf-irn-question-audio-v1",
            question.source_id,
            question.section_source_id,
            str(question.task_number),
            question.task_type_fr,
            build_question_audio_input(question),
            settings.OPENAI_TTS_MODEL,
            str(settings.OPENAI_TTS_VOICE),
            normalized_audio_format(),
            settings.OPENAI_TTS_INSTRUCTIONS,
        ]
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def build_question_audio_input(question: Question) -> str:
    return question.prompt.strip()


def normalized_audio_format() -> str:
    return (settings.OPENAI_TTS_FORMAT or "mp3").strip().lower()
