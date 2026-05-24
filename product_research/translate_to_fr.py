"""One-shot translator: turn English-language *values* in question_bank.json
into French.

Keeps all keys/IDs/level codes (A1..C2) and proper nouns intact. Run once:
    .venv/bin/python translate_to_fr.py

Reads question_bank.json, writes back in place. A backup is at
question_bank.json.bak (created manually before running this script).
"""
import json
from pathlib import Path

DATA = Path(__file__).parent / "question_bank.json"

data = json.loads(DATA.read_text(encoding="utf-8"))

# -------------------------------------------------------------------
# Metadata
# -------------------------------------------------------------------
data["metadata"]["scope"] = "Expression orale et expression écrite uniquement"

# -------------------------------------------------------------------
# Sections
# -------------------------------------------------------------------
SECTION_FORMATS = {
    "expression_orale": "Entretien en face-à-face avec un examinateur ; la production est enregistrée.",
    "expression_ecrite": "Trois courtes productions écrites réalisées sur ordinateur. Le candidat gère lui-même son temps dans les 30 minutes imparties.",
}
SECTION_NOTES = {
    "expression_orale": [
        "Aucun temps de préparation.",
        "L'examinateur peut interrompre une présentation apprise par cœur pour forcer une réponse plus spontanée.",
        "Lors de l'examen réel, les tâches 2 et 3 sont tirées d'un pool de 5 sujets chacune ; l'examinateur en choisit un.",
    ],
    "expression_ecrite": [
        "Le nombre de mots est strict et entre dans la notation.",
        "Le TCF IRN ne demande pas de longues dissertations de 150–180 mots. Le format est volontairement court.",
        "Hors-sujet, tâche manquante ou non-respect du nombre de mots peuvent faire basculer la section en « A1 non atteint ».",
    ],
}
for sec in data["sections"]:
    sec["format"] = SECTION_FORMATS[sec["id"]]
    sec["section_notes"] = SECTION_NOTES[sec["id"]]

