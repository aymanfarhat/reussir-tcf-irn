from django.contrib import admin

from .models import TaskGrade


@admin.register(TaskGrade)
class TaskGradeAdmin(admin.ModelAdmin):
    list_display = [
        "task_attempt",
        "status",
        "model",
        "overall_score_20",
        "estimated_cefr_level",
        "automatic_failure",
        "updated_at",
    ]
    list_filter = ["status", "estimated_cefr_level", "automatic_failure", "model"]
    search_fields = [
        "task_attempt__uuid",
        "task_attempt__test_session__uuid",
        "task_attempt__test_session__user__username",
        "prompt_markdown",
        "candidate_input",
        "error_message",
    ]
    readonly_fields = [
        "prompt_markdown",
        "raw_response",
        "parsed_result",
        "audio_feedback",
        "audio_feedback_error",
        "improved_response",
        "improved_response_error",
        "token_usage",
        "created_at",
        "updated_at",
    ]
    autocomplete_fields = ["task_attempt"]
