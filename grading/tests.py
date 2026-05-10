import json
import tempfile
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from exams.services.import_question_bank import import_question_bank
from grading.models import TaskGrade
from grading.services.audio_feedback import build_audio_feedback
from grading.services.grade_attempt import grade_attempt
from grading.services.prompt_builder import build_grader_markdown
from grading.services.schemas import GradingResult, ImprovedResponseResult
from simulations.models import TaskAttempt
from simulations.services.start_session import start_test_session


QUESTION_BANK = Path(settings.BASE_DIR).parent / "product_research" / "question_bank.json"


@override_settings(OPENAI_API_KEY="")
class GradingServiceTests(TestCase):
    def setUp(self):
        import_question_bank(QUESTION_BANK)
        self.user = User.objects.create_user("learner", password="pass12345")
        self.session = start_test_session(self.user, "written")
        self.attempt = self.session.attempts.order_by("sequence_order").first()
        self.attempt.answer_text = "Salut Nora, Amine a trente ans et il est collegue. Il est calme, drole et aime le cinema et le sport. A bientot."
        self.attempt.word_count_observed = 24
        self.attempt.within_word_limits = False
        self.attempt.save()

    def test_prompt_contains_required_context(self):
        prompt = build_grader_markdown(self.attempt)

        self.assertIn("Grader TCF IRN", prompt)
        self.assertIn(self.attempt.question.source_id, prompt)
        self.assertIn("Production du candidat", prompt)
        self.assertIn("Format de sortie", prompt)

    def test_grading_schema_uses_strict_array_dimensions(self):
        schema = GradingResult.model_json_schema()

        self.assertEqual(schema["properties"]["dimensions"]["type"], "array")
        self.assertIn("dimension_id", schema["$defs"]["DimensionGrade"]["required"])
        self.assertNotIn("minimum", json.dumps(schema))
        self.assertNotIn("maximum", json.dumps(schema))

    def test_improved_response_schema_is_strict(self):
        schema = ImprovedResponseResult.model_json_schema()

        self.assertEqual(
            set(schema["required"]),
            {
                "improved_response_fr",
                "changes_made",
                "reusable_phrases",
                "focus_next_time",
            },
        )
        self.assertFalse(schema["additionalProperties"])

    def test_local_stub_grade_is_saved_without_api_key(self):
        grade = grade_attempt(self.attempt)

        self.assertEqual(grade.status, TaskGrade.STATUS_SUCCEEDED)
        self.assertEqual(grade.parsed_result["question_id"], self.attempt.question.source_id)
        self.assertEqual(grade.improved_response_status, TaskGrade.STATUS_SUCCEEDED)
        self.assertIn("improved_response_fr", grade.improved_response)
        self.attempt.refresh_from_db()
        self.assertEqual(self.attempt.status, TaskAttempt.STATUS_GRADED)

    def test_mocked_audio_feedback_is_saved_for_oral_recording(self):
        oral_session = start_test_session(self.user, "oral")
        oral_attempt = oral_session.attempts.order_by("sequence_order").first()
        oral_attempt.transcript_text = (
            "Bonjour, je me presente avec des details sur mon travail et ma famille."
        )
        oral_attempt.word_count_observed = 12
        oral_attempt.within_word_limits = True
        fake_response = {
            "audio_evidence_used": True,
            "pronunciation_score_20": 13,
            "fluency_score_20": 14,
            "pronunciation_observations": ["Prononciation globalement intelligible."],
            "fluency_observations": ["Debit regulier avec quelques pauses."],
            "transcript_quality_notes": ["Transcript coherent avec l'audio."],
            "suggested_drills": ["Travailler les liaisons courantes."],
            "limitations": [],
        }

        with tempfile.TemporaryDirectory() as media_root, override_settings(
            OPENAI_API_KEY="test-key",
            MEDIA_ROOT=media_root,
        ), patch("grading.services.audio_feedback.OpenAI") as openai_mock, patch(
            "grading.services.grade_attempt.request_openai_grade"
        ) as grade_mock, patch(
            "grading.services.grade_attempt.build_improved_response"
        ) as improved_mock:
            oral_attempt.audio_file.save(
                "speech.wav",
                SimpleUploadedFile("speech.wav", b"fake wav bytes", "audio/wav"),
                save=False,
            )
            oral_attempt.audio_mime_type = "audio/wav"
            oral_attempt.save()
            grade_mock.return_value = (
                build_local_stub_result_for_test(oral_attempt),
                {"provider": "mock"},
                "response-id",
                {},
            )
            improved_mock.return_value = (
                ImprovedResponseResult(
                    improved_response_fr="Bonjour, je me presente clairement.",
                    changes_made=["Phrase clarifiee."],
                    reusable_phrases=["Je me presente"],
                    focus_next_time=["Ajouter un exemple."],
                ),
                {"provider": "mock"},
                "improved-id",
            )
            openai_mock.return_value.chat.completions.create.return_value = SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content=json.dumps(fake_response))
                    )
                ]
            )

            grade = grade_attempt(oral_attempt)

        self.assertEqual(grade.audio_feedback_status, TaskGrade.STATUS_SUCCEEDED)
        self.assertTrue(grade.audio_feedback["audio_evidence_used"])
        self.assertEqual(grade.audio_feedback["fluency_score_20"], 14.0)
        self.assertEqual(grade.improved_response_status, TaskGrade.STATUS_SUCCEEDED)

    def test_webm_audio_feedback_skips_direct_openai_audio_call(self):
        oral_session = start_test_session(self.user, "oral")
        oral_attempt = oral_session.attempts.order_by("sequence_order").first()
        oral_attempt.transcript_text = "Bonjour, je donne mon opinion avec un exemple."

        with tempfile.TemporaryDirectory() as media_root, override_settings(
            OPENAI_API_KEY="test-key",
            MEDIA_ROOT=media_root,
        ), patch("grading.services.audio_feedback.OpenAI") as openai_mock:
            oral_attempt.audio_file.save(
                "speech.webm",
                SimpleUploadedFile("speech.webm", b"fake webm bytes", "audio/webm"),
                save=False,
            )
            oral_attempt.audio_mime_type = "audio/webm"
            oral_attempt.save()

            result = build_audio_feedback(oral_attempt)

        self.assertFalse(result.audio_evidence_used)
        self.assertIn("wav and mp3 only", " ".join(result.limitations))
        openai_mock.assert_not_called()


def build_local_stub_result_for_test(attempt):
    from grading.services.grade_attempt import build_local_stub_result

    return build_local_stub_result(attempt)