# -------------------------------------------------------------------
# Tasks
# -------------------------------------------------------------------
TASKS = {
    "oral_task_1": {
        "objective": "Parler de soi, de sa situation et de sa vie quotidienne de manière personnelle, développée et spontanée (pas de discours appris par cœur).",
        "format": "Entretien dirigé : l'examinateur pose des questions et des relances.",
        "examiner_behavior": "Peut poser des questions de relance, demander des clarifications ou interrompre une présentation récitée.",
        "expected_response_word_count_rationale": "À ~95–115 mots/minute pour un candidat B2, 3 minutes de parole effective correspondent à environ 280–340 mots. La borne basse tient compte des relances de l'examinateur dans les 3 minutes.",
        "skills_assessed": [
            "Parler de soi spontanément",
            "Développer ses idées avec des détails personnels",
            "Répondre aux questions de relance",
            "Tenir un court échange conversationnel",
        ],
        "expected_structure": [
            "Ouverture directe et personnelle qui répond à la question",
            "Deux ou trois détails concrets (faits, exemples, raisons)",
            "Une nuance, un contraste ou un ressenti personnel",
            "Une clôture qui ouvre vers une relance (projet, souhait, situation actuelle)",
        ],
        "required_elements": [
            "Rester personnel et concret (pas de bio récitée)",
            "Donner au moins 3 informations spécifiques",
            "Utiliser au moins 2 temps verbaux différents (présent + passé ou présent + futur)",
            "Inclure des connecteurs (par exemple, en effet, par contre, donc)",
        ],
        "strategy_tips": [
            "Traiter le sujet comme une amorce de conversation, pas comme un discours.",
            "Utiliser « parce que », « par exemple », « en fait » pour développer chaque idée.",
            "Rester attentif aux relances et y répondre directement, sans repartir dans son script.",
        ],
        "common_pitfalls": [
            "Réciter une présentation de soi apprise par cœur.",
            "Énumérer des faits sans les développer.",
            "Parler trop brièvement et attendre la question suivante.",
            "Sortir du sujet pour recycler du contenu pré-préparé.",
        ],
    },
    "oral_task_2": {
        "objective": "Négocier, poser des questions précises, expliquer ses besoins, comparer des options et réagir aux réponses de l'examinateur dans une situation de la vie courante.",
        "format": "Jeu de rôle : l'examinateur joue un rôle défini (agent, vendeur, secrétaire). Le candidat doit obtenir des informations, expliquer ses besoins et réagir.",
        "examiner_behavior": "Joue le rôle indiqué dans le sujet ; fournit des informations auxquelles il faut réagir ; peut ajouter des complications.",
        "expected_response_word_count_rationale": "3 min 30 d'interaction orale. Inclut les tours de l'examinateur, donc le candidat produit ~250–330 mots répartis sur plusieurs échanges.",
        "skills_assessed": [
            "Ouvrir et clore une interaction poliment",
            "Poser des questions précises",
            "Expliquer des besoins, des préférences et des contraintes",
            "Comparer et hiérarchiser des options",
            "Reformuler quand on ne comprend pas",
            "Réagir aux réponses de l'interlocuteur",
        ],
        "expected_structure": [
            "Ouverture (salutation + énoncé du besoin)",
            "Description de la situation (contexte, contraintes, préférences)",
            "Deux à quatre questions précises",
            "Réaction aux réponses (comparaison, préférence, reformulation)",
            "Conclusion (décision, prochaine étape, remerciements, formule de clôture)",
        ],
        "required_elements": [
            "Au moins 3 questions précises, pas seulement des oui/non",
            "Contraintes explicites (budget, temps, lieu, préférences)",
            "Comparaison ou hiérarchie entre les options",
            "Une conclusion claire (option choisie, prochaine étape, formule de clôture polie)",
        ],
        "strategy_tips": [
            "Ouvrir par une salutation et une phrase qui énonce le besoin.",
            "Annoncer ses contraintes tôt pour que l'examinateur puisse donner des informations ciblées.",
            "Écouter activement ; reformuler avant de décider.",
            "Toujours terminer par une conclusion claire ou une prochaine étape.",
        ],
        "common_pitfalls": [
            "Faire un monologue au lieu d'interagir.",
            "Poser uniquement des questions oui/non.",
            "Ne pas énoncer ses contraintes, et se voir proposer des options non pertinentes.",
            "Ne jamais conclure l'échange.",
        ],
    },
    "oral_task_3": {
        "objective": "Exprimer une opinion claire, la défendre avec des arguments et des exemples, la nuancer, puis conclure.",
        "format": "Monologue suivi : le candidat énonce et défend une position sur un sujet familier.",
        "examiner_behavior": "Écoute ; peut poser une ou deux questions de relance à la fin si le temps le permet.",
        "expected_response_word_count_rationale": "3 min 30 de parole essentiellement continue. ~95–120 mots/minute → 330–420 mots pour un candidat B2 fluide.",
        "skills_assessed": [
            "Énoncer une position claire",
            "Développer des arguments avec un raisonnement",
            "Illustrer par des exemples",
            "Introduire une nuance ou une concession",
            "Conclure de manière convaincante",
        ],
        "expected_structure": [
            "Brève introduction qui reformule la question",
            "Énoncé clair de l'opinion",
            "Premier argument + exemple",
            "Deuxième argument + exemple",
            "Nuance, concession ou contre-argument",
            "Courte conclusion",
        ],
        "required_elements": [
            "Position explicite (pas seulement « ça dépend »)",
            "Au moins 2 arguments distincts",
            "Au moins 1 exemple concret",
            "Une nuance ou une concession (« cependant », « malgré tout », « il est vrai que »)",
            "Une courte conclusion",
        ],
        "strategy_tips": [
            "Choisir un camp rapidement même si on voit les deux côtés. La nuance vient ensuite.",
            "Préparer deux arguments distincts avant d'attaquer le second (ne pas redire le premier autrement).",
            "Ancrer chaque argument dans un exemple concret du quotidien.",
            "Utiliser les connecteurs comme jalons sonores : « d'abord », « ensuite », « par exemple », « cependant », « pour conclure ».",
        ],
        "common_pitfalls": [
            "Éviter de prendre position avec « ça dépend ».",
            "Deux arguments qui sont en réalité le même.",
            "Exemples trop abstraits ou hypothétiques.",
            "Pas de conclusion : le discours s'arrête en cours quand le temps est écoulé.",
        ],
    },
    "written_task_1": {
        "objective": "Produire un message descriptif court et précis qui répond à chaque élément demandé dans le sujet, dans un registre adapté au destinataire.",
        "format": "Répondre à un court message d'un ami ou d'un contact. Décrire une personne, un lieu, un objet ou un service.",
        "expected_response_word_count_rationale": "Format court officiel : 30 à 60 mots. Le respect strict de la fourchette est explicitement noté.",
        "skills_assessed": [
            "Répondre à un message court",
            "Décrire avec précision et concision",
            "Adapter le registre au destinataire",
            "Couvrir tous les descripteurs demandés",
        ],
        "expected_structure": [
            "Salutation adressée au contact nommé",
            "Mention directe de ce qui est décrit",
            "2 à 3 attributs concrets (tirés de la liste à puces du sujet)",
            "Une courte recommandation ou conclusion personnelle",
            "Formule de clôture",
        ],
        "required_elements": [
            "S'adresser explicitement au destinataire nommé",
            "Couvrir CHAQUE descripteur mentionné dans le sujet (par ex. âge, profession, caractère, centres d'intérêt)",
            "Rester dans 30–60 mots",
            "Utiliser un registre amical et informel (tu) sauf indication contraire du sujet",
            "Signer",
        ],
        "strategy_tips": [
            "Souligner chaque descripteur dans le sujet et les cocher au fur et à mesure de la rédaction.",
            "Écrire un brouillon, puis resserrer jusqu'à entrer dans 30–60 mots.",
            "Faire des phrases courtes et claires ; la précision prime sur la sophistication.",
        ],
        "common_pitfalls": [
            "Oublier un descripteur de la liste à puces.",
            "Écrire moins de 30 mots (pénalité automatique).",
            "Écrire plus de 60 mots et perdre le focus.",
            "Confondre le registre (vous formel alors que le sujet désigne un ami).",
        ],
    },
    "written_task_2": {
        "objective": "Raconter une courte histoire au passé, avec une chronologie claire, des détails concrets et une réaction personnelle.",
        "format": "Répondre à un court message d'un ami. Raconter une expérience récente ou un événement de la vie quotidienne.",
        "expected_response_word_count_rationale": "Format officiel : 40 à 90 mots. Permet une trame courte avec chronologie, détail et réaction.",
        "skills_assessed": [
            "Raconter au passé",
            "Organiser des événements en chronologie",
            "Donner un détail concret",
            "Exprimer une réaction personnelle",
        ],
        "expected_structure": [
            "Salutation et brève mise en contexte",
            "Repère temporel (la semaine dernière, hier, il y a quelques jours)",
            "Suite d'événements en ordre chronologique (au début, ensuite, finalement)",
            "Un détail concret ou une anecdote",
            "Réaction personnelle, ressenti ou conséquence",
            "Formule de clôture",
        ],
        "required_elements": [
            "Utiliser le passé (passé composé + imparfait)",
            "Au moins un repère temporel explicite",
            "Au moins 3 événements ordonnés",
            "Une réaction personnelle ou une conséquence",
            "Rester dans 40–90 mots",
        ],
        "strategy_tips": [
            "Choisir un événement réel (ou réaliste) facile à décrire ; le sujet importe moins que la structure.",
            "Utiliser « au début / ensuite / finalement » pour rendre la chronologie évidente.",
            "Choisir un détail vivant et écarter les autres.",
            "Terminer sur un ressenti ou un enseignement.",
        ],
        "common_pitfalls": [
            "Tout au passé composé sans imparfait (ou l'inverse).",
            "Pas de repères temporels, donc l'ordre des événements n'est pas clair.",
            "Trop d'événements listés superficiellement.",
            "Aucune réaction personnelle à la fin.",
        ],
    },
    "written_task_3": {
        "objective": "Énoncer une opinion claire, la justifier par deux arguments et un exemple ou une concession, dans un registre adapté à un forum public.",
        "format": "Publier un court texte d'opinion sur un forum, un blog ou un site communautaire à propos d'un sujet familier.",
        "expected_response_word_count_rationale": "Format officiel : 40 à 90 mots. Permet position + 2 arguments + nuance + clôture.",
        "skills_assessed": [
            "Énoncer une opinion claire",
            "Justifier avec deux arguments distincts",
            "Donner un exemple ou une concession",
            "Adapter le registre à un forum public",
        ],
        "expected_structure": [
            "Ouverture qui annonce la position",
            "Premier argument avec une raison",
            "Deuxième argument avec un exemple",
            "Une concession ou une nuance",
            "Brève clôture",
        ],
        "required_elements": [
            "Position explicite dès la première phrase",
            "Deux justifications distinctes",
            "Un exemple concret OU une concession",
            "Connecteurs argumentatifs (« d'abord », « ensuite », « cependant », « par exemple », « donc »)",
            "Rester dans 40–90 mots",
        ],
        "strategy_tips": [
            "Décider sa position avant d'écrire le premier mot.",
            "Préparer deux arguments réellement différents (pas deux formulations du même point).",
            "Si on nuance, le faire en une phrase près de la fin, pas tout au long.",
            "Viser le haut de la fourchette (75–90 mots) pour démontrer du développement.",
        ],
        "common_pitfalls": [
            "Ouverture évasive qui masque la position.",
            "Répétition d'un argument sous deux formes.",
            "Concession qui se transforme en seconde opinion contradictoire.",
            "Écrire comme s'il s'agissait d'un message privé au lieu d'un forum public.",
        ],
    },
}

