from __future__ import annotations

from django.conf import settings
from openai import OpenAI

from grading.services.schemas import GradingResult, ImprovedResponseResult
from simulations.models import TaskAttempt


def build_improved_response(
    attempt: TaskAttempt, grading_result: GradingResult
) -> tuple[ImprovedResponseResult, dict, str]:
    if not settings.OPENAI_API_KEY:
        return build_local_improved_response(attempt, grading_result), {
            "provider": "local_stub",
            "reason": "OPENAI_API_KEY missing",
        }, ""

    prompt = build_improved_response_prompt(attempt, grading_result)
    return request_openai_improved_response(prompt)


def request_openai_improved_response(
    prompt: str,
) -> tuple[ImprovedResponseResult, dict, str]:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.responses.parse(
        model=settings.OPENAI_IMPROVEMENT_MODEL,
        instructions=(
            "You rewrite TCF IRN French practice answers into improved B2-level "
            "versions. Return only the requested structured output."
        ),
        input=prompt,
        text_format=ImprovedResponseResult,
    )
    parsed = getattr(response, "output_parsed", None)
    if parsed is None:
        for output in response.output:
            if output.type != "message":
                continue
            for item in output.content:
                item_parsed = getattr(item, "parsed", None)
                if item_parsed is not None:
                    parsed = item_parsed
                    break
    if parsed is None:
        raise RuntimeError("The improved response could not be parsed.")

    raw_response = response.model_dump(mode="json")
    response_id = getattr(response, "id", "") or ""
    return parsed, raw_response, response_id


def build_improved_response_prompt(
    attempt: TaskAttempt, grading_result: GradingResult
) -> str:
    question = attempt.question
    task = question.task_definition
    expected = question.expected_response or {}
    word_limit = ""
    if task.is_written and task.word_count_min and task.word_count_max:
        word_limit = f"{task.word_count_min}-{task.word_count_max} words"
    elif task.is_oral:
        target = expected.get("word_count_target", {})
        if target:
            word_limit = f"{target.get('min')}-{target.get('max')} spoken words"

    missing = ", ".join(grading_result.elements_missing) or "None"
    errors = "; ".join(
        f"{error.type}: {error.excerpt} -> {error.correction}"
        for error in grading_result.errors[:8]
    ) or "None listed"

    return "\n".join(
        [
            "Return JSON with keys: improved_response_fr, changes_made, "
            "reusable_phrases, focus_next_time.",
            "",
            "Rewrite the learner's own production into a stronger TCF IRN response.",
            "Keep the same personal facts and intent when possible.",
            "Do not copy the reference answer. Do not invent major new facts.",
            "Aim for a clear B2-level answer that respects the task constraints.",
            "Use natural French suitable for the addressee and register.",
            "",
            f"Section: {task.section.name_fr}",
            f"Task {task.task_number}: {task.name_fr}",
            f"Format: {task.format}",
            f"Constraints: {word_limit or 'Use the task timing and format constraints.'}",
            f"Prompt: {question.prompt}",
            f"Register: {question.register or 'Not specified'}",
            f"Addressee: {question.addressee or 'Not specified'}",
            "",
            "Expected structure:",
            "\n".join(f"- {item}" for item in expected.get("structure", [])) or "- Not specified",
            "",
            f"Missing elements from grading: {missing}",
            f"Observed errors from grading: {errors}",
            "",
            "Learner production:",
            attempt.candidate_text or "(empty)",
        ]
    )


def build_local_improved_response(
    attempt: TaskAttempt, grading_result: GradingResult
) -> ImprovedResponseResult:
    text = attempt.candidate_text.strip()
    question = attempt.question
    task = question.task_definition
    expected = question.expected_response or {}
    starter = (
        text
        if text
        else "Je reponds a la consigne avec une structure claire et des exemples concrets."
    )
    improved = (
        starter
        + "\n\n"
        + "Version de developpement: activez OPENAI_API_KEY pour obtenir une "
        + "reformulation personnalisee, naturelle et corrigee au niveau B2."
    )
    return ImprovedResponseResult(
        improved_response_fr=improved,
        changes_made=[
            "Mode local: reformulation detaillee disponible avec OpenAI.",
            "Conserver une structure claire adaptee a la tache.",
        ],
        reusable_phrases=expected.get("key_vocabulary", [])[:5],
        focus_next_time=grading_result.elements_missing[:3]
        or [f"Respecter le format de la tache {task.task_number}."],
    )
