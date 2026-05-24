from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.test import TestCase
from django.urls import reverse

from exams.admin import QuestionAdminForm
from exams.models import (
    ExamSection,
    GradingDimension,
    Question,
    TaskDefinition,
    TestDefinition,
)
from exams.services.import_question_bank import import_question_bank


QUESTION_BANK = Path(settings.BASE_DIR).parent / "product_research" / "question_bank.json"


class QuestionBankImportTests(TestCase):
    def test_import_creates_expected_content(self):
        import_question_bank(QUESTION_BANK)

        self.assertEqual(ExamSection.objects.count(), 2)
        self.assertEqual(TaskDefinition.objects.count(), 6)
        self.assertEqual(Question.objects.count(), 60)
        self.assertEqual(GradingDimension.objects.count(), 7)
        self.assertEqual(TestDefinition.objects.count(), 3)
        self.assertEqual(Question.objects.filter(task_number=1).count(), 10)
        self.assertEqual(Question.objects.filter(task_number=6).count(), 10)

    def test_import_is_idempotent_without_replace(self):
        import_question_bank(QUESTION_BANK)
        summary = import_question_bank(QUESTION_BANK)

        self.assertEqual(summary.created, {})
        self.assertEqual(summary.updated, {})
        self.assertEqual(summary.skipped["question"], 60)

    def test_test_definition_sequences_are_seeded(self):
        import_question_bank(QUESTION_BANK)

        full = list(
            TestDefinition.objects.get(source_id="full")
            .steps.order_by("sequence_order")
            .values_list("task_definition__task_number", flat=True)
        )
        oral = list(
            TestDefinition.objects.get(source_id="oral")
            .steps.order_by("sequence_order")
            .values_list("task_definition__task_number", flat=True)
        )
        written = list(
            TestDefinition.objects.get(source_id="written")
            .steps.order_by("sequence_order")
            .values_list("task_definition__task_number", flat=True)
        )

        self.assertEqual(full, [1, 2, 3, 4, 5, 6])
        self.assertEqual(oral, [1, 2, 3])
        self.assertEqual(written, [4, 5, 6])

    def test_admin_content_pages_load(self):
        import_question_bank(QUESTION_BANK)
        admin = User.objects.create_superuser(
            "admin", email="admin@example.com", password="pass12345"
        )
        self.client.force_login(admin)

        urls = [
            reverse("admin:exams_exam_changelist"),
            reverse("admin:exams_examsection_changelist"),
            reverse("admin:exams_taskdefinition_changelist"),
            reverse("admin:exams_question_changelist"),
            reverse("admin:exams_testdefinition_changelist"),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_admin_question_change_page_includes_grader_prompt_preview(self):
        import_question_bank(QUESTION_BANK)
        admin = User.objects.create_superuser(
            "admin", email="admin@example.com", password="pass12345"
        )
        self.client.force_login(admin)
        question = Question.objects.first()

        response = self.client.get(reverse("admin:exams_question_change", args=[question.pk]))

        self.assertContains(response, "Generated grader prompt preview")
        self.assertContains(response, "Format de sortie")

    def test_admin_question_form_blocks_missing_task_specific_content(self):
        import_question_bank(QUESTION_BANK)
        question = Question.objects.filter(section_source_id="expression_ecrite").first()
        data = model_to_dict(question)
        data["expected_response"] = {"structure": []}
        form = QuestionAdminForm(data=data, instance=question)

        self.assertFalse(form.is_valid())
        self.assertIn("expected_response", form.errors)

    def test_admin_question_form_detects_duplicate_prompt(self):
        import_question_bank(QUESTION_BANK)
        question = Question.objects.first()
        data = model_to_dict(question)
        data["source_id"] = "duplicate-question"
        form = QuestionAdminForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("prompt", form.errors)