for sec in data["sections"]:
    for t in sec["tasks"]:
        if t["id"] not in TASKS:
            continue
        tr = TASKS[t["id"]]
        for k, v in tr.items():
            if k in t:
                t[k] = v
            elif v:
                t[k] = v

# -------------------------------------------------------------------
# Task-specific rubrics
# -------------------------------------------------------------------
RUBRICS = {
    "oral_task_1": {
        "task_realization": {
            "B2_target": "Répond de manière personnelle et concrète ; donne 3+ informations ; développe avec des raisons ou des exemples ; réagit naturellement aux relances.",
            "common_below_B2": "Présentation récitée, énumération sans développement, réponses très brèves qui obligent l'examinateur à meubler.",
        },
        "coherence_structure": {
            "B2_target": "Idées reliées par des connecteurs appropriés ; progression claire de la réponse principale au détail puis à la nuance.",
            "common_below_B2": "Phrases déconnectées ; uniquement « et » et « mais » comme connecteurs.",
        },
        "sociolinguistic_appropriateness": {
            "B2_target": "Ton poli avec l'examinateur, ni trop familier ni trop formel ; usage naturel du « vous ».",
            "common_below_B2": "Confusion entre tu/vous ; absence de formules de politesse.",
        },
        "lexicon": {
            "B2_target": "Vocabulaire varié sur la vie personnelle, le travail, les loisirs ; capable de paraphraser un mot manquant.",
            "common_below_B2": "Forte répétition de « bien », « beaucoup », « choses ».",
        },
        "morphosyntax": {
            "B2_target": "Présent, passé composé, imparfait, futur proche/simple, conditionnel disponibles ; subordonnées avec « parce que », « quand », « si ».",
            "common_below_B2": "Uniquement le présent ; erreurs d'accord qui bloquent le sens.",
        },
        "phonology": {
            "B2_target": "Prononciation claire et intelligible ; l'accent ne perturbe pas la compréhension.",
            "common_below_B2": "Prononciations erronées ou hésitations qui forcent l'examinateur à faire répéter.",
        },
    },
    "oral_task_2": {
        "task_realization": {
            "B2_target": "Explique ses besoins clairement, pose 3+ questions précises, compare des options, réagit aux réponses, conclut l'échange.",
            "common_below_B2": "Besoins vagues, uniquement des questions oui/non, pas de réaction aux réponses de l'examinateur, pas de conclusion.",
        },
        "coherence_structure": {
            "B2_target": "Enchaînement logique du besoin aux questions, à la comparaison puis à la décision ; les transitions semblent naturelles.",
            "common_below_B2": "Questions dans un ordre aléatoire ; pas de lien visible entre les tours de parole.",
        },
        "sociolinguistic_appropriateness": {
            "B2_target": "Formules polies adaptées à un échange client/professionnel (Bonjour, je voudrais, est-ce que vous pourriez, merci, au revoir).",
            "common_below_B2": "Demandes directes sans politesse ; familiarité inappropriée.",
        },
        "lexicon": {
            "B2_target": "Vocabulaire spécifique à la situation (logement, formation, voyage, soin, mobilité) ; descripteurs et quantifieurs précis.",
            "common_below_B2": "Vocabulaire générique inadapté à la situation.",
        },
        "morphosyntax": {
            "B2_target": "Conditionnel de politesse (« je voudrais », « pourriez-vous »), structures interrogatives (inversion ou « est-ce que »), structures de comparaison.",
            "common_below_B2": "Uniquement des phrases déclaratives avec une intonation montante en guise de questions.",
        },
        "phonology": {
            "B2_target": "L'intonation soutient la fonction de chaque tour de parole (question, demande, conclusion).",
            "common_below_B2": "Débit monotone qui ne permet pas de distinguer une question d'une affirmation.",
        },
    },
    "oral_task_3": {
        "task_realization": {
            "B2_target": "Opinion claire, 2 arguments distincts, au moins 1 exemple, une nuance, une conclusion.",
            "common_below_B2": "Position jamais énoncée ; arguments qui se confondent ; pas de nuance ; fin abrupte.",
        },
        "coherence_structure": {
            "B2_target": "Plan audible avec des connecteurs qui jalonnent chaque étape (introduction, arguments, nuance, conclusion).",
            "common_below_B2": "Flot d'opinions sans plan visible.",
        },
        "sociolinguistic_appropriateness": {
            "B2_target": "Modalisateurs polis (« à mon avis », « selon moi », « il me semble que ») et ton respectueux même sur des sujets sensibles.",
            "common_below_B2": "Affirmations catégoriques sans modalisation ; ton trop agressif ou trop hésitant.",
        },
        "lexicon": {
            "B2_target": "Vocabulaire spécifique au sujet (santé, environnement, numérique, éducation) et connecteurs argumentatifs.",
            "common_below_B2": "Répétitions de « bien », « mauvais », « bon » ; peu de mots spécifiques au sujet.",
        },
        "morphosyntax": {
            "B2_target": "Subjonctif après « il faut que », « bien que » ; conditionnel pour les opinions ; phrases complexes.",
            "common_below_B2": "Uniquement des phrases simples ; subjonctif absent là où il est attendu.",
        },
        "phonology": {
            "B2_target": "L'intonation structure l'argumentation ; emphase claire sur les mots-clés.",
            "common_below_B2": "Débit monotone ; les arguments-clés ne sont pas mis en valeur vocalement.",
        },
    },
    "written_task_1": {
        "task_realization": {
            "B2_target": "Chaque descripteur du sujet est couvert par une information concrète ; nombre de mots respecté ; destinataire nommé.",
            "common_below_B2": "Un ou plusieurs descripteurs manquants ; hors fourchette de mots ; description vague.",
        },
        "coherence_structure": {
            "B2_target": "Salutation → sujet → attributs → recommandation → clôture, fluide en moins de 50 mots.",
            "common_below_B2": "Format en liste ; pas de salutation ou pas de clôture.",
        },
        "sociolinguistic_appropriateness": {
            "B2_target": "Ton amical avec marqueurs informels appropriés (« Salut », « Coucou », « À bientôt »).",
            "common_below_B2": "Ton trop formel avec « Madame, Monsieur » pour un ami.",
        },
        "lexicon": {
            "B2_target": "Vocabulaire descriptif concret (adjectifs de caractère, de lieu, de fonction) ; éviter les mots vides.",
            "common_below_B2": "Répétitions de « bien », « sympa », « cool » sans précisions.",
        },
        "morphosyntax": {
            "B2_target": "Présent bien maîtrisé ; accords des adjectifs ; propositions relatives avec « qui », « que ».",
            "common_below_B2": "Erreurs d'accord répétées sur les adjectifs ; uniquement des phrases très simples.",
        },
        "orthography": {
            "B2_target": "Orthographe suffisante pour une lecture fluide ; ponctuation standard.",
            "common_below_B2": "Plusieurs fautes d'orthographe par phrase ; accents manquants qui changent le sens.",
        },
    },
    "written_task_2": {
        "task_realization": {
            "B2_target": "Court récit complet avec chronologie, détail concret et réaction personnelle ; destinataire nommé.",
            "common_below_B2": "Liste brute d'événements ; pas de détail ; pas de réaction ; hors-sujet.",
        },
        "coherence_structure": {
            "B2_target": "Les repères temporels structurent le récit ; les transitions entre événements sont fluides.",
            "common_below_B2": "Événements juxtaposés uniquement avec « et » ou « puis » ; chronologie peu claire.",
        },
        "sociolinguistic_appropriateness": {
            "B2_target": "Registre amical informel avec destinataire nommé ; formule de clôture adaptée.",
            "common_below_B2": "Registre inadapté ou ton impersonnel.",
        },
        "lexicon": {
            "B2_target": "Vocabulaire des sentiments, du domaine d'activité (travail, santé, culture, démarches administratives) ; quelques adjectifs évaluatifs.",
            "common_below_B2": "Verbes génériques (« faire », « aller ») et aucun vocabulaire descriptif.",
        },
        "morphosyntax": {
            "B2_target": "Emploi cohérent du passé composé pour les événements et de l'imparfait pour le contexte ; pronoms « y » / « en » si pertinents.",
            "common_below_B2": "Erreurs de temps qui obscurcissent la chronologie ; auxiliaires manquants.",
        },
        "orthography": {
            "B2_target": "Accords des participes passés majoritairement corrects ; ponctuation lisible.",
            "common_below_B2": "Erreurs répétées sur les participes passés qui obscurcissent le sens.",
        },
    },
    "written_task_3": {
        "task_realization": {
            "B2_target": "Position claire, 2 justifications distinctes, un exemple ou une concession, conclusion ; nombre de mots respecté.",
            "common_below_B2": "Position floue ; un seul argument ; hors fourchette de mots.",
        },
        "coherence_structure": {
            "B2_target": "Les connecteurs argumentatifs structurent le texte ; le lecteur identifie le plan d'un coup d'œil.",
            "common_below_B2": "Suite d'affirmations sans architecture argumentative visible.",
        },
        "sociolinguistic_appropriateness": {
            "B2_target": "Ton adapté à un forum public : tranché mais courtois, sans langage agressif ou offensant.",
            "common_below_B2": "Soit trop personnel/émotionnel, soit trop académique pour un contexte de forum.",
        },
        "lexicon": {
            "B2_target": "Vocabulaire pertinent au sujet, adjectifs évaluatifs, modalisateurs (« selon moi », « à mon avis », « il me semble »).",
            "common_below_B2": "Vocabulaire évaluatif vide ; répétition de « bon », « mauvais ».",
        },
        "morphosyntax": {
            "B2_target": "Subjonctif après les déclencheurs fréquents ; conditionnel pour l'opinion ; phrases complexes avec « bien que », « parce que », « si ».",
            "common_below_B2": "Uniquement des phrases simples ; subjonctif absent.",
        },
        "orthography": {
            "B2_target": "Orthographe suffisante ; accords respectés la plupart du temps.",
            "common_below_B2": "Plusieurs fautes par phrase ; accents manquants qui changent le sens.",
        },
    },
}
for sec in data["sections"]:
    for t in sec["tasks"]:
        if t["id"] in RUBRICS:
            for dim, fields in RUBRICS[t["id"]].items():
                t.setdefault("task_specific_rubric", {}).setdefault(dim, {}).update(fields)

