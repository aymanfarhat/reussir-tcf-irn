from __future__ import annotations

from datetime import timedelta

from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone

from simulations.models import TaskAttempt, TestSession


def ensure_session_owner(session: TestSession, user) -> None:
    if session.user_id != user.id:
        raise PermissionDenied("This test session belongs to another user.")


def can_open_attempt(attempt: TaskAttempt) -> bool:
    previous_attempts = TaskAttempt.objects.filter(
        test_session=attempt.test_session,
        sequence_order__lt=attempt.sequence_order,
    )
    return not previous_attempts.exclude(
        status__in=[
            TaskAttempt.STATUS_SUBMITTED,
            TaskAttempt.STATUS_GRADING,
            TaskAttempt.STATUS_GRADED,
            TaskAttempt.STATUS_GRADING_FAILED,
        ]
    ).exists()


def start_attempt_if_needed(attempt: TaskAttempt) -> TaskAttempt:
    if attempt.started_at:
        return attempt

    if not can_open_attempt(attempt):
        raise ValidationError("Previous tasks must be submitted first.")

    now = timezone.now()
    attempt.started_at = now
    duration_seconds = attempt.step.task_definition.duration_seconds or 60
    attempt.deadline_at = now + timedelta(seconds=duration_seconds)
    attempt.status = TaskAttempt.STATUS_IN_PROGRESS
    attempt.save(update_fields=["started_at", "deadline_at", "status", "updated_at"])
    return attempt


def next_attempt(attempt: TaskAttempt) -> TaskAttempt | None:
    return (
        TaskAttempt.objects.filter(
            test_session=attempt.test_session,
            sequence_order__gt=attempt.sequence_order,
        )
        .order_by("sequence_order")
        .first()
    )


def mark_session_completion_if_ready(session: TestSession) -> None:
    incomplete = session.attempts.exclude(
        status__in=[
            TaskAttempt.STATUS_SUBMITTED,
            TaskAttempt.STATUS_GRADING,
            TaskAttempt.STATUS_GRADED,
            TaskAttempt.STATUS_GRADING_FAILED,
        ]
    ).exists()
    if incomplete:
        return

    if session.status != TestSession.STATUS_COMPLETED:
        session.status = TestSession.STATUS_COMPLETED
        session.completed_at = timezone.now()
        session.save(update_fields=["status", "completed_at", "updated_at"])
