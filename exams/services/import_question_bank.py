from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

from django.db import transaction
from django.utils import timezone

from exams.models import (
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


@dataclass
class ImportSummary:
    created: Counter[str] = field(default_factory=Counter)
    updated: Counter[str] = field(default_factory=Counter)
    skipped: Counter[str] = field(default_factory=Counter)
    errors: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, dict[str, int] | list[str]]:
        return {
            "created": dict(self.created),
            "updated": dict(self.updated),
            "skipped": dict(self.skipped),
            "errors": self.errors,
        }


class QuestionBankImportError(RuntimeError):
    pass


def import_question_bank(
    source_path: str | Path,
    *,
    dry_run: bool = False,
    replace_existing: bool = False,
    deactivate_missing: bool = False,
) -> ImportSummary:
    path = Path(source_path)
    payload_text = path.read_text(encoding="utf-8")
    source_hash = hashlib.sha256(payload_text.encode("utf-8")).hexdigest()
    data = json.loads(payload_text)

    validate_question_bank(data)

    summary = ImportSummary()
    import_run = ImportRun.objects.create(
        source_path=str(path),
        source_hash=source_hash,
        source_version=data.get("metadata", {}).get("version", ""),
        dry_run=dry_run,
        replace_existing=replace_existing,
    )

    try:
        if dry_run:
            collect_dry_run_counts(data, summary)
            import_run.status = ImportRun.STATUS_SUCCEEDED
            import_run.finished_at = timezone.now()
            import_run.created_counts = dict(summary.created)
            import_run.updated_counts = dict(summary.updated)
            import_run.skipped_counts = dict(summary.skipped)
            import_run.errors = summary.errors
            import_run.save()
            return summary

        with transaction.atomic():
            exam = import_exam(data, summary, replace_existing)
            import_dimensions(data, summary, replace_existing)
            import_score_bands(data, exam, summary, replace_existing)
            task_by_source_id = import_sections_and_tasks(
                data, exam, summary, replace_existing
            )
            import_questions(data, task_by_source_id, summary, replace_existing)
            import_test_definitions(task_by_source_id, summary, replace_existing)

            if deactivate_missing:
                deactivate_missing_content(data, summary)

        import_run.status = ImportRun.STATUS_SUCCEEDED
    except Exception as exc:
        summary.errors.append(str(exc))
        import_run.status = ImportRun.STATUS_FAILED
        raise
    finally:
        import_run.finished_at = timezone.now()
        import_run.created_counts = dict(summary.created)
        import_run.updated_counts = dict(summary.updated)
        import_run.skipped_counts = dict(summary.skipped)
        import_run.errors = summary.errors
        import_run.save()

    return summary


def validate_question_bank(data: dict[str, Any]) -> None:
    required_top_level = {"metadata", "scoring", "grading_dimensions", "sections", "questions"}
    missing = required_top_level - set(data)
    if missing:
        raise QuestionBankImportError(f"Missing top-level keys: {sorted(missing)}")

    sections = data["sections"]
    questions = data["questions"]
    if len(sections) != 2:
        raise QuestionBankImportError(f"Expected 2 sections, found {len(sections)}")

    task_ids: set[str] = set()
    task_numbers: list[int] = []
    for section in sections:
        for task in section.get("tasks", []):
            task_ids.add(task["id"])
            task_numbers.append(task["task_number"])

    if len(task_ids) != 6:
        raise QuestionBankImportError(f"Expected 6 task definitions, found {len(task_ids)}")
    if len(questions) != 60:
        raise QuestionBankImportError(f"Expected 60 questions, found {len(questions)}")

    per_task = Counter(q["task_number"] for q in questions)
    for number in range(1, 7):
        if per_task[number] != 10:
            raise QuestionBankImportError(
                f"Expected 10 questions for task {number}, found {per_task[number]}"
            )

    for question in questions:
        if question["task_id"] not in task_ids:
            raise QuestionBankImportError(
                f"Question {question['id']} references unknown task {question['task_id']}"
            )

    dimension_ids = {d["id"] for d in data["grading_dimensions"]}
    for section in sections:
        for task in section.get("tasks", []):
            for dimension_id in task.get("rubric_dimensions", []):
                if dimension_id not in dimension_ids:
                    raise QuestionBankImportError(
                        f"Task {task['id']} references unknown dimension {dimension_id}"
                    )


def collect_dry_run_counts(data: dict[str, Any], summary: ImportSummary) -> None:
    summary.created["exam"] = 1
    summary.created["grading_dimension"] = len(data["grading_dimensions"])
    summary.created["level_descriptor"] = sum(
        len(levels) for levels in data.get("generic_level_descriptors", {}).values()
    )
    summary.created["score_band"] = len(data["scoring"]["level_bands"])
    summary.created["exam_section"] = len(data["sections"])
    summary.created["task_definition"] = sum(
        len(section.get("tasks", [])) for section in data["sections"]
    )
    summary.created["question"] = len(data["questions"])
    summary.created["test_definition"] = 3
    summary.created["test_definition_step"] = 12