# -------------------------------------------------------------------
# Grading dimensions
# -------------------------------------------------------------------
DIMENSIONS = {
    "task_realization": {
        "description": "Le candidat répond-il pleinement au sujet, reste-t-il dans le thème, respecte-t-il la situation et délivre-t-il tous les éléments explicitement ou implicitement requis ?",
        "weight_hint": "Priorité la plus haute. Une faible réalisation de la tâche plafonne la note globale, quelle que soit la qualité linguistique.",
    },
    "coherence_structure": {
        "description": "Les idées sont-elles organisées, enchaînées logiquement, reliées par des connecteurs appropriés et faciles à suivre du début à la fin ?",
    },
    "sociolinguistic_appropriateness": {
        "description": "Le registre est-il adapté à la situation, à l'interlocuteur et au support (entretien en face-à-face, message amical, forum public, etc.) ? Les marqueurs de politesse, salutations et formules de clôture sont-ils utilisés à bon escient ?",
    },
    "lexicon": {
        "description": "Le vocabulaire est-il varié, précis et adapté au sujet ? Les répétitions sont-elles limitées ? Le candidat sait-il paraphraser quand un mot lui manque ?",
    },
    "morphosyntax": {
        "description": "Les structures fréquentes du B2 sont-elles maîtrisées (temps, accords, prépositions, propositions relatives, subordination) ? Les erreurs sont-elles non bloquantes pour la compréhension ?",
    },
    "phonology": {
        "description": "La prononciation est-elle intelligible ? Le rythme, l'intonation et les liaisons soutiennent-ils le sens ? L'accent est-il non perturbant pour un auditeur non préparé ?",
    },
    "orthography": {
        "description": "L'orthographe et la ponctuation de base sont-elles suffisamment maîtrisées pour ne pas perturber la lecture ?",
    },
}
for d in data["grading_dimensions"]:
    if d["id"] in DIMENSIONS:
        d.update(DIMENSIONS[d["id"]])

