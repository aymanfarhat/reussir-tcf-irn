from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models


class TestSession(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_SUBMITTED = "submitted"
    STATUS_GRADING = "grading"
    STATUS_COMPLETED = "completed"
    STATUS_ABANDONED = "abandoned"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_IN_PROGRESS, "In progress"),
        (STATUS_SUBMITTED, "Submitted"),
        (STATUS_GRADING, "Grading"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_ABANDONED, "Abandoned"),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="test_sessions"
    )
    test_definition = models.ForeignKey(
        "exams.TestDefinition", on_delete=models.PROTECT, related_name="sessions"
    )
    mode = models.CharField(max_length=20)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    current_step_order = models.PositiveSmallIntegerField(default=1)
    random_seed = models.PositiveIntegerField(null=True, blank=True)
    oral_score = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True
    )
    oral_level = models.CharField(max_length=10, blank=True)
    written_score = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True
    )
    written_level = models.CharField(max_length=10, blank=True)
    summary = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user} {self.mode} {self.uuid}"


class TaskAttempt(models.Model):
    STATUS_NOT_STARTED = "not_started"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_SUBMITTED = "submitted"
    STATUS_GRADING = "grading"
    STATUS_GRADED = "graded"
    STATUS_GRADING_FAILED = "grading_failed"
    STATUS_CHOICES = [
        (STATUS_NOT_STARTED, "Not started"),
        (STATUS_IN_PROGRESS, "In progress"),
        (STATUS_SUBMITTED, "Submitted"),
        (STATUS_GRADING, "Grading"),
        (STATUS_GRADED, "Graded"),
        (STATUS_GRADING_FAILED, "Grading failed"),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    test_session = models.ForeignKey(
        TestSession, on_delete=models.CASCADE, related_name="attempts"
    )
    step = models.ForeignKey(
        "exams.TestDefinitionStep", on_delete=models.PROTECT, related_name="attempts"
    )
    question = models.ForeignKey(
        "exams.Question", on_delete=models.PROTECT, related_name="attempts"
    )
    task_definition_snapshot = models.JSONField(default=dict, blank=True)
    question_snapshot = models.JSONField(default=dict, blank=True)
    sequence_order = models.PositiveSmallIntegerField()
    status = models.CharField(
        max_length=24, choices=STATUS_CHOICES, default=STATUS_NOT_STARTED
    )
    started_at = models.DateTimeField(null=True, blank=True)
    deadline_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    submitted_late = models.BooleanField(default=False)
    answer_text = models.TextField(blank=True)
    audio_file = models.FileField(upload_to="oral_recordings/%Y/%m/%d/", blank=True)
    audio_mime_type = models.CharField(max_length=120, blank=True)
    transcript_text = models.TextField(blank=True)
    manual_transcript = models.BooleanField(default=False)
    word_count_observed = models.PositiveSmallIntegerField(null=True, blank=True)
    within_word_limits = models.BooleanField(null=True, blank=True)
    client_events = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["test_session", "sequence_order"]
        constraints = [
            models.UniqueConstraint(
                fields=["test_session", "sequence_order"],
                name="unique_attempt_order_per_session",
            )
        ]

    def __str__(self) -> str:
        return f"{self.test_session.uuid} task {self.sequence_order}"

    @property
    def is_written(self) -> bool:
        return self.question.section_source_id == "expression_ecrite"

    @property
    def is_oral(self) -> bool:
        return self.question.section_source_id == "expression_orale"

    @property
    def candidate_text(self) -> str:
        return self.transcript_text if self.is_oral else self.answer_text