def import_exam(
    data: dict[str, Any], summary: ImportSummary, replace_existing: bool
) -> Exam:
    metadata = data["metadata"]
    defaults = {
        "name": metadata.get("exam_name", "TCF IRN"),
        "full_name": metadata.get("exam_full_name", ""),
        "issuing_organization": metadata.get("issuing_organization", ""),
        "version": metadata.get("version", ""),
        "valid_from": parse_date(metadata.get("valid_from")),
        "target_level": metadata.get("target_level", ""),
        "scope": metadata.get("scope", ""),
        "language": metadata.get("language", ""),
        "metadata": metadata,
    }
    return upsert(
        Exam,
        {"source_id": "tcf_irn"},
        defaults,
        summary,
        "exam",
        replace_existing,
    )


def import_dimensions(
    data: dict[str, Any], summary: ImportSummary, replace_existing: bool
) -> None:
    for dimension in data["grading_dimensions"]:
        obj = upsert(
            GradingDimension,
            {"source_id": dimension["id"]},
            {
                "name_fr": dimension.get("name_fr", ""),
                "name_en": dimension.get("name_en", ""),
                "description": dimension.get("description", ""),
                "applies_to": dimension.get("applies_to", []),
                "weight_hint": dimension.get("weight_hint", ""),
                "is_active": True,
                "raw_source": dimension,
            },
            summary,
            "grading_dimension",
            replace_existing,
        )
        descriptors = data.get("generic_level_descriptors", {}).get(dimension["id"], {})
        for level, description in descriptors.items():
            upsert(
                LevelDescriptor,
                {"dimension": obj, "level": level},
                {"description": description},
                summary,
                "level_descriptor",
                replace_existing,
            )


def import_score_bands(
    data: dict[str, Any], exam: Exam, summary: ImportSummary, replace_existing: bool
) -> None:
    for band in data["scoring"]["level_bands"]:
        upsert(
            ScoreBand,
            {"exam": exam, "level": band["level"]},
            {
                "score_min": decimal_value(band["score_min"]),
                "score_max": decimal_value(band["score_max"]),
                "midpoint": decimal_value(band.get("midpoint")),
            },
            summary,
            "score_band",
            replace_existing,
        )


def import_sections_and_tasks(
    data: dict[str, Any],
    exam: Exam,
    summary: ImportSummary,
    replace_existing: bool,
) -> dict[str, TaskDefinition]:
    task_by_source_id: dict[str, TaskDefinition] = {}
    for section_order, section in enumerate(data["sections"], start=1):
        section_obj = upsert(
            ExamSection,
            {"source_id": section["id"]},
            {
                "exam": exam,
                "name_fr": section.get("name_fr", ""),
                "name_en": section.get("name_en", ""),
                "sequence_order": section_order,
                "total_duration_minutes": decimal_value(section["total_duration_minutes"]),
                "preparation_time_minutes": decimal_value(
                    section.get("preparation_time_minutes", 0)
                ),
                "format": section.get("format", ""),
                "number_of_tasks": section.get("number_of_tasks", 0),
                "section_notes": section.get("section_notes", []),
                "is_active": True,
                "raw_source": section,
            },
            summary,
            "exam_section",
            replace_existing,
        )

        for task in section.get("tasks", []):
            word_count = task.get("word_count") or {}
            oral_word_count = task.get("expected_response_word_count") or {}
            task_obj = upsert(
                TaskDefinition,
                {"source_id": task["id"]},
                {
                    "section": section_obj,
                    "task_number": task["task_number"],
                    "name_fr": task.get("name_fr", ""),
                    "name_en": task.get("name_en", ""),
                    "format": task.get("format", ""),
                    "objective": task.get("objective", ""),
                    "duration_minutes": decimal_value(task.get("duration_minutes")),
                    "suggested_duration_minutes": decimal_value(
                        task.get("suggested_duration_minutes")
                    ),
                    "preparation_time_minutes": decimal_value(
                        task.get("preparation_time_minutes", 0)
                    ),
                    "word_count_min": word_count.get("min"),
                    "word_count_max": word_count.get("max"),
                    "word_count_target": word_count.get("target"),
                    "expected_response_word_count_min": oral_word_count.get("min"),
                    "expected_response_word_count_ideal": oral_word_count.get("ideal"),
                    "expected_response_word_count_max": oral_word_count.get("max"),
                    "expected_structure": task.get("expected_structure", []),
                    "required_elements": task.get("required_elements", []),
                    "skills_assessed": task.get("skills_assessed", []),
                    "strategy_tips": task.get("strategy_tips", []),
                    "common_pitfalls": task.get("common_pitfalls", []),
                    "common_topics": task.get("common_topics", []),
                    "examiner_behavior": task.get("examiner_behavior", ""),
                    "rubric_dimensions": task.get("rubric_dimensions", []),
                    "task_specific_rubric": task.get("task_specific_rubric", {}),
                    "is_active": True,
                    "raw_source": task,
                },
                summary,
                "task_definition",
                replace_existing,
            )
            task_by_source_id[task["id"]] = task_obj

    return task_by_source_id


