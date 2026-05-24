from __future__ import annotations

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import FileResponse, Http404, HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from exams.models import Question, TaskDefinition, TestDefinition
from grading.services.grade_attempt import grade_attempt
from grading.services.transcription import transcribe_audio_file
from simulations.api.serializers import (
    LoginSerializer,
    OralSubmitSerializer,
    PracticeStartSerializer,
    SignUpSerializer,
    TestStartSerializer,
    WrittenSubmitSerializer,
    attempt_payload,
    session_payload,
    task_definition_payload,
    test_definition_payload,
)
from simulations.models import TaskAttempt, TestSession
from simulations.services.navigation import (
    can_open_attempt,
    ensure_session_owner,
    mark_session_completion_if_ready,
    next_attempt,
    start_attempt_if_needed,
)
from simulations.services.question_audio import (
    QuestionAudioUnavailable,
    get_or_create_question_audio,
)
from simulations.services.scoring import update_session_scores
from simulations.services.start_session import start_practice_session, start_test_session
from simulations.services.word_count import count_words
from simulations.views import build_example_responses, get_personal_best_attempt


def get_session_for_request(session_uuid, user) -> TestSession:
    session = get_object_or_404(
        TestSession.objects.select_related("test_definition"), uuid=session_uuid
    )
    ensure_session_owner(session, user)
    return session


def get_attempt_for_request(session: TestSession, order: int) -> TaskAttempt:
    return get_object_or_404(
        TaskAttempt.objects.select_related(
            "test_session",
            "question",
            "question__task_definition",
            "question__task_definition__section",
            "step",
            "step__task_definition",
            "grade",
        ),
        test_session=session,
        sequence_order=order,
    )


@api_view(["GET"])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def csrf(request: Request):
    return Response({"csrf_token": get_token(request)})


