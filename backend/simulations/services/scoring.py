from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from exams.models import ScoreBand
from simulations.models import TestSession


def round_half(value: Decimal) -> Decimal:
    return (value * Decimal("2")).quantize(Decimal("1"), rounding=ROUND_HALF_UP) / Decimal(
        "2"
    )


def level_for_score(session: TestSession, score: Decimal | None) -> str:
    if score is None:
        return ""
    band = (
        ScoreBand.objects.filter(
            exam=session.test_definition.steps.first().task_definition.section.exam,
            score_min__lte=score,
            score_max__gte=score,
        )
        .order_by("score_min")
        .first()
    )
    return band.level if band else ""


def update_session_scores(session: TestSession) -> TestSession:
    attempts = session.attempts.select_related("question").prefetch_related("grade")
    section_scores: dict[str, list[Decimal]] = {"expression_orale": [], "expression_ecrite": []}

    for attempt in attempts:
        grade = getattr(attempt, "grade", None)
        if not grade or grade.status != "succeeded" or grade.overall_score_20 is None:
            continue
        section_scores[attempt.question.section_source_id].append(grade.overall_score_20)

    updates: list[str] = []
    for section_id, field_prefix in [
        ("expression_orale", "oral"),
        ("expression_ecrite", "written"),
    ]:
        scores = section_scores[section_id]
        score_field = f"{field_prefix}_score"
        level_field = f"{field_prefix}_level"
        if scores:
            score = round_half(sum(scores, Decimal("0")) / Decimal(len(scores)))
            setattr(session, score_field, score)
            setattr(session, level_field, level_for_score(session, score))
        else:
            setattr(session, score_field, None)
            setattr(session, level_field, "")
        updates.extend([score_field, level_field])

    session.save(update_fields=[*updates, "updated_at"])
    return session