def import_questions(
    data: dict[str, Any],
    task_by_source_id: dict[str, TaskDefinition],
    summary: ImportSummary,
    replace_existing: bool,
) -> None:
    for question in data["questions"]:
        task = task_by_source_id[question["task_id"]]
        upsert(
            Question,
            {"source_id": question["id"]},
            {
                "task_definition": task,
                "section_source_id": question["section"],
                "task_number": question["task_number"],
                "task_type_fr": question.get("task_type_fr", ""),
                "prompt": question.get("question", ""),
                "themes": question.get("themes", []),
                "timing": question.get("timing", {}),
                "addressee": question.get("addressee", ""),
                "register": question.get("register", ""),
                "channel": question.get("channel", ""),
                "examiner_role_fr": question.get("examiner_role_fr", ""),
                "expected_response": question.get("expected_response", {}),
                "evaluation_focus": question.get("evaluation_focus", []),
                "is_active": True,
                "raw_source": question,
            },
            summary,
            "question",
            replace_existing,
        )


def import_test_definitions(
    task_by_source_id: dict[str, TaskDefinition],
    summary: ImportSummary,
    replace_existing: bool,
) -> None:
    definitions = {
        "full": {
            "name": "Full TCF IRN simulation",
            "mode": TestDefinition.MODE_FULL,
            "description": "Oral tasks 1-3 followed by written tasks 4-6.",
            "tasks": [
                "oral_task_1",
                "oral_task_2",
                "oral_task_3",
                "written_task_1",
                "written_task_2",
                "written_task_3",
            ],
        },
        "oral": {
            "name": "Oral expression practice",
            "mode": TestDefinition.MODE_ORAL,
            "description": "Oral tasks 1-3.",
            "tasks": ["oral_task_1", "oral_task_2", "oral_task_3"],
        },
        "written": {
            "name": "Written expression practice",
            "mode": TestDefinition.MODE_WRITTEN,
            "description": "Written tasks 4-6.",
            "tasks": ["written_task_1", "written_task_2", "written_task_3"],
        },
    }

    for source_id, definition in definitions.items():
        test_definition = upsert(
            TestDefinition,
            {"source_id": source_id},
            {
                "name": definition["name"],
                "mode": definition["mode"],
                "description": definition["description"],
                "is_active": True,
            },
            summary,
            "test_definition",
            replace_existing,
        )
        for order, task_id in enumerate(definition["tasks"], start=1):
            upsert(
                TestDefinitionStep,
                {"test_definition": test_definition, "sequence_order": order},
                {"task_definition": task_by_source_id[task_id]},
                summary,
                "test_definition_step",
                replace_existing,
            )


def deactivate_missing_content(data: dict[str, Any], summary: ImportSummary) -> None:
    task_ids = {task["id"] for section in data["sections"] for task in section.get("tasks", [])}
    question_ids = {question["id"] for question in data["questions"]}
    section_ids = {section["id"] for section in data["sections"]}
    dimension_ids = {dimension["id"] for dimension in data["grading_dimensions"]}

    summary.updated["task_definition"] += TaskDefinition.objects.exclude(
        source_id__in=task_ids
    ).update(is_active=False)
    summary.updated["question"] += Question.objects.exclude(
        source_id__in=question_ids
    ).update(is_active=False)
    summary.updated["exam_section"] += ExamSection.objects.exclude(
        source_id__in=section_ids
    ).update(is_active=False)
    summary.updated["grading_dimension"] += GradingDimension.objects.exclude(
        source_id__in=dimension_ids
    ).update(is_active=False)


def upsert(
    model_class,
    lookup: dict[str, Any],
    defaults: dict[str, Any],
    summary: ImportSummary,
    counter_name: str,
    replace_existing: bool,
):
    obj = model_class.objects.filter(**lookup).first()
    if obj is None:
        obj = model_class.objects.create(**lookup, **defaults)
        summary.created[counter_name] += 1
        return obj

    if not replace_existing:
        summary.skipped[counter_name] += 1
        return obj

    for field_name, value in defaults.items():
        setattr(obj, field_name, value)
    obj.save()
    summary.updated[counter_name] += 1
    return obj


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def decimal_value(value: Any) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


def question_counts_by_task() -> dict[int, int]:
    counts = defaultdict(int)
    for row in Question.objects.filter(is_active=True).values("task_number"):
        counts[row["task_number"]] += 1
    return dict(counts)