@api_view(["GET"])
def me(request: Request):
    user: User = request.user
    return Response(
        {
            "id": user.id,
            "username": user.username,
            "display_name": user.get_full_name() or user.username,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request: Request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = authenticate(
        request,
        username=serializer.validated_data["username"],
        password=serializer.validated_data["password"],
    )
    if user is None:
        return Response(
            {"detail": "Invalid username or password."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    login(request, user)
    return Response({"user": {"id": user.id, "username": user.username}})


@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request: Request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    login(request, user)
    return Response(
        {"user": {"id": user.id, "username": user.username}},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
def logout_view(request: Request):
    logout(request)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
def test_definitions(request: Request):
    definitions = TestDefinition.objects.filter(is_active=True).order_by("source_id")
    return Response([test_definition_payload(definition) for definition in definitions])


@api_view(["GET"])
def practice_options(request: Request):
    task_definitions = (
        TaskDefinition.objects.select_related("section").filter(is_active=True).order_by("task_number")
    )
    themes = sorted(
        {
            str(theme)
            for themes in Question.objects.filter(is_active=True).values_list("themes", flat=True)
            for theme in (themes or [])
            if str(theme).strip()
        },
        key=str.lower,
    )
    return Response(
        {
            "task_definitions": [
                task_definition_payload(task_definition)
                for task_definition in task_definitions
            ],
            "themes": themes,
        }
    )


@api_view(["GET"])
def sessions(request: Request):
    queryset = (
        request.user.test_sessions.select_related("test_definition")
        .prefetch_related(
            "attempts__question",
            "attempts__question__task_definition",
            "attempts__grade",
        )[:50]
    )
    return Response([session_payload(session) for session in queryset])


@api_view(["POST"])
def start_session(request: Request):
    serializer = TestStartSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        session = start_test_session(request.user, serializer.validated_data["mode"])
    except TestDefinition.DoesNotExist:
        return Response(
            {"detail": "This test mode is not available yet. Import the question bank first."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except RuntimeError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(session_payload(session), status=status.HTTP_201_CREATED)


@api_view(["POST"])
def start_practice(request: Request):
    serializer = PracticeStartSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        session = start_practice_session(
            request.user,
            task_number=serializer.validated_data.get("task_number"),
            theme=serializer.validated_data.get("theme", ""),
        )
    except RuntimeError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    except TestDefinition.DoesNotExist:
        return Response(
            {"detail": "Practice mode needs the full test definition. Import the question bank first."},
            status=status.HTTP_404_NOT_FOUND,
        )
    return Response(session_payload(session), status=status.HTTP_201_CREATED)


@api_view(["GET", "DELETE"])
def session_detail(request: Request, session_uuid):
    session = get_session_for_request(session_uuid, request.user)
    if request.method == "DELETE":
        for attempt in session.attempts.all():
            if attempt.audio_file:
                attempt.audio_file.delete(save=False)
        session.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(session_payload(session))


@api_view(["GET"])
def session_report(request: Request, session_uuid):
    session = get_session_for_request(session_uuid, request.user)
    update_session_scores(session)
    return Response(session_payload(session))


@api_view(["GET"])
def attempt_detail(request: Request, session_uuid, order: int):
    session = get_session_for_request(session_uuid, request.user)
    attempt = get_attempt_for_request(session, order)
    try:
        start_attempt_if_needed(attempt)
    except ValidationError:
        return Response(
            {
                "detail": "Complete the previous task before opening this one.",
                "current_step_order": session.current_step_order,
            },
            status=status.HTTP_409_CONFLICT,
        )
    attempts = session.attempts.select_related("question").order_by("sequence_order")
    return Response(
        {
            "session": session_payload(session, include_attempts=False),
            "attempt": attempt_payload(attempt),
            "attempts": [attempt_payload(item, include_question=True) for item in attempts],
            "next_attempt_order": next_attempt(attempt).sequence_order if next_attempt(attempt) else None,
        }
    )


@api_view(["POST"])
def submit_attempt(request: Request, session_uuid, order: int):
    session = get_session_for_request(session_uuid, request.user)
    attempt = get_attempt_for_request(session, order)

    if attempt.status in [TaskAttempt.STATUS_GRADED, TaskAttempt.STATUS_GRADING_FAILED]:
        return Response(attempt_payload(attempt))
    if not can_open_attempt(attempt):
        raise PermissionDenied("Previous tasks must be submitted first.")
    start_attempt_if_needed(attempt)

    now = timezone.now()
    attempt.submitted_at = now
    attempt.submitted_late = bool(attempt.deadline_at and now > attempt.deadline_at)

    if attempt.is_written:
        serializer = WrittenSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answer_text = serializer.validated_data.get("answer_text", "").strip()
        attempt.answer_text = answer_text
        attempt.word_count_observed = count_words(answer_text)
        task = attempt.question.task_definition
        attempt.within_word_limits = (
            task.word_count_min <= attempt.word_count_observed <= task.word_count_max
            if task.word_count_min is not None and task.word_count_max is not None
            else True
        )
    else:
        serializer = OralSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        manual_transcript = serializer.validated_data.get("transcript_text", "").strip()
        uploaded_audio = serializer.validated_data.get("audio_file")
        if uploaded_audio:
            attempt.audio_file = uploaded_audio
            attempt.audio_mime_type = getattr(uploaded_audio, "content_type", "") or ""
            attempt.save()
        if manual_transcript:
            attempt.transcript_text = manual_transcript
            attempt.manual_transcript = True
        elif attempt.audio_file:
            attempt.transcript_text = transcribe_audio_file(attempt.audio_file.path)
            attempt.manual_transcript = False
        attempt.answer_text = ""
        attempt.word_count_observed = count_words(attempt.transcript_text)
        attempt.within_word_limits = bool(attempt.transcript_text.strip())

    attempt.status = TaskAttempt.STATUS_SUBMITTED
    attempt.save()
    grade_attempt(attempt)
    update_session_scores(session)
    mark_session_completion_if_ready(session)
    attempt = get_attempt_for_request(session, order)
    return Response(attempt_payload(attempt))


@api_view(["GET"])
def attempt_grade(request: Request, session_uuid, order: int):
    session = get_session_for_request(session_uuid, request.user)
    attempt = get_attempt_for_request(session, order)
    update_session_scores(session)
    next_item = next_attempt(attempt)
    personal_best_attempt = get_personal_best_attempt(attempt)
    return Response(
        {
            "session": session_payload(session, include_attempts=False),
            "attempt": attempt_payload(attempt),
            "grade": attempt_payload(attempt)["grade"],
            "next_attempt": attempt_payload(next_item) if next_item else None,
            "example_responses": build_example_responses(attempt.question),
            "personal_best_attempt": (
                attempt_payload(personal_best_attempt)
                if personal_best_attempt is not None
                else None
            ),
        }
    )


@api_view(["POST"])
def retry_grade(request: Request, session_uuid, order: int):
    session = get_session_for_request(session_uuid, request.user)
    attempt = get_attempt_for_request(session, order)
    if attempt.status not in {
        TaskAttempt.STATUS_SUBMITTED,
        TaskAttempt.STATUS_GRADED,
        TaskAttempt.STATUS_GRADING_FAILED,
    }:
        return Response(
            {"detail": "This task has not been submitted yet."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not attempt.candidate_text.strip():
        return Response(
            {"detail": "This task has no saved answer to grade."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    grade_attempt(attempt)
    update_session_scores(session)
    mark_session_completion_if_ready(session)
    attempt = get_attempt_for_request(session, order)
    return Response(attempt_payload(attempt))


@api_view(["GET"])
def question_audio(request: Request, session_uuid, order: int):
    session = get_session_for_request(session_uuid, request.user)
    attempt = get_attempt_for_request(session, order)
    if not attempt.is_oral:
        raise Http404("Question audio is only available for oral tasks.")

    try:
        audio_file = get_or_create_question_audio(attempt.question)
    except QuestionAudioUnavailable as exc:
        return HttpResponse(str(exc), status=503, content_type="text/plain")

    response = FileResponse(open(audio_file.path, "rb"), content_type=audio_file.content_type)
    response["Cache-Control"] = "private, max-age=3600"
    return response
