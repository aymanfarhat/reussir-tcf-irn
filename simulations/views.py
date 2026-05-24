from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from exams.models import Question, TaskDefinition, TestDefinition
from grading.services.grade_attempt import grade_attempt
from grading.services.transcription import transcribe_audio_file
from simulations.forms import SignUpForm
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
from simulations.services.start_session import start_test_session
from simulations.services.start_session import start_practice_session
from simulations.services.word_count import count_words


def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("dashboard")
    return render(request, "registration/signup.html", {"form": form})


@login_required
def dashboard(request):
    definitions = TestDefinition.objects.filter(is_active=True).order_by("source_id")
    recent_sessions = request.user.test_sessions.select_related("test_definition")[:5]
    return render(
        request,
        "simulations/dashboard.html",
        {"definitions": definitions, "recent_sessions": recent_sessions},
    )


@login_required
def practice_start(request):
    task_definitions = TaskDefinition.objects.select_related("section").filter(
        is_active=True
    )
    task_definitions = task_definitions.order_by("task_number")
    themes = sorted(
        {
            str(theme)
            for themes in Question.objects.filter(is_active=True).values_list(
                "themes", flat=True
            )
            for theme in (themes or [])
            if str(theme).strip()
        },
        key=str.lower,
    )

    if request.method == "POST":
        task_number_raw = request.POST.get("task_number", "").strip()
        task_number_invalid = False
        try:
            task_number = int(task_number_raw) if task_number_raw else None
        except ValueError:
            messages.error(request, "Choose a valid task type.")
            task_number = None
            task_number_invalid = True
        theme = request.POST.get("theme", "").strip()
        if task_number_invalid:
            return render(
                request,
                "simulations/practice_start.html",
                {"task_definitions": task_definitions, "themes": themes},
            )
        try:
            session = start_practice_session(
                request.user, task_number=task_number, theme=theme
            )
        except RuntimeError as exc:
            messages.error(request, str(exc))
        except TestDefinition.DoesNotExist:
            messages.error(
                request,
                "Practice mode needs the full test definition. Import the question bank first.",
            )
        else:
            return redirect("task_detail", session_uuid=session.uuid, order=1)

    return render(
        request,
        "simulations/practice_start.html",
        {"task_definitions": task_definitions, "themes": themes},
    )


@login_required
def start_test(request, mode: str):
    if request.method != "POST":
        return redirect("dashboard")
    try:
        session = start_test_session(request.user, mode)
    except TestDefinition.DoesNotExist:
        messages.error(
            request,
            "This test mode is not available yet. Import the question bank first.",
        )
        return redirect("dashboard")
    except RuntimeError as exc:
        messages.error(request, str(exc))
        return redirect("dashboard")
    return redirect("task_detail", session_uuid=session.uuid, order=1)


@login_required
def task_detail(request, session_uuid, order: int):
    session = get_session_for_user(session_uuid, request.user)
    attempt = get_object_or_404(
        TaskAttempt.objects.select_related(
            "test_session",
            "question",
            "question__task_definition",
            "question__task_definition__section",
            "step",
            "step__task_definition",
        ),
        test_session=session,
        sequence_order=order,
    )
    try:
        start_attempt_if_needed(attempt)
    except ValidationError:
        messages.error(request, "Complete the previous task before opening this one.")
        return redirect("task_detail", session_uuid=session.uuid, order=session.current_step_order)

    if attempt.status in [TaskAttempt.STATUS_GRADED, TaskAttempt.STATUS_GRADING_FAILED]:
        return redirect("task_grade", session_uuid=session.uuid, order=order)

    template = (
        "simulations/task_written.html" if attempt.is_written else "simulations/task_oral.html"
    )
    return render_task(request, template, session, attempt)


@login_required
def question_audio(request, session_uuid, order: int):
    session = get_session_for_user(session_uuid, request.user)
    attempt = get_object_or_404(
        TaskAttempt.objects.select_related(
            "test_session",
            "question",
            "question__task_definition",
            "question__task_definition__section",
        ),
        test_session=session,
        sequence_order=order,
    )
    if not attempt.is_oral:
        raise Http404("Question audio is only available for oral tasks.")

    try:
        audio_file = get_or_create_question_audio(attempt.question)
    except QuestionAudioUnavailable as exc:
        return HttpResponse(str(exc), status=503, content_type="text/plain")

    response = FileResponse(open(audio_file.path, "rb"), content_type=audio_file.content_type)
    response["Cache-Control"] = "private, max-age=3600"
    return response


