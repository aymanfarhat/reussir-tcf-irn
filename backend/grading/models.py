from __future__ import annotations

from django.db import models


class TaskGrade(models.Model):
    STATUS_PENDING = "pending"
    STATUS_RUNNING = "running"
    STATUS_SUCCEEDED = "succeeded"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_RUNNING, "Running"),
        (STATUS_SUCCEEDED, "Succeeded"),
        (STATUS_FAILED, "Failed"),
    ]

    task_attempt = models.OneToOneField(
        "simulations.TaskAttempt", on_delete=models.CASCADE, related_name="grade"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    prompt_version = models.CharField(max_length=40, blank=True)
    prompt_markdown = models.TextField(blank=True)
    candidate_input = models.TextField(blank=True)
    model = models.CharField(max_length=120, blank=True)
    response_id = models.CharField(max_length=120, blank=True)
    raw_response = models.JSONField(default=dict, blank=True)
    parsed_result = models.JSONField(default=dict, blank=True)
    audio_feedback = models.JSONField(default=dict, blank=True)
    audio_feedback_status = models.CharField(max_length=20, blank=True)
    audio_feedback_error = models.TextField(blank=True)
    improved_response = models.JSONField(default=dict, blank=True)
    improved_response_status = models.CharField(max_length=20, blank=True)
    improved_response_error = models.TextField(blank=True)
    improved_response_model = models.CharField(max_length=120, blank=True)
    improved_response_id = models.CharField(max_length=120, blank=True)
    overall_score_20 = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True
    )
    estimated_cefr_level = models.CharField(max_length=10, blank=True)
    automatic_failure = models.BooleanField(default=False)
    automatic_failure_reasons = models.JSONField(default=list, blank=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)
    token_usage = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Grade for {self.task_attempt_id}: {self.status}"
