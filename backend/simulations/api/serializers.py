from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.contrib.auth.models import User
from rest_framework import serializers

from exams.models import Question, TaskDefinition, TestDefinition
from grading.models import TaskGrade
from simulations.models import TaskAttempt, TestSession


class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    def validate_username(self, value: str) -> str:
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "The two password fields did not match."})
        return attrs

    def create(self, validated_data: dict[str, Any]) -> User:
        return User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
        )


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class TestStartSerializer(serializers.Serializer):
    mode = serializers.ChoiceField(choices=[choice[0] for choice in TestDefinition.MODE_CHOICES])


class PracticeStartSerializer(serializers.Serializer):
    task_number = serializers.IntegerField(required=False, allow_null=True, min_value=1, max_value=6)
    theme = serializers.CharField(required=False, allow_blank=True, default="")


class WrittenSubmitSerializer(serializers.Serializer):
    answer_text = serializers.CharField(required=False, allow_blank=True, default="")


class OralSubmitSerializer(serializers.Serializer):
    transcript_text = serializers.CharField(required=False, allow_blank=True, default="")
    audio_file = serializers.FileField(required=False, allow_empty_file=False)


def decimal_to_number(value: Decimal | None) -> float | None:
    return float(value) if value is not None else None


def task_definition_payload(task: TaskDefinition) -> dict[str, Any]:
    return {
        "id": task.id,
        "source_id": task.source_id,
        "task_number": task.task_number,
        "name_fr": task.name_fr,
        "name_en": task.name_en,
        "duration_minutes": decimal_to_number(task.duration_minutes),
        "suggested_duration_minutes": decimal_to_number(task.suggested_duration_minutes),
        "duration_seconds": task.duration_seconds,
        "word_count_min": task.word_count_min,
        "word_count_max": task.word_count_max,
        "word_count_target": task.word_count_target,
        "expected_response_word_count_min": task.expected_response_word_count_min,
        "expected_response_word_count_ideal": task.expected_response_word_count_ideal,
        "expected_response_word_count_max": task.expected_response_word_count_max,
        "expected_structure": task.expected_structure,
        "required_elements": task.required_elements,
        "strategy_tips": task.strategy_tips,
        "common_pitfalls": task.common_pitfalls,
        "rubric_dimensions": task.rubric_dimensions,
        "is_written": task.is_written,
        "is_oral": task.is_oral,
    }


def question_payload(question: Question) -> dict[str, Any]:
    return {
        "id": question.id,
        "source_id": question.source_id,
        "section_source_id": question.section_source_id,
        "task_number": question.task_number,
        "task_type_fr": question.task_type_fr,
        "prompt": question.prompt,
        "themes": question.themes,
        "timing": question.timing,
        "addressee": question.addressee,
        "register": question.register,
        "channel": question.channel,
        "examiner_role_fr": question.examiner_role_fr,
        "expected_response": question.expected_response,
        "evaluation_focus": question.evaluation_focus,
        "task_definition": task_definition_payload(question.task_definition),
    }


def grade_payload(grade: TaskGrade | None) -> dict[str, Any] | None:
    if grade is None:
        return None
    return {
        "id": grade.id,
        "status": grade.status,
        "prompt_version": grade.prompt_version,
        "model": grade.model,
        "response_id": grade.response_id,
        "parsed_result": grade.parsed_result,
        "audio_feedback": grade.audio_feedback,
        "audio_feedback_status": grade.audio_feedback_status,
        "audio_feedback_error": grade.audio_feedback_error,
        "improved_response": grade.improved_response,
        "improved_response_status": grade.improved_response_status,
        "improved_response_error": grade.improved_response_error,
        "improved_response_model": grade.improved_response_model,
        "overall_score_20": decimal_to_number(grade.overall_score_20),
        "estimated_cefr_level": grade.estimated_cefr_level,
        "automatic_failure": grade.automatic_failure,
        "automatic_failure_reasons": grade.automatic_failure_reasons,
        "duration_ms": grade.duration_ms,
        "token_usage": grade.token_usage,
        "error_message": grade.error_message,
        "created_at": grade.created_at,
        "updated_at": grade.updated_at,
    }


def safe_grade(attempt: TaskAttempt) -> TaskGrade | None:
    try:
        return attempt.grade
    except TaskGrade.DoesNotExist:
        return None


def attempt_payload(attempt: TaskAttempt, *, include_question: bool = True) -> dict[str, Any]:
    return {
        "id": attempt.id,
        "uuid": str(attempt.uuid),
        "test_session_uuid": str(attempt.test_session.uuid),
        "sequence_order": attempt.sequence_order,
        "status": attempt.status,
        "started_at": attempt.started_at,
        "deadline_at": attempt.deadline_at,
        "submitted_at": attempt.submitted_at,
        "submitted_late": attempt.submitted_late,
        "answer_text": attempt.answer_text,
        "transcript_text": attempt.transcript_text,
        "manual_transcript": attempt.manual_transcript,
        "audio_file_url": attempt.audio_file.url if attempt.audio_file else "",
        "audio_mime_type": attempt.audio_mime_type,
        "word_count_observed": attempt.word_count_observed,
        "within_word_limits": attempt.within_word_limits,
        "is_written": attempt.is_written,
        "is_oral": attempt.is_oral,
        "candidate_text": attempt.candidate_text,
        "question": question_payload(attempt.question) if include_question else None,
        "grade": grade_payload(safe_grade(attempt)),
    }


def session_payload(session: TestSession, *, include_attempts: bool = True) -> dict[str, Any]:
    data = {
        "id": session.id,
        "uuid": str(session.uuid),
        "mode": session.mode,
        "status": session.status,
        "started_at": session.started_at,
        "completed_at": session.completed_at,
        "current_step_order": session.current_step_order,
        "random_seed": session.random_seed,
        "oral_score": decimal_to_number(session.oral_score),
        "oral_level": session.oral_level,
        "written_score": decimal_to_number(session.written_score),
        "written_level": session.written_level,
        "summary": session.summary,
        "metadata": session.metadata,
        "test_definition": {
            "id": session.test_definition.id,
            "source_id": session.test_definition.source_id,
            "name": session.test_definition.name,
            "mode": session.test_definition.mode,
            "description": session.test_definition.description,
        },
        "created_at": session.created_at,
        "updated_at": session.updated_at,
    }
    if include_attempts:
        attempts = session.attempts.select_related(
            "question",
            "question__task_definition",
            "question__task_definition__section",
            "grade",
        ).order_by("sequence_order")
        data["attempts"] = [attempt_payload(attempt, include_question=True) for attempt in attempts]
    return data


def test_definition_payload(definition: TestDefinition) -> dict[str, Any]:
    return {
        "id": definition.id,
        "source_id": definition.source_id,
        "name": definition.name,
        "mode": definition.mode,
        "description": definition.description,
    }
