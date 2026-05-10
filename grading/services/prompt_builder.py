from __future__ import annotations

from exams.models import GradingDimension, Question, ScoreBand
from simulations.models import TaskAttempt

PROMPT_VERSION = "grader-v1"


def build_grader_markdown(attempt: TaskAttempt) -> str:
    return build_grader_markdown_for_question(
        question=attempt.question,
        candidate_text=attempt.candidate_text,
        word_count_observed=attempt.word_count_observed or 0,
        within_word_limits=attempt.within_word_limits,
        submitted_late=attempt.submitted_late,
        audio_evidence_available=bool(attempt.audio_file),
    )


def build_grader_preview_for_question(question: Question) -> str:
    return build_grader_markdown_for_question(
        question=question,
        candidate_text="[Production du candidat a evaluer]",
        word_count_observed=0,
        within_word_limits=None,
        submitted_late=False,
        audio_evidence_available=False,
    )


def build_grader_markdown_for_question(
    *,
    question: Question,
    candidate_text: str,
    word_count_observed: int,
    within_word_limits: bool | None,
    submitted_late: bool,
    audio_evidence_available: bool,
) -> str:
    task = question.task_definition
    section = task.section
    exam = section.exam
    expected = question.expected_response

    lines: list[str] = []
    add = lines.append
    add(f"# Grader TCF IRN - {section.name_fr}, Tache {task.task_number}")
    add("")
    add(f"_Question `{question.source_id}` - prompt version `{PROMPT_VERSION}`_")
    add("")
    add("## Role")
    add(
        f"Tu es un examinateur certifie du {exam.full_name or exam.name}. "
        f"Tu evalues une production candidate pour le niveau cible {exam.target_level}."
    )
    add("")
    add("## Contexte de la tache")
    add(f"- Section: {section.name_fr} - {section.format}")
    add(f"- Tache {task.task_number}: {task.name_fr} ({task.name_en})")
    add(f"- Type: {question.task_type_fr}")
    add(f"- Objectif: {task.objective}")
    add(f"- Format: {task.format}")
    if task.is_written:
        add(
            f"- Duree suggeree: {task.suggested_duration_minutes} min; "
            f"longueur attendue: {task.word_count_min}-{task.word_count_max} mots "
            f"(cible {task.word_count_target})"
        )
        add(f"- Nombre de mots observe: {word_count_observed}")
        add(f"- Dans les limites: {bool(within_word_limits)}")
    else:
        add(f"- Duree: {task.duration_minutes} min; preparation: 0 min")
        target = expected.get("word_count_target", {})
        if target:
            add(
                f"- Longueur orale estimee: {target.get('min')}-{target.get('max')} mots "
                f"(ideal {target.get('ideal')})"
            )
        if audio_evidence_available:
            add(
                "- Phonologie: le correcteur texte utilise le transcript; "
                "un module audio separe peut ajouter prononciation et fluidite."
            )
        else:
            add("- Phonologie: approximation limitee depuis le transcript uniquement.")
    if question.addressee:
        add(f"- Destinataire: {question.addressee}")
    if question.register:
        add(f"- Registre attendu: {question.register}")
    if question.channel:
        add(f"- Support: {question.channel}")
    if question.examiner_role_fr:
        add(f"- Role examinateur: {question.examiner_role_fr}")
    if task.examiner_behavior:
        add(f"- Comportement examinateur: {task.examiner_behavior}")
    add(f"- Soumission tardive: {submitted_late}")
    add("")
    add("## Sujet presente au candidat")
    add("")
    add("> " + question.prompt.replace("\n", "\n> "))
    add("")
    if question.themes:
        add("Themes: " + ", ".join(question.themes))
        add("")

    add("## Structure attendue")
    for index, item in enumerate(expected.get("structure", []), start=1):
        add(f"{index}. {item}")
    add("")

    add("## Elements a couvrir")
    for item in expected.get("key_elements_to_cover", []):
        add(f"- [ ] {item}")
    add("")

    add("## Lexique attendu")
    vocabulary = expected.get("key_vocabulary", [])
    add(", ".join(f"`{item}`" for item in vocabulary) if vocabulary else "Non specifie")
    add("")

    add("## Grammaire attendue")
    for item in expected.get("key_grammar", []):
        add(f"- {item}")
    add("")

    add("## Modele A")
    add("```")
    add(expected.get("reference_answer", ""))
    add("```")
    add("")
    if expected.get("alternative_answer"):
        add("## Modele B")
        add("```")
        add(expected["alternative_answer"])
        add("```")
        add("")
    add(
        "Les modeles sont des exemples B2 reussis. Ne penalise pas une reponse "
        "differente si elle reste pertinente, structuree et linguistiquement comparable."
    )
    add("")

    add("## Points d'attention")
    for item in question.evaluation_focus:
        add(f"- {item}")
    add("")

    add("## Rubrique de notation")
    dimensions = {
        dimension.source_id: dimension
        for dimension in GradingDimension.objects.filter(
            source_id__in=task.rubric_dimensions
        )
    }
    for dimension_id in task.rubric_dimensions:
        dimension = dimensions.get(dimension_id)
        if not dimension:
            continue
        add(f"### {dimension.name_fr} ({dimension.name_en})")
        add(dimension.description)
        if dimension.weight_hint:
            add(f"Poids indicatif: {dimension.weight_hint}")
        task_rubric = task.task_specific_rubric.get(dimension_id, {})
        if task_rubric:
            add(f"- Cible B2: {task_rubric.get('B2_target', '')}")
            add(f"- Sous le B2: {task_rubric.get('common_below_B2', '')}")
        descriptors = dimension.level_descriptors.all().order_by("level")
        if descriptors:
            add("")
            add("| Niveau | Descripteur |")
            add("| --- | --- |")
            for descriptor in descriptors:
                add(f"| {descriptor.level} | {descriptor.description} |")
        add("")

    add("## Echelle /20")
    add("| Niveau CECRL | Score /20 |")
    add("| --- | --- |")
    for band in ScoreBand.objects.filter(exam=exam).order_by("score_min"):
        add(f"| {band.level} | {band.score_min}-{band.score_max} |")
    add("")
    scoring = exam.metadata.get("scoring", {})
    failure_conditions = scoring.get("automatic_failure_conditions") or [
        "Nombre de mots non respecte",
        "Reponse hors-sujet",
        "Tache obligatoire manquante",
        "Production incomplete",
    ]
    add("## Conditions d'echec automatique")
    for item in failure_conditions:
        add(f"- {item}")
    add("")

    add("## Format de sortie")
    add("Retourne uniquement un objet JSON conforme au schema structure fourni par l'application.")
    add("Le champ `dimensions` doit etre une liste, pas un objet; chaque element doit inclure `dimension_id`.")
    add("Justifie chaque dimension avec des extraits courts du candidat dans `evidence`.")
    add("")
    add("## Production du candidat a evaluer")
    add("```")
    add(candidate_text)
    add("```")
    return "\n".join(lines)
