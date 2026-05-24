from django.contrib import admin

from .models import TaskAttempt, TestSession


class TaskAttemptInline(admin.TabularInline):
    model = TaskAttempt
    extra = 0
    fields = ["sequence_order", "question", "status", "submitted_at", "submitted_late"]
    readonly_fields = fields
    can_delete = False


@admin.register(TestSession)
class TestSessionAdmin(admin.ModelAdmin):
    list_display = [
        "uuid",
        "user",
        "mode",
        "status",
        "oral_score",
        "oral_level",
        "written_score",
        "written_level",
        "created_at",
    ]
    list_filter = ["mode", "status", "oral_level", "written_level", "created_at"]
    search_fields = ["uuid", "user__username", "user__email"]
    readonly_fields = ["uuid", "summary", "metadata", "created_at", "updated_at"]
    inlines = [TaskAttemptInline]


@admin.register(TaskAttempt)
class TaskAttemptAdmin(admin.ModelAdmin):
    list_display = [
        "uuid",
        "test_session",
        "sequence_order",
        "question",
        "status",
        "word_count_observed",
        "within_word_limits",
        "submitted_late",
    ]
    list_filter = [
        "status",
        "sequence_order",
        "submitted_late",
        "within_word_limits",
        "question__section_source_id",
        "question__task_number",
    ]
    search_fields = [
        "uuid",
        "test_session__uuid",
        "test_session__user__username",
        "question__source_id",
        "question__prompt",
        "answer_text",
        "transcript_text",
    ]
    readonly_fields = [
        "uuid",
        "task_definition_snapshot",
        "question_snapshot",
        "client_events",
        "metadata",
        "created_at",
        "updated_at",
    ]
    autocomplete_fields = ["test_session", "step", "question"]
