from __future__ import annotations

import time
from decimal import Decimal

from django.conf import settings
from openai import OpenAI
from openai import OpenAIError

from grading.models import TaskGrade
from grading.services.audio_feedback import build_audio_feedback
from grading.services.improved_response import build_improved_response
from grading.services.prompt_builder import PROMPT_VERSION, build_grader_markdown
from grading.services.schemas import (
    DimensionGrade,
    GradingResult,
    VocabularyFeedback,
)
from simulations.models import TaskAttempt


def grade_attempt(attempt: TaskAttempt) -> TaskGrade:
    prompt = build_grader_markdown(attempt)
    candidate = attempt.candidate_text
    grade, _ = TaskGrade.objects.update_or_create(
        task_attempt=attempt,
        defaults={
            "status": TaskGrade.STATUS_RUNNING,
            "prompt_version": PROMPT_VERSION,
            "prompt_markdown": prompt,
            "candidate_input": candidate,
            "model": settings.OPENAI_GRADING_MODEL,
            "error_message": "",
            "audio_feedback": {},
            "audio_feedback_status": "",
            "audio_feedback_error": "",
            "improved_response": {},
            "improved_response_status": "",
            "improved_response_error": "",
            "improved_response_model": settings.OPENAI_IMPROVEMENT_MODEL,
            "improved_response_id": "",
        },
    )
    attempt.status = TaskAttempt.STATUS_GRADING
    attempt.save(update_fields=["status", "updated_at"])

    started = time.monotonic()
    try:
        if not settings.OPENAI_API_KEY:
            result = build_local_stub_result(attempt)
            raw_response = {"provider": "local_stub", "reason": "OPENAI_API_KEY missing"}
            response_id = ""
            token_usage = {}
        else:
            result, raw_response, response_id, token_usage = request_openai_grade(prompt)

        parsed = result.model_dump()
        audio_feedback = {}
        audio_feedback_status = ""
        audio_feedback_error = ""
        improved_response = {}
        improved_response_status = ""
        improved_response_error = ""
        improved_response_id = ""
        try:
            improved_result, _improved_raw, improved_response_id = build_improved_response(
                attempt, result
            )
            improved_response = improved_result.model_dump()
            improved_response_status = TaskGrade.STATUS_SUCCEEDED
            parsed["improved_response"] = improved_result.model_dump()
        except (OpenAIError, RuntimeError, ValueError) as exc:
            improved_response_status = TaskGrade.STATUS_FAILED
            improved_response_error = str(exc)

        if attempt.is_oral:
            try:
                audio_feedback_result = build_audio_feedback(attempt)
                audio_feedback = audio_feedback_result.model_dump()
                audio_feedback_status = TaskGrade.STATUS_SUCCEEDED
                parsed["audio_feedback"] = audio_feedback
            except (OpenAIError, RuntimeError, ValueError) as exc:
                audio_feedback_status = TaskGrade.STATUS_FAILED
                audio_feedback_error = str(exc)

        grade.status = TaskGrade.STATUS_SUCCEEDED
        grade.parsed_result = parsed
        grade.audio_feedback = audio_feedback
        grade.audio_feedback_status = audio_feedback_status
        grade.audio_feedback_error = audio_feedback_error
        grade.improved_response = improved_response
        grade.improved_response_status = improved_response_status
        grade.improved_response_error = improved_response_error
        grade.improved_response_model = settings.OPENAI_IMPROVEMENT_MODEL
        grade.improved_response_id = improved_response_id
        grade.raw_response = raw_response
        grade.response_id = response_id
        grade.token_usage = token_usage
        grade.overall_score_20 = Decimal(str(result.overall_score_20))
        grade.estimated_cefr_level = result.estimated_cefr_level
        grade.automatic_failure = result.automatic_failure
        grade.automatic_failure_reasons = result.automatic_failure_reasons
        grade.duration_ms = int((time.monotonic() - started) * 1000)
        grade.error_message = ""
        grade.save()

        attempt.status = TaskAttempt.STATUS_GRADED
        attempt.save(update_fields=["status", "updated_at"])
        return grade
    except (OpenAIError, RuntimeError, ValueError) as exc:
        grade.status = TaskGrade.STATUS_FAILED
        grade.duration_ms = int((time.monotonic() - started) * 1000)
        grade.error_message = str(exc)
        grade.save(update_fields=["status", "duration_ms", "error_message", "updated_at"])
        attempt.status = TaskAttempt.STATUS_GRADING_FAILED
        attempt.save(update_fields=["status", "updated_at"])
        return grade


def request_openai_grade(prompt: str):
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.responses.parse(
        model=settings.OPENAI_GRADING_MODEL,
        instructions=(
            "You grade TCF IRN French exam practice answers. "
            "Return only the requested structured output."
        ),
        input=prompt,
        text_format=GradingResult,
    )
    parsed = getattr(response, "output_parsed", None)
    if parsed is None:
        for output in response.output:
            if output.type != "message":
                continue
            for item in output.content:
                item_parsed = getattr(item, "parsed", None)
                if item_parsed is not None:
                    parsed = item_parsed
                    break
    if parsed is None:
        raise RuntimeError("The model response could not be parsed.")

    raw_response = response.model_dump(mode="json")
    response_id = getattr(response, "id", "") or ""
    usage = getattr(response, "usage", None)
    token_usage = usage.model_dump(mode="json") if usage else {}
    return parsed, raw_response, response_id, token_usage


def build_local_stub_result(attempt: TaskAttempt) -> GradingResult:
    text = attempt.candidate_text.strip()
    question = attempt.question
    task = question.task_definition
    expected = question.expected_response
    word_count = attempt.word_count_observed or len(text.split())
    within_word_limits = (
        bool(attempt.within_word_limits)
        if attempt.within_word_limits is not None
        else bool(text)
    )
    automatic_failure = not text
    score = 0 if automatic_failure else (12 if within_word_limits else 8)
    level = "A1" if automatic_failure else ("B2" if score >= 10 else "B1")
    covered = expected.get("key_elements_to_cover", [])[:2] if text else []
    missing = expected.get("key_elements_to_cover", [])[len(covered) :]
    dimensions = [
        DimensionGrade(
            dimension_id=dimension_id,
            score_20=float(score),
            level=level,
            justification=(
                "Evaluation locale de developpement: la production est presente "
                "et respecte globalement les contraintes visibles."
                if text
                else "Aucune production exploitable."
            ),
            evidence=[text[:160]] if text else [],
        )
        for dimension_id in task.rubric_dimensions
    ]
    return GradingResult(
        question_id=question.source_id,
        overall_score_20=float(score),
        estimated_cefr_level=level,
        word_count_observed=word_count,
        within_word_limits=within_word_limits,
        automatic_failure=automatic_failure,
        automatic_failure_reasons=["Production vide"] if automatic_failure else [],
        dimensions=dimensions,
        elements_covered=covered,
        elements_missing=missing,
        structure_followed=bool(text),
        structure_comments=(
            "Structure plausible pour un mode local de developpement."
            if text
            else "Aucune structure observable."
        ),
        vocabulary=VocabularyFeedback(
            expected_used=[],
            expected_missing=expected.get("key_vocabulary", []),
            notable_extras=[],
        ),
        grammar_observations=[
            "Mode local: observation grammaticale detaillee disponible avec OpenAI."
        ],
        errors=[],
        strengths=["Reponse soumise dans le simulateur."] if text else [],
        improvement_advice_fr=[
            "Activez OPENAI_API_KEY pour obtenir une correction detaillee par modele.",
            "Verifiez que chaque element demande dans le sujet est traite explicitement.",
        ],
    )