# -------------------------------------------------------------------
# Generic level descriptors
# -------------------------------------------------------------------
DESCRIPTORS = {
    "task_realization": {
        "A1": "Réponse quasi inexistante, hors-sujet, ou si brève que la tâche n'est pas réalisée.",
        "A2": "Réponse partielle, plusieurs éléments requis manquants ou seulement effleurés.",
        "B1": "La plupart des éléments requis sont traités, mais certains sont faibles, manquants ou simplement listés sans développement.",
        "B2": "Tous les éléments requis sont traités clairement et avec un développement adéquat. Reste dans le sujet et respecte la situation tout du long.",
        "C1": "Éléments requis développés en profondeur avec des détails pertinents, anticipation des objections et adaptation fine à la situation.",
        "C2": "Tâche pleinement et habilement réalisée, avec des choix subtils et ciblés et une adaptation sans effort à la situation.",
    },
    "coherence_structure": {
        "A1": "Mots ou phrases juxtaposés sans lien visible.",
        "A2": "Phrases simples reliées par quelques connecteurs basiques (et, mais, parce que). L'ordre peut être confus.",
        "B1": "Enchaînement globalement cohérent avec des connecteurs simples. Quelques ruptures abruptes possibles.",
        "B2": "Progression claire avec des connecteurs appropriés (d'abord, ensuite, par contre, en effet, donc, par exemple, en conclusion). Facile à suivre.",
        "C1": "Discours bien structuré avec des connecteurs variés, paragraphes clairs ou jalons oraux, transitions fluides.",
        "C2": "Discours étroitement organisé avec des dispositifs de cohésion sophistiqués employés naturellement.",
    },
    "sociolinguistic_appropriateness": {
        "A1": "Registre inapproprié ou absent. Aucun marqueur de politesse.",
        "A2": "Politesse de base présente mais registre parfois inadapté.",
        "B1": "Registre globalement approprié mais quelques incohérences.",
        "B2": "Registre clairement adapté à l'interlocuteur et au support. Marqueurs de politesse, formules d'ouverture et de clôture correctement utilisés.",
        "C1": "Maîtrise assurée du registre, y compris des nuances et des changements de ton.",
        "C2": "Adaptation sociolinguistique pleinement naturelle, y compris l'humour ou le sens implicite quand il est pertinent.",
    },
    "lexicon": {
        "A1": "Vocabulaire très limité, lacunes fréquentes qui bloquent le sens.",
        "A2": "Vocabulaire de base suffisant pour des sujets prévisibles, mais nombreuses répétitions.",
        "B1": "Vocabulaire adéquat sur des sujets familiers, imprécisions occasionnelles mais le sens passe.",
        "B2": "Vocabulaire suffisamment étendu sur une grande variété de sujets. Répétitions limitées. Capable de paraphraser quand un mot manque. Quelques imprécisions subsistent mais ne bloquent jamais la compréhension.",
        "C1": "Vocabulaire large et précis avec des expressions idiomatiques et des termes spécifiques au sujet.",
        "C2": "Vocabulaire très large et précis, y compris expressions idiomatiques et familières utilisées à bon escient.",
    },
    "morphosyntax": {
        "A1": "Uniquement des fragments mémorisés. Les erreurs bloquent la compréhension.",
        "A2": "Structures simples. Erreurs fréquentes mais le sens passe souvent.",
        "B1": "Emploi raisonnablement correct des schémas fréquents. Erreurs lors de tentatives de structures plus complexes.",
        "B2": "Bonne maîtrise des structures B2 fréquentes (passés, conditionnel, subjonctif après déclencheurs courants, propositions relatives, phrases complexes). Des erreurs sont présentes mais non bloquantes.",
        "C1": "Maîtrise grammaticale élevée. Les erreurs sont rares et auto-corrigées.",
        "C2": "Maîtrise grammaticale constante d'une langue complexe, même en attention partagée.",
    },
    "phonology": {
        "A1": "Prononciation souvent inintelligible.",
        "A2": "Prononciation qui demande un effort pour être comprise.",
        "B1": "Prononciation globalement claire malgré un accent perceptible et des prononciations erronées occasionnelles.",
        "B2": "Prononciation claire et intelligible. L'accent peut être perceptible mais ne perturbe pas la compréhension. L'intonation soutient le sens.",
        "C1": "Intonation variée et articulation claire, influence très mineure de l'accent de la L1.",
        "C2": "Prononciation aussi facile à suivre que celle d'un locuteur natif, avec une maîtrise prosodique complète.",
    },
    "orthography": {
        "A1": "L'orthographe bloque souvent la lecture.",
        "A2": "Beaucoup d'erreurs orthographiques de base, mais les mots restent en grande partie reconnaissables.",
        "B1": "Orthographe globalement correcte sur les mots fréquents. Erreurs sur les accords et les terminaisons verbales.",
        "B2": "Orthographe et ponctuation suffisamment maîtrisées. Des erreurs subsistent (notamment sur les terminaisons verbales et les accords) mais ne bloquent jamais la lecture.",
        "C1": "Peu d'erreurs orthographiques, bonne maîtrise de la ponctuation.",
        "C2": "Pratiquement aucune erreur d'orthographe ou de ponctuation.",
    },
}
data["generic_level_descriptors"] = DESCRIPTORS

