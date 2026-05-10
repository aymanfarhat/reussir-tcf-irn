from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

from django.conf import settings
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

from simulations.models import TaskAttempt


class AudioFeedbackResult(BaseModel):
    audio_evidence_used: bool = False
    pronunciation_score_20: float | None = Field(default=None, ge=0, le=20)
    fluency_score_20: float | None = Field(default=None, ge=0, le=20)
    pronunciation_observations: list[str] = Field(default_factory=list)
    fluency_observations: list[str] = Field(default_factory=list)
    transcript_quality_notes: list[str] = Field(default_factory=list)
    suggested_drills: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


SUPPORTED_AUDIO_FORMATS = {
    ".wav": "wav",
    ".mp3": "mp3",
}


def build_audio_feedback(attempt: TaskAttempt) -> AudioFeedbackResult:
    if not attempt.is_oral:
        return AudioFeedbackResult(
            limitations=["Audio feedback is only relevant for oral tasks."]
        )
    if not attempt.audio_file:
        return AudioFeedbackResult(
            transcript_quality_notes=[
                "No audio recording was submitted; oral feedback is based on transcript content only."
            ],
            limitations=["Pronunciation and fluency were not evaluated from audio."],
        )
    if not settings.OPENAI_API_KEY:
        return AudioFeedbackResult(
            transcript_quality_notes=[
                "Audio was saved, but OPENAI_API_KEY is not configured in this environment."
            ],
            limitations=[
                "Local development fallback cannot directly evaluate pronunciation or fluency from audio."
            ],
        )

    audio_path = Path(attempt.audio_file.path)
    audio_format = infer_audio_format(audio_path, attempt.audio_mime_type)
    if audio_format is None:
        return AudioFeedbackResult(
            transcript_quality_notes=[
                f"Unsupported audio format for direct audio grading: {audio_path.suffix or attempt.audio_mime_type}."
            ],
            limitations=[
                "Direct OpenAI audio feedback currently supports wav and mp3 only. "
                "Browser webm recordings are still transcribed and graded from text."
            ],
        )

    return request_audio_feedback(attempt, audio_path, audio_format)


def infer_audio_format(audio_path: Path, mime_type: str = "") -> str | None:
    suffix_format = SUPPORTED_AUDIO_FORMATS.get(audio_path.suffix.lower())
    if suffix_format:
        return suffix_format
    normalized_mime = (mime_type or "").split(";")[0].lower()
    if normalized_mime in {"audio/wav", "audio/x-wav"}:
        return "wav"
    if normalized_mime in {"audio/mpeg", "audio/mp3"}:
        return "mp3"
    return None


def request_audio_feedback(
    attempt: TaskAttempt, audio_path: Path, audio_format: str
) -> AudioFeedbackResult:
    prompt = build_audio_feedback_prompt(attempt)
    encoded_audio = base64.b64encode(audio_path.read_bytes()).decode("utf-8")
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    completion = client.chat.completions.create(
        model=settings.OPENAI_AUDIO_GRADING_MODEL,
        modalities=["text"],
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a TCF IRN oral examiner. Return only valid JSON "
                    "matching the requested keys."
                ),
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": encoded_audio,
                            "format": audio_format,
                        },
                    },
                ],
            },
        ],
        response_format={"type": "json_object"},
    )
    content = completion.choices[0].message.content or "{}"
    return parse_audio_feedback(content)


def build_audio_feedback_prompt(attempt: TaskAttempt) -> str:
    question = attempt.question
    task = question.task_definition
    return "\n".join(
        [
            "Return JSON with keys: audio_evidence_used, pronunciation_score_20, "
            "fluency_score_20, pronunciation_observations, fluency_observations, "
            "transcript_quality_notes, suggested_drills, limitations.",
            "",
            "Evaluate only speech delivery signals from the recording: pronunciation, "
            "intelligibility, rhythm, hesitation, self-correction, and fluency.",
            "Do not re-grade grammar or task completion except when the transcript "
            "appears unreliable because of audio quality.",
            "",
            f"Exam: {task.section.exam.full_name or task.section.exam.name}",
            f"Section: {task.section.name_fr}",
            f"Task {task.task_number}: {task.name_fr}",
            f"Prompt: {question.prompt}",
            "",
            "Transcript already used by the text grader:",
            attempt.transcript_text or "(no transcript)",
        ]
    )


def parse_audio_feedback(content: str | dict[str, Any]) -> AudioFeedbackResult:
    if isinstance(content, str):
        data = json.loads(content)
    else:
        data = content
    try:
        return AudioFeedbackResult.model_validate(data)
    except ValidationError as exc:
        raise ValueError(f"Audio feedback response did not match schema: {exc}") from exc