@login_required
def submit_task(request, session_uuid, order: int):
    if request.method != "POST":
        return redirect("task_detail", session_uuid=session_uuid, order=order)

    session = get_session_for_user(session_uuid, request.user)
    attempt = get_object_or_404(
        TaskAttempt.objects.select_related(
            "test_session",
            "question",
            "question__task_definition",
            "question__task_definition__section",
            "step",
            "step__task_definition",
        ),
        test_session=session,
        sequence_order=order,
    )

    if attempt.status in [TaskAttempt.STATUS_GRADED, TaskAttempt.STATUS_GRADING_FAILED]:
        return redirect("task_grade", session_uuid=session.uuid, order=order)
    if not can_open_attempt(attempt):
        raise PermissionDenied("Previous tasks must be submitted first.")
    start_attempt_if_needed(attempt)

    now = timezone.now()
    attempt.submitted_at = now
    attempt.submitted_late = bool(attempt.deadline_at and now > attempt.deadline_at)

    if attempt.is_written:
        answer_text = request.POST.get("answer_text", "").strip()
        attempt.answer_text = answer_text
        attempt.word_count_observed = count_words(answer_text)
        task = attempt.question.task_definition
        attempt.within_word_limits = (
            task.word_count_min <= attempt.word_count_observed <= task.word_count_max
            if task.word_count_min is not None and task.word_count_max is not None
            else True
        )
    else:
        manual_transcript = request.POST.get("transcript_text", "").strip()
        uploaded_audio = request.FILES.get("audio_file")
        if uploaded_audio:
            attempt.audio_file = uploaded_audio
            attempt.audio_mime_type = uploaded_audio.content_type or ""
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
    return redirect("task_grade", session_uuid=session.uuid, order=order)


@login_required
def task_grade(request, session_uuid, order: int):
    session = get_session_for_user(session_uuid, request.user)
    attempt = get_object_or_404(
        TaskAttempt.objects.select_related(
            "test_session", "question", "question__task_definition", "step"
        ),
        test_session=session,
        sequence_order=order,
    )
    next_item = next_attempt(attempt)
    update_session_scores(session)
    example_responses = build_example_responses(attempt.question)
    personal_best_attempt = get_personal_best_attempt(attempt)
    return render(
        request,
        "simulations/task_grade.html",
        {
            "session": session,
            "attempt": attempt,
            "grade": getattr(attempt, "grade", None),
            "next_attempt": next_item,
            "example_responses": example_responses,
            "personal_best_attempt": personal_best_attempt,
        },
    )


@login_required
def retry_grade(request, session_uuid, order: int):
    if request.method != "POST":
        return redirect("task_grade", session_uuid=session_uuid, order=order)

    session = get_session_for_user(session_uuid, request.user)
    attempt = get_object_or_404(
        TaskAttempt.objects.select_related(
            "test_session",
            "question",
            "question__task_definition",
            "question__task_definition__section",
            "step",
            "step__task_definition",
        ),
        test_session=session,
        sequence_order=order,
    )
    if attempt.status != TaskAttempt.STATUS_GRADING_FAILED:
        return redirect("task_grade", session_uuid=session.uuid, order=order)

    grade_attempt(attempt)
    update_session_scores(session)
    mark_session_completion_if_ready(session)
    return redirect("task_grade", session_uuid=session.uuid, order=order)


@login_required
def report(request, session_uuid):
    session = get_session_for_user(session_uuid, request.user)
    update_session_scores(session)
    attempts = session.attempts.select_related(
        "question", "question__task_definition", "grade"
    ).order_by("sequence_order")
    return render(
        request,
        "simulations/report.html",
        {"session": session, "attempts": attempts},
    )


@login_required
def history(request):
    sessions = (
        request.user.test_sessions.select_related("test_definition")
        .prefetch_related(
            "attempts__question",
            "attempts__question__task_definition",
            "attempts__grade",
        )[:50]
    )
    return render(request, "simulations/history.html", {"sessions": sessions})


@login_required
def delete_history_session(request, session_uuid):
    if request.method != "POST":
        return redirect("history")

    session = get_session_for_user(session_uuid, request.user)
    for attempt in session.attempts.all():
        if attempt.audio_file:
            attempt.audio_file.delete(save=False)
    session.delete()
    messages.success(request, "History item deleted.")
    return redirect("history")


def get_session_for_user(session_uuid, user) -> TestSession:
    session = get_object_or_404(
        TestSession.objects.select_related("test_definition"), uuid=session_uuid
    )
    ensure_session_owner(session, user)
    return session


def render_task(request, template: str, session: TestSession, attempt: TaskAttempt):
    attempts = session.attempts.select_related("question").order_by("sequence_order")
    deadline_iso = attempt.deadline_at.isoformat() if attempt.deadline_at else ""
    return render(
        request,
        template,
        {
            "session": session,
            "attempt": attempt,
            "attempts": attempts,
            "deadline_iso": deadline_iso,
            "question_audio_url": (
                reverse(
                    "question_audio",
                    kwargs={"session_uuid": session.uuid, "order": attempt.sequence_order},
                )
                if attempt.is_oral
                else ""
            ),
            "submit_url": reverse(
                "submit_task",
                kwargs={"session_uuid": session.uuid, "order": attempt.sequence_order},
            ),
        },
    )


def build_example_responses(question: Question) -> list[dict[str, str]]:
    expected = question.expected_response or {}
    responses = []
    for label, key in [
        ("Example response A", "reference_answer"),
        ("Example response B", "alternative_answer"),
    ]:
        answer = (expected.get(key) or "").strip()
        if answer:
            responses.append({"label": label, "answer": answer})
    return responses


def get_personal_best_attempt(attempt: TaskAttempt) -> TaskAttempt | None:
    return (
        TaskAttempt.objects.select_related("grade", "test_session")
        .filter(
            test_session__user=attempt.test_session.user,
            question=attempt.question,
            status=TaskAttempt.STATUS_GRADED,
            grade__status="succeeded",
            grade__overall_score_20__isnull=False,
        )
        .exclude(pk=attempt.pk)
        .order_by("-grade__overall_score_20", "-submitted_at", "-created_at")
        .first()
    )