# -------------------------------------------------------------------
# Scoring
# -------------------------------------------------------------------
sc = data["scoring"]
sc["evaluation_method"] = (
    "Chaque production orale et écrite est corrigée indépendamment par deux "
    "examinateurs. Chaque examinateur attribue un niveau CECRL (A1 à C2) à "
    "chacune des trois tâches de la section. Une formule non publique combine "
    "les niveaux des tâches en un score final sur 20 et un niveau CECRL "
    "correspondant pour la section."
)
sc["target_safe_score_rationale"] = (
    "Viser au moins 12/20 sans qu'aucune tâche ne soit nettement en dessous du "
    "B2 sécurise le résultat B2 nécessaire pour la naturalisation (la zone B2 "
    "s'étend de 10 à 13/20 ; 12 laisse une marge face aux variations entre "
    "examinateurs)."
)
sc["automatic_failure_conditions"] = [
    "Nombre de mots non respecté (en particulier à l'écrit)",
    "Réponse hors-sujet",
    "Une tâche obligatoire est manquante",
    "La production est incomplète",
    "Ces conditions peuvent faire basculer le résultat de la section vers « A1 non atteint »",
]
sc["scoring_aggregation_for_app"] = {
    "per_dimension_score_range": [0, 20],
    "task_score_formula": "Moyenne de tous les scores de dimensions de la tâche, arrondie à 0,5.",
    "section_score_formula": "Moyenne pondérée des 3 scores de tâches (poids égaux par défaut raisonnable ; la formule officielle n'est pas publique).",
    "level_assignment": "Mapper le score final de la section vers une bande de niveau via level_bands.",
}

# -------------------------------------------------------------------
# Write back
# -------------------------------------------------------------------
DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("ok — wrote", DATA)
