import tempfile
from decimal import Decimal
from html import unescape
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from exams.services.import_question_bank import import_question_bank
from grading.models import TaskGrade
from simulations.models import TaskAttempt, TestSession
from simulations.services.start_session import start_practice_session, start_test_session
from simulations.services.word_count import count_words


QUESTION_BANK = Path(settings.BASE_DIR).parent / "product_research" / "question_bank.json"


class WordCountTests(TestCase):
    def test_counts_french_words_with_apostrophes(self):
        self.assertEqual(count_words("J'aime le francais aujourd'hui."), 4)


@override_settings(OPENAI_API_KEY="")
class SimulationFlowTests(TestCase):
    def setUp(self):
        import_question_bank(QUESTION_BANK)
        self.user = User.objects.create_user("learner", password="pass12345")

    def test_start_written_session_creates_ordered_attempts(self):
        session = start_test_session(self.user, "written")
        numbers = list(
            session.attempts.order_by("sequence_order").values_list(
                "question__task_number", flat=True
            )
        )

        self.assertEqual(numbers, [4, 5, 6])

    def test_start_practice_session_filters_by_task_and_theme(self):
        session = start_practice_session(self.user, task_number=4, theme="travail")
        attempt = session.attempts.get()

        self.assertEqual(session.mode, "practice")
        self.assertEqual(attempt.question.task_number, 4)
        self.assertIn("travail", attempt.question.themes)

    def test_practice_page_starts_single_task(self):
        self.client.login(username="learner", password="pass12345")

        response = self.client.post(
            reverse("practice_start"),
            {"task_number": "5", "theme": ""},
        )

        session = TestSession.objects.get(user=self.user, mode="practice")
        self.assertRedirects(
            response,
            reverse("task_detail", kwargs={"session_uuid": session.uuid, "order": 1}),
            fetch_redirect_response=False,
        )
        self.assertEqual(session.attempts.count(), 1)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

    def test_written_submission_creates_grade_and_report(self):
        self.client.login(username="learner", password="pass12345")
        response = self.client.post(reverse("start_test", kwargs={"mode": "written"}))
        session = TestSession.objects.get(user=self.user, mode="written")
        first_attempt = session.attempts.order_by("sequence_order").first()

        self.assertRedirects(
            response,
            reverse("task_detail", kwargs={"session_uuid": session.uuid, "order": 1}),
            fetch_redirect_response=False,
        )
        self.client.get(
            reverse(
                "task_detail",
                kwargs={"session_uuid": session.uuid, "order": first_attempt.sequence_order},
            )
        )
        response = self.client.post(
            reverse(
                "submit_task",
                kwargs={"session_uuid": session.uuid, "order": first_attempt.sequence_order},
            ),
            {
                "answer_text": (
                    "Salut Nora, Amine a trente-deux ans et il travaille avec moi. "
                    "Il est calme, drole et aime le cinema et la randonnee. "
                    "Je pense qu'il va bien s'integrer au groupe. A samedi."
                )
            },
        )
        first_attempt.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(first_attempt.status, TaskAttempt.STATUS_GRADED)
        self.assertTrue(hasattr(first_attempt, "grade"))

    def test_oral_manual_transcript_fallback(self):
        self.client.login(username="learner", password="pass12345")
        self.client.post(reverse("start_test", kwargs={"mode": "oral"}))
        session = TestSession.objects.get(user=self.user, mode="oral")
        first_attempt = session.attempts.order_by("sequence_order").first()
        self.client.get(
            reverse(
                "task_detail",
                kwargs={"session_uuid": session.uuid, "order": first_attempt.sequence_order},
            )
        )
        response = self.client.post(
            reverse(
                "submit_task",
                kwargs={"session_uuid": session.uuid, "order": first_attempt.sequence_order},
            ),
            {
                "transcript_text": (
                    "Bonjour, je m'appelle Ali. Je travaille dans la logistique "
                    "et j'apprends le francais pour progresser dans ma vie quotidienne."
                )
            },
        )
        first_attempt.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(first_attempt.manual_transcript)
        self.assertEqual(first_attempt.status, TaskAttempt.STATUS_GRADED)

    def test_oral_task_page_includes_question_audio_control(self):
        self.client.login(username="learner", password="pass12345")
        session = start_test_session(self.user, "oral")
        first_attempt = session.attempts.order_by("sequence_order").first()

        response = self.client.get(
            reverse(
                "task_detail",
                kwargs={"session_uuid": session.uuid, "order": first_attempt.sequence_order},
            )
        )

        self.assertContains(response, "Play question")
        self.assertContains(response, "AI-generated examiner audio")
        self.assertContains(
            response,
            reverse(
                "question_audio",
                kwargs={"session_uuid": session.uuid, "order": first_attempt.sequence_order},
            ),
        )

    def test_question_audio_endpoint_generates_and_reuses_cached_tts(self):
        session = start_test_session(self.user, "oral")
        first_attempt = session.attempts.order_by("sequence_order").first()
        self.client.login(username="learner", password="pass12345")
        created_calls = []

        class FakeSpeechResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                return False

            def stream_to_file(self, path):
                Path(path).write_bytes(b"fake mp3 bytes")

        class FakeStreamingResponse:
            def create(self, **kwargs):
                created_calls.append(kwargs)
                return FakeSpeechResponse()

        class FakeSpeech:
            with_streaming_response = FakeStreamingResponse()

        class FakeAudio:
            speech = FakeSpeech()

        class FakeClient:
            audio = FakeAudio()

        with tempfile.TemporaryDirectory() as media_root, override_settings(
            OPENAI_API_KEY="test-key",
            OPENAI_TTS_MODEL="gpt-4o-mini-tts",
            OPENAI_TTS_VOICE="marin",
            OPENAI_TTS_FORMAT="mp3",
            OPENAI_TTS_INSTRUCTIONS="Speak clearly in French.",
            MEDIA_ROOT=media_root,
        ), patch(
            "simulations.services.question_audio.OpenAI", return_value=FakeClient()
        ) as openai_mock:
            url = reverse(
                "question_audio",
                kwargs={"session_uuid": session.uuid, "order": first_attempt.sequence_order},
            )
            response = self.client.get(url)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["Content-Type"], "audio/mpeg")
            self.assertEqual(b"".join(response.streaming_content), b"fake mp3 bytes")
            self.assertEqual(len(created_calls), 1)
            self.assertEqual(created_calls[0]["model"], "gpt-4o-mini-tts")
            self.assertEqual(created_calls[0]["voice"], "marin")
            self.assertEqual(created_calls[0]["response_format"], "mp3")
            self.assertEqual(created_calls[0]["input"], first_attempt.question.prompt)

            response = self.client.get(url)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(b"".join(response.streaming_content), b"fake mp3 bytes")
            self.assertEqual(len(created_calls), 1)
            openai_mock.assert_called_once_with(api_key="test-key")

    def test_question_audio_endpoint_returns_unavailable_without_api_key(self):
        session = start_test_session(self.user, "oral")
        first_attempt = session.attempts.order_by("sequence_order").first()
        self.client.login(username="learner", password="pass12345")

        with tempfile.TemporaryDirectory() as media_root, override_settings(
            OPENAI_API_KEY="",
            MEDIA_ROOT=media_root,
        ):
            response = self.client.get(
                reverse(
                    "question_audio",
                    kwargs={
                        "session_uuid": session.uuid,
                        "order": first_attempt.sequence_order,
                    },
                )
            )

        self.assertEqual(response.status_code, 503)
        self.assertIn("OPENAI_API_KEY", response.content.decode())

    def test_question_audio_endpoint_rejects_written_task(self):
        session = start_test_session(self.user, "written")
        first_attempt = session.attempts.order_by("sequence_order").first()
        self.client.login(username="learner", password="pass12345")

        response = self.client.get(
            reverse(
                "question_audio",
                kwargs={"session_uuid": session.uuid, "order": first_attempt.sequence_order},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_user_cannot_access_another_users_question_audio(self):
        other = User.objects.create_user("other-audio", password="pass12345")
        session = start_test_session(other, "oral")
        first_attempt = session.attempts.order_by("sequence_order").first()
        self.client.login(username="learner", password="pass12345")

        response = self.client.get(
            reverse(
                "question_audio",
                kwargs={"session_uuid": session.uuid, "order": first_attempt.sequence_order},
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_full_simulation_can_be_completed(self):
        self.client.login(username="learner", password="pass12345")
        session = start_test_session(self.user, "full")

        for attempt in session.attempts.order_by("sequence_order"):
            self.client.get(
                reverse(
                    "task_detail",
                    kwargs={
                        "session_uuid": session.uuid,
                        "order": attempt.sequence_order,
                    },
                )
            )
            payload = (
                {
                    "answer_text": (
                        "Bonjour, je reponds a la consigne avec plusieurs details "
                        "concrets, une structure claire et une conclusion adaptee."
                    )
                }
                if attempt.is_written
                else {
                    "transcript_text": (
                        "Bonjour, je reponds oralement a la question avec des details, "
                        "des exemples et une conclusion claire."
                    )
                }
            )
            response = self.client.post(
                reverse(
                    "submit_task",
                    kwargs={
                        "session_uuid": session.uuid,
                        "order": attempt.sequence_order,
                    },
                ),
                payload,
            )
            self.assertEqual(response.status_code, 302)

        session.refresh_from_db()
        response = self.client.get(reverse("report", kwargs={"session_uuid": session.uuid}))

        self.assertEqual(session.status, TestSession.STATUS_COMPLETED)
        self.assertContains(response, "Final report")

    def test_user_cannot_access_another_users_session(self):
        other = User.objects.create_user("other", password="pass12345")
        session = start_test_session(other, "written")
        self.client.login(username="learner", password="pass12345")

        response = self.client.get(
            reverse("report", kwargs={"session_uuid": session.uuid})
        )

        self.assertEqual(response.status_code, 403)

    def test_retry_failed_grade_regrades_saved_answer(self):
        session = start_test_session(self.user, "written")
        attempt = session.attempts.order_by("sequence_order").first()
        attempt.answer_text = (
            "Bonjour, je reponds a la consigne avec des details concrets et une conclusion."
        )
        attempt.word_count_observed = 13
        attempt.within_word_limits = False
        attempt.status = TaskAttempt.STATUS_GRADING_FAILED
        attempt.save()
        TaskGrade.objects.create(
            task_attempt=attempt,
            status=TaskGrade.STATUS_FAILED,
            error_message="Invalid schema",
        )
        self.client.login(username="learner", password="pass12345")

        response = self.client.post(
            reverse(
                "retry_grade",
                kwargs={"session_uuid": session.uuid, "order": attempt.sequence_order},
            )
        )
        attempt.refresh_from_db()

        self.assertRedirects(
            response,
            reverse(
                "task_grade",
                kwargs={"session_uuid": session.uuid, "order": attempt.sequence_order},
            ),
            fetch_redirect_response=False,
        )
        self.assertEqual(attempt.status, TaskAttempt.STATUS_GRADED)
        self.assertEqual(attempt.grade.status, TaskGrade.STATUS_SUCCEEDED)

    def test_task_feedback_shows_examples_and_previous_best_for_same_prompt(self):
        current_session = start_test_session(self.user, "written")
        current_attempt = current_session.attempts.order_by("sequence_order").first()
        current_attempt.status = TaskAttempt.STATUS_GRADED
        current_attempt.answer_text = "Bonjour, voici une reponse courte pour ce sujet."
        current_attempt.word_count_observed = 8
        current_attempt.within_word_limits = False
        current_attempt.save()
        TaskGrade.objects.create(
            task_attempt=current_attempt,
            status=TaskGrade.STATUS_SUCCEEDED,
            overall_score_20=Decimal("10.0"),
            estimated_cefr_level="B1",
            improved_response_status=TaskGrade.STATUS_SUCCEEDED,
            improved_response={
                "improved_response_fr": "Bonjour, voici une version amelioree de ma reponse.",
                "changes_made": ["Structure plus claire."],
                "reusable_phrases": ["Je vous recommande"],
                "focus_next_time": ["Ajouter des details concrets."],
            },
            parsed_result={
                "strengths": [],
                "improvement_advice_fr": [],
                "dimensions": [],
            },
        )

        previous_session = TestSession.objects.create(
            user=self.user,
            test_definition=current_session.test_definition,
            mode="written",
            status=TestSession.STATUS_COMPLETED,
        )
        previous_attempt = TaskAttempt.objects.create(
            test_session=previous_session,
            step=current_attempt.step,
            question=current_attempt.question,
            sequence_order=1,
            status=TaskAttempt.STATUS_GRADED,
            answer_text="Une ancienne reponse meilleure.",
            word_count_observed=4,
            within_word_limits=False,
        )
        TaskGrade.objects.create(
            task_attempt=previous_attempt,
            status=TaskGrade.STATUS_SUCCEEDED,
            overall_score_20=Decimal("16.5"),
            estimated_cefr_level="B2",
            parsed_result={
                "strengths": [],
                "improvement_advice_fr": [],
                "dimensions": [],
            },
        )
        self.client.login(username="learner", password="pass12345")

        response = self.client.get(
            reverse(
                "task_grade",
                kwargs={
                    "session_uuid": current_session.uuid,
                    "order": current_attempt.sequence_order,
                },
            )
        )

        reference_answer = current_attempt.question.expected_response["reference_answer"]
        self.assertContains(response, "Example B2 responses")
        self.assertIn(reference_answer, unescape(response.content.decode()))
        self.assertContains(response, "Same prompt best")
        self.assertContains(response, "16.5/20")
        self.assertContains(response, "Improved version of your response")
        self.assertContains(response, "version amelioree")

    def test_history_links_to_report_and_task_feedback(self):
        session = start_test_session(self.user, "written")
        attempt = session.attempts.order_by("sequence_order").first()
        attempt.status = TaskAttempt.STATUS_GRADED
        attempt.answer_text = "Bonjour, voici une reponse sauvegardee."
        attempt.word_count_observed = 5
        attempt.within_word_limits = False
        attempt.save()
        TaskGrade.objects.create(
            task_attempt=attempt,
            status=TaskGrade.STATUS_SUCCEEDED,
            overall_score_20=Decimal("12.0"),
            estimated_cefr_level="B1",
            parsed_result={
                "strengths": [],
                "improvement_advice_fr": [],
                "dimensions": [],
            },
        )
        self.client.login(username="learner", password="pass12345")

        response = self.client.get(reverse("history"))

        self.assertContains(response, "Full report")
        self.assertContains(response, reverse("report", kwargs={"session_uuid": session.uuid}))
        self.assertContains(response, "Task feedback")
        self.assertContains(
            response,
            reverse(
                "task_grade",
                kwargs={"session_uuid": session.uuid, "order": attempt.sequence_order},
            ),
        )
        self.assertContains(response, "Delete")

    def test_user_can_delete_own_history_item(self):
        session = start_test_session(self.user, "written")
        self.client.login(username="learner", password="pass12345")

        response = self.client.post(
            reverse("delete_history_session", kwargs={"session_uuid": session.uuid})
        )

        self.assertRedirects(response, reverse("history"))
        self.assertFalse(TestSession.objects.filter(pk=session.pk).exists())

    def test_user_cannot_delete_another_users_history_item(self):
        other = User.objects.create_user("other-history", password="pass12345")
        session = start_test_session(other, "written")
        self.client.login(username="learner", password="pass12345")

        response = self.client.post(
            reverse("delete_history_session", kwargs={"session_uuid": session.uuid})
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(TestSession.objects.filter(pk=session.pk).exists())
