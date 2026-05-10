from __future__ import annotations

import random

from django.db import transaction
from django.utils import timezone

from exams.models import Question, TestDefinition, TestDefinitionStep
from simulations.models import TaskAttempt, TestSession


@transaction.atomic
def start_test_session(user, mode: str) -> TestSession:
    test_definition = (
        TestDefinition.objects.filter(source_id=mode, is_active=True)
        .prefetch_related("steps__task_definition")
        .get()
    )
    seed = random.SystemRandom().randint(1, 2_147_483_647)
    rng = random.Random(seed)
    session = TestSession.objects.create(
        user=user,
        test_definition=test_definition,
        mode=mode,
        status=TestSession.STATUS_IN_PROGRESS,
        started_at=timezone.now(),
        random_seed=seed,
    )

    for step in test_definition.steps.select_related("task_definition").order_by(
        "sequence_order"
    ):
        questions = list(
            Question.objects.filter(
                task_definition=step.task_definition,
                is_active=True,
            ).order_by("source_id")
        )
        if not questions:
            raise RuntimeError(
                f"No active questions for task {step.task_definition.source_id}"
            )
        question = rng.choice(questions)
        TaskAttempt.objects.create(
            test_session=session,
            step=step,
            question=question,
            task_definition_snapshot=step.task_definition.raw_source,
            question_snapshot=question.raw_source,
            sequence_order=step.sequence_order,
        )

    return session


@transaction.atomic
def start_practice_session(
    user, *, task_number: int | None = None, theme: str = ""
) -> TestSession:
    questions = Question.objects.filter(is_active=True).select_related(
        "task_definition", "task_definition__section"
    )
    if task_number:
        questions = questions.filter(task_number=task_number)

    candidates = list(questions.order_by("source_id"))
    if theme:
        normalized_theme = theme.strip().lower()
        candidates = [
            question
            for question in candidates
            if normalized_theme in [str(item).lower() for item in question.themes]
        ]
    if not candidates:
        raise RuntimeError("No active questions match this practice filter.")

    seed = random.SystemRandom().randint(1, 2_147_483_647)
    question = random.Random(seed).choice(candidates)
    test_definition = TestDefinition.objects.get(source_id=TestDefinition.MODE_FULL)
    step = TestDefinitionStep.objects.get(
        test_definition=test_definition,
        task_definition=question.task_definition,
    )
    session = TestSession.objects.create(
        user=user,
        test_definition=test_definition,
        mode="practice",
        status=TestSession.STATUS_IN_PROGRESS,
        started_at=timezone.now(),
        random_seed=seed,
        metadata={
            "practice": True,
            "task_number": task_number,
            "theme": theme,
            "selected_question_id": question.source_id,
        },
    )
    TaskAttempt.objects.create(
        test_session=session,
        step=step,
        question=question,
        task_definition_snapshot=question.task_definition.raw_source,
        question_snapshot=question.raw_source,
        sequence_order=1,
    )
    return session
