from difflib import SequenceMatcher
import re

from django.contrib import admin
from django import forms
from django.utils.html import format_html

from grading.services.prompt_builder import build_grader_preview_for_question

from .models import (
    Exam,
    ExamSection,
    GradingDimension,
    ImportRun,
    LevelDescriptor,
    Question,
    ScoreBand,
    TaskDefinition,
    TestDefinition,
    TestDefinitionStep,
)


def normalize_prompt(prompt: str) -> str:
    return re.sub(r"\W+", " ", prompt.lower()).strip()


class QuestionAdminForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        task = cleaned.get("task_definition")
        prompt = cleaned.get("prompt") or ""
        expected = cleaned.get("expected_response") or {}
        evaluation_focus = cleaned.get("evaluation_focus") or []

        if task:
            if cleaned.get("section_source_id") and cleaned["section_source_id"] != task.section.source_id:
                self.add_error(
                    "section_source_id",
                    "Section must match the selected task definition.",
                )
            if cleaned.get("task_number") and cleaned["task_number"] != task.task_number:
                self.add_error(
                    "task_number",
                    "Task number must match the selected task definition.",
                )

            required_expected_fields = [
                "structure",
                "reference_answer",
                "key_elements_to_cover",
                "key_vocabulary",
                "key_grammar",
            ]
            missing_fields = [
                field for field in required_expected_fields if not expected.get(field)
            ]
            if missing_fields:
                self.add_error(
                    "expected_response",
                    "Missing expected response fields: " + ", ".join(missing_fields),
                )

            if task.is_written and (
                task.word_count_min is None or task.word_count_max is None
            ):
                self.add_error(
                    "task_definition",
                    "Written tasks must define strict minimum and maximum word counts.",
                )
            if task.is_oral:
                timing = cleaned.get("timing") or {}
                if not task.duration_minutes and not timing.get("duration_minutes"):
                    self.add_error(
                        "timing",
                        "Oral questions must define a duration through the task or timing metadata.",
                    )
                if not evaluation_focus:
                    self.add_error(
                        "evaluation_focus",
                        "Oral questions need evaluation focus notes for grader guidance.",
                    )

        normalized = normalize_prompt(prompt)
        if normalized:
            existing_questions = Question.objects.exclude(pk=self.instance.pk)
            for question in existing_questions.only("source_id", "prompt"):
                existing_normalized = normalize_prompt(question.prompt)
                if not existing_normalized:
                    continue
                similarity = SequenceMatcher(None, normalized, existing_normalized).ratio()
                if normalized == existing_normalized or similarity >= 0.94:
                    self.add_error(
                        "prompt",
                        f"Possible duplicate of {question.source_id} ({similarity:.0%} similar).",
                    )
                    break

        return cleaned


class TestDefinitionStepInline(admin.TabularInline):
    model = TestDefinitionStep
    extra = 0
    autocomplete_fields = ["task_definition"]


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ["name", "version", "target_level", "language", "updated_at"]
    search_fields = ["source_id", "name", "full_name", "issuing_organization"]


@admin.register(ExamSection)
class ExamSectionAdmin(admin.ModelAdmin):
    list_display = [
        "name_fr",
        "source_id",
        "sequence_order",
        "total_duration_minutes",
        "is_active",
    ]
    list_filter = ["is_active", "exam"]
    search_fields = ["source_id", "name_fr", "name_en"]


@admin.register(GradingDimension)
class GradingDimensionAdmin(admin.ModelAdmin):
    list_display = ["source_id", "name_fr", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["source_id", "name_fr", "name_en", "description"]


@admin.register(LevelDescriptor)
class LevelDescriptorAdmin(admin.ModelAdmin):
    list_display = ["dimension", "level"]
    list_filter = ["level", "dimension"]
    search_fields = ["dimension__source_id", "description"]


@admin.register(ScoreBand)
class ScoreBandAdmin(admin.ModelAdmin):
    list_display = ["exam", "level", "score_min", "score_max", "midpoint"]
    list_filter = ["exam", "level"]


@admin.register(TaskDefinition)
class TaskDefinitionAdmin(admin.ModelAdmin):
    list_display = [
        "task_number",
        "name_fr",
        "section",
        "duration_minutes",
        "suggested_duration_minutes",
        "word_count_min",
        "word_count_max",
        "is_active",
    ]
    list_filter = ["section", "task_number", "is_active"]
    search_fields = ["source_id", "name_fr", "name_en", "objective", "format"]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    form = QuestionAdminForm
    list_display = [
        "source_id",
        "task_number",
        "task_type_fr",
        "section_source_id",
        "is_active",
    ]
    list_filter = ["section_source_id", "task_number", "is_active"]
    search_fields = ["source_id", "prompt", "task_type_fr"]
    autocomplete_fields = ["task_definition"]
    readonly_fields = ["grader_prompt_preview", "raw_source"]

    def save_model(self, request, obj, form, change):
        if obj.task_definition_id:
            obj.section_source_id = obj.task_definition.section.source_id
            obj.task_number = obj.task_definition.task_number
            if not obj.task_type_fr:
                obj.task_type_fr = obj.task_definition.name_fr
        super().save_model(request, obj, form, change)

    @admin.display(description="Generated grader prompt preview")
    def grader_prompt_preview(self, obj):
        if not obj or not obj.pk:
            return "Save the question first to preview the generated grader prompt."
        preview = build_grader_preview_for_question(obj)
        return format_html(
            '<pre style="white-space: pre-wrap; max-height: 520px; overflow: auto; '
            'border: 1px solid #cbd5e1; border-radius: 6px; padding: 12px; '
            'background: #f8fafc;">{}</pre>',
            preview,
        )


@admin.register(TestDefinition)
class TestDefinitionAdmin(admin.ModelAdmin):
    list_display = ["source_id", "name", "mode", "is_active"]
    list_filter = ["mode", "is_active"]
    search_fields = ["source_id", "name", "description"]
    inlines = [TestDefinitionStepInline]


@admin.register(TestDefinitionStep)
class TestDefinitionStepAdmin(admin.ModelAdmin):
    list_display = ["test_definition", "sequence_order", "task_definition"]
    list_filter = ["test_definition"]
    search_fields = [
        "test_definition__source_id",
        "test_definition__name",
        "task_definition__source_id",
        "task_definition__name_fr",
    ]
    autocomplete_fields = ["test_definition", "task_definition"]


@admin.register(ImportRun)
class ImportRunAdmin(admin.ModelAdmin):
    list_display = [
        "source_path",
        "source_version",
        "status",
        "dry_run",
        "replace_existing",
        "started_at",
        "finished_at",
    ]
    list_filter = ["status", "dry_run", "replace_existing"]
    search_fields = ["source_path", "source_hash", "source_version"]
    readonly_fields = [
        "source_hash",
        "created_counts",
        "updated_counts",
        "skipped_counts",
        "errors",
    ]
