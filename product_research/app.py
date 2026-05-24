"""TCF IRN review app — Flask wrapper around question_bank.json.

Serves index.html, exposes the JSON, and renders a per-question grader prompt
(Markdown) suitable for handing to an LLM grading agent.
"""
from __future__ import annotations

import json
from pathlib import Path

from flask import Flask, abort, jsonify, send_from_directory

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "question_bank.json"

app = Flask(__name__, static_folder=None)


def load_data() -> dict:
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def find_task(data: dict, task_id: str):
    for sec in data["sections"]:
        for t in sec["tasks"]:
            if t["id"] == task_id:
                return t, sec
    return None, None


# ----------------------------------------------------------------------------
# Markdown grader prompt template
# ----------------------------------------------------------------------------

def build_grader_markdown(q: dict, data: dict) -> str:
    task, section = find_task(data, q["task_id"])
    if task is None:
        raise ValueError(f"task {q['task_id']} not found")

    is_written = q["section"] == "expression_ecrite"
    er = q["expected_response"]
    meta = data["metadata"]
    sc = data["scoring"]

    L: list[str] = []
    add = L.append

    # ---- Header ----
    add(f"# Grader TCF IRN — {section['name_fr']}, Tâche {q['task_number']}")
    add("")
    add(f"_Question `{q['id']}` • généré depuis `question_bank.json` v{meta['version']}_")
    add("")

    # ---- Role ----
    add("## Rôle")
    add(
        f"Tu es un **examinateur certifié** du **{meta['exam_full_name']}** "
        f"({meta['issuing_organization']}). Tu évalues une production candidate sur "
        f"la tâche décrite ci-dessous, en appliquant strictement les critères officiels "
        f"du CECRL et la grille de notation propre à cette tâche. Le niveau cible visé "
        f"par les candidats est **{meta['target_level']}** "
        f"(naturalisation française à partir du {meta['naturalization_requirement_from']})."
    )
    add("")

    # ---- Task context ----
    add("## Contexte de la tâche")
    add(f"- **Section** : {section['name_fr']} — _{section['format']}_")
    add(f"- **Tâche {q['task_number']}** : {task['name_fr']} ({task['name_en']})")
    add(f"- **Type** : {q['task_type_fr']}")
    add(f"- **Objectif pédagogique** : {task['objective']}")
    add(f"- **Format** : {task['format']}")
    if is_written:
        section_total = q["timing"].get(
            "section_total_minutes",
            q["timing"].get("total_section_duration_minutes", section.get("total_duration_minutes")),
        )
        add(
            f"- **Durée suggérée** : {q['timing']['suggested_duration_minutes']} min "
            f"sur {section_total} min pour la section"
        )
        wc = er["word_count"]
        add(
            f"- **Longueur attendue** : **{wc['min']}–{wc['max']} mots** "
            f"(cible ~{wc['target']})"
        )
    else:
        prep = q["timing"].get("preparation_minutes", 0)
        add(
            f"- **Durée** : {q['timing']['duration_minutes']} min, "
            f"{prep} min de préparation"
        )
        wc = er["word_count_target"]
        add(
            f"- **Longueur orale estimée** : ~{wc['ideal']} mots "
            f"({wc['min']}–{wc['max']}), basée sur ~95–115 mots/min"
        )
    if q.get("addressee"):
        add(f"- **Destinataire** : {q['addressee']}")
    if q.get("register"):
        add(f"- **Registre attendu** : {q['register']}")
    if q.get("channel"):
        add(f"- **Support** : {q['channel']}")
    if q.get("examiner_role_fr"):
        add(f"- **Rôle joué par l'examinateur** : {q['examiner_role_fr']}")
    if task.get("examiner_behavior"):
        add(f"- **Comportement examinateur prévu** : {task['examiner_behavior']}")
    add("")

    # ---- Question ----
    add("## Sujet présenté au candidat")
    add("")
    add("> " + q["question"].replace("\n", "\n> "))
    add("")
    if q.get("themes"):
        add(f"**Thèmes couverts** : {', '.join(q['themes'])}")
        add("")

    # ---- Structure ----
    add("## Structure attendue de la réponse")
    for i, s in enumerate(er["structure"], 1):
        add(f"{i}. {s}")
    add("")

    # ---- Required elements ----
    add("## Éléments à couvrir (vérification obligatoire)")
    add("Coche un élément seulement s'il est traité **explicitement** dans la production.")
    add("")
    for el in er["key_elements_to_cover"]:
        add(f"- [ ] {el}")
    add("")

    # ---- Lexicon & grammar ----
    add("## Lexique clé attendu")
    if er.get("key_vocabulary"):
        add(", ".join(f"`{v}`" for v in er["key_vocabulary"]))
    else:
        add("_(non spécifié)_")
    add("")

    add("## Structures grammaticales clés attendues")
    if er.get("key_grammar"):
        for g in er["key_grammar"]:
            add(f"- {g}")
    else:
        add("_(non spécifié)_")
    add("")

    # ---- Reference answers ----
    add("## Modèle A — réponse de référence")
    if er.get("reference_answer_word_count"):
        add(f"_Longueur : {er['reference_answer_word_count']} mots_")
        add("")
    add("```")
    add(er["reference_answer"])
    add("```")
    add("")

    if er.get("alternative_answer"):
        add("## Modèle B — alternative valable")
        if er.get("alternative_answer_word_count"):
            add(f"_Longueur : {er['alternative_answer_word_count']} mots_")
            add("")
        add("```")
        add(er["alternative_answer"])
        add("```")
        add("")

    add(
        "> Les modèles ci-dessus illustrent une production de niveau B2 réussie. "
        "**Ne pénalise pas** une production qui s'en éloigne tant qu'elle reste "
        "pertinente, structurée, et linguistiquement comparable."
    )
    add("")

    # ---- Examiner focus ----
    add("## Points d'attention spécifiques pour cette question")
    for f in q["evaluation_focus"]:
        add(f"- {f}")
    add("")

    # ---- Detailed rubric ----
    add("## Rubrique de notation détaillée")
    add(
        "Évalue chaque dimension applicable. Pour chaque dimension, situe la production "
        "sur l'échelle CECRL (A1 → C2) en t'appuyant sur :"
    )
    add("1. Le **repère B2** spécifique à cette tâche (ce qui est attendu pour valider B2).")
    add("2. Les **erreurs typiques sous le B2** signalées pour cette tâche.")
    add("3. Les **descripteurs génériques** de la dimension (rappel CECRL fourni).")
    add("")

    for dim_id in task.get("rubric_dimensions", []):
        dim_def = next(
            (d for d in data["grading_dimensions"] if d["id"] == dim_id), None
        )
        if not dim_def:
            continue
        add(f"### {dim_def['name_fr']} ({dim_def['name_en']})")
        add(f"_{dim_def['description']}_")
        if dim_def.get("weight_hint"):
            add(f"**Poids indicatif** : {dim_def['weight_hint']}")
        rub = (task.get("task_specific_rubric") or {}).get(dim_id, {})
        if rub:
            add("")
            add(f"- **Cible B2** : {rub.get('B2_target', '—')}")
            add(f"- **Sous le B2 (erreurs fréquentes)** : {rub.get('common_below_B2', '—')}")
        descs = (data.get("generic_level_descriptors") or {}).get(dim_id, {})
        if descs:
            add("")
            add("**Descripteurs CECRL pour cette dimension :**")
            add("")
            add("| Niveau | Descripteur |")
            add("| --- | --- |")
            for lvl, txt in descs.items():
                add(f"| **{lvl}** | {txt} |")
        add("")

    # ---- Scoring scale ----
    add("## Échelle de notation /20 et bandes CECRL")
    add(sc["evaluation_method"])
    add("")
    add("| Niveau CECRL | Score /20 |")
    add("| --- | --- |")
    for b in sc["level_bands"]:
        add(f"| {b['level']} | {b['score_min']}–{b['score_max']} |")
    add("")
    add(
        f"**Score sécurisé conseillé** : {sc['target_safe_score']}/20 — "
        f"{sc['target_safe_score_rationale']}"
    )
    add("")

    add("### Conditions d'échec automatique (à signaler en priorité)")
    for fc in sc["automatic_failure_conditions"]:
        add(f"- {fc}")
    add("")

    # ---- Strategy / pitfalls (helpful context) ----
    add("## Conseils stratégiques associés à la tâche")
    for tip in task.get("strategy_tips", []):
        add(f"- {tip}")
    add("")

    add("## Pièges fréquents à détecter")
    for p in task.get("common_pitfalls", []):
        add(f"- {p}")
    add("")

    # ---- Output format ----
    add("## Format de sortie attendu")
    add(
        "Réponds **uniquement** avec un objet JSON respectant le schéma ci-dessous. "
        "Pas de texte avant ni après. Cite des extraits courts du candidat dans `evidence` "
        "pour justifier chaque score."
    )
    add("")
    add("```json")
    add("{")
    add('  "question_id": "' + q["id"] + '",')
    add('  "overall_score_20": 0,')
    add('  "estimated_cefr_level": "A1|A2|B1|B2|C1|C2",')
    add('  "word_count_observed": 0,')
    add('  "within_word_limits": true,')
    add('  "automatic_failure": false,')
    add('  "automatic_failure_reasons": [],')
    add('  "dimensions": {')
    dims = task.get("rubric_dimensions", [])
    for i, dim_id in enumerate(dims):
        comma = "," if i < len(dims) - 1 else ""
        add(
            f'    "{dim_id}": {{ "score_20": 0, "level": "B2", '
            f'"justification": "", "evidence": [] }}{comma}'
        )
    add("  },")
    add('  "elements_covered": [],')
    add('  "elements_missing": [],')
    add('  "structure_followed": true,')
    add('  "structure_comments": "",')
    add('  "vocabulary": {')
    add('    "expected_used": [],')
    add('    "expected_missing": [],')
    add('    "notable_extras": []')
    add("  },")
    add('  "grammar_observations": [],')
    add('  "errors": [')
    add('    { "type": "lex|gram|orth|cohérence|registre|phonologie", '
        '"excerpt": "", "correction": "", "severity": "low|med|high" }')
    add("  ],")
    add('  "strengths": [],')
    add('  "improvement_advice_fr": []')
    add("}")
    add("```")
    add("")

    # ---- Grading instructions ----
    add("## Procédure de notation")
    add("1. **Compte les mots** de la production avant tout. Pour l'écrit, vérifie la fourchette officielle ; en deçà du minimum, applique une sanction lourde sur _Réalisation de la tâche_.")
    add("2. **Vérifie chaque élément** de la liste « Éléments à couvrir » et marque-le présent uniquement s'il est traité explicitement (pas seulement effleuré).")
    add("3. **Évalue chaque dimension** de la rubrique : situe la production sur l'échelle CECRL en t'appuyant sur le repère B2 de la tâche **et** sur les descripteurs génériques. Donne un score /20 par dimension et **justifie avec au moins une citation** tirée du texte candidat.")
    add("4. **Calcule le score global** comme moyenne pondérée des dimensions (en respectant les `weight_hint` quand fournis), arrondi à l'entier le plus proche.")
    add("5. **Sois bienveillant mais exigeant** : ne donne pas un B2 si la production reste majoritairement B1 ; ne sanctionne pas une production B2 sur de petites maladresses isolées.")
    add("6. **Vérifie les conditions d'échec automatique** ; si l'une est rencontrée, mets `automatic_failure: true` et explique.")
    add("7. **Rédige tous les retours en français** et reste constructif (les conseils doivent être actionnables pour un apprenant).")
    add("")

    add("---")
    add("")
    add("## Production du candidat à évaluer")
    add("")
    add("```")
    add("<<INSÉRER ICI LA RÉPONSE DU CANDIDAT>>")
    add("```")
    add("")

    return "\n".join(L)


# ----------------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/question_bank.json")
def serve_data():
    return send_from_directory(BASE_DIR, "question_bank.json")


@app.route("/api/grader/<question_id>")
def grader_prompt(question_id: str):
    data = load_data()
    q = next((x for x in data["questions"] if x["id"] == question_id), None)
    if not q:
        abort(404, description=f"question {question_id} not found")
    md = build_grader_markdown(q, data)
    return jsonify({"id": question_id, "markdown": md})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
