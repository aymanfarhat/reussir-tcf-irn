# Business Rules

This document describes product and exam behavior that the app must preserve. It complements `docs/ARCHITECTURE.md`, which describes implementation structure.

## Product Purpose

The app helps learners practice TCF IRN French production tasks in realistic, timed conditions. It is not a generic language tutoring product. The core experience is:

1. Start a simulation or targeted practice task.
2. Answer one prompt at a time under task constraints.
3. Submit the response.
4. Receive structured feedback, a score estimate, examples, and an improved version of the learner's own response.
5. Review final reports and history.

## Source Of Truth

The seed source of product behavior is `product_research/question_bank.json`.

Important research references:

- `product_research/EXAM_STRUCTURE.md`
- `product_research/QUESTION_BANK_GUIDANCE.md`
- `product_research/question_bank.json`
- `product_research/app.py`

The Django app should use database rows imported from the question bank rather than hard-coding task metadata in views and templates.

Do not edit research files unless explicitly requested. Production backend work should happen under `backend/`; user-facing frontend work should happen under `frontend/`.

## Current Exam Scope

The product currently focuses on:

- `expression_orale`
- `expression_ecrite`

The current bank targets B2-oriented practice and contains:

- 60 questions total
- 10 questions per task number
- task numbers 1-3 for oral production
- task numbers 4-6 for written production

Do not expand the product into comprehension, long essays, or long speeches unless the source data and product scope are intentionally expanded.

## Exam Structure

### Oral Section

Total oral section duration: about 10 minutes.

Tasks:

- Task 1: presentation / personal questions, about 3 minutes
- Task 2: situational interaction / role play, about 3.5 minutes
- Task 3: opinion / point of view, about 3.5 minutes

Preparation time is 0 minutes.

Oral assessment dimensions include:

- task realization
- coherence
- sociolinguistic appropriateness
- lexicon
- morphosyntax
- phonology

In the current implementation, main oral grading is transcript-based. Direct audio delivery feedback is optional and format-limited.

### Written Section

Total written section duration: about 30 minutes.

Tasks:

- Task 4: short descriptive message, suggested 7 minutes, 30-60 words
- Task 5: short narrative / personal experience, suggested 9 minutes, 40-90 words
- Task 6: short opinion text, suggested 12 minutes, 40-90 words

Preparation time is 0 minutes.

Written assessment dimensions include:

- task realization
- coherence
- sociolinguistic appropriateness
- lexicon
- morphosyntax
- orthography

Written word limits are strict. The app must count words, display the count, store the observed count, and pass limit compliance to grading.

## Simulation Selection Rules

Question selection must preserve official task sequence.

Simulation modes:

- `oral`: select one random active question each for task 1, task 2, and task 3
- `written`: select one random active question each for task 4, task 5, and task 6
- `full`: select one random active question each for tasks 1, 2, 3, 4, 5, and 6

Targeted practice:

- Select one active question.
- Optionally filter by task number.
- Optionally filter by theme.
- Save it as a `practice` session so grading, reports, task feedback, and history remain consistent with simulations.

Each session must preserve:

- selected question ids
- task sequence
- timing metadata
- word limits or oral target ranges
- candidate answer or transcript
- audio upload path when present
- grading output and secondary feedback artifacts

## Navigation Rules

Users must be authenticated to use the app beyond signup and login.

Session ownership is mandatory:

- users can only view, submit, retry, report, or delete their own sessions
- cross-user report, feedback, and delete attempts must be blocked

Simulation task navigation is sequential:

- users start at task order 1
- later task pages cannot be opened until previous task attempts are submitted or graded
- a graded or failed task redirects to its task feedback page
- final report becomes useful when all selected attempts are submitted and graded or failed

## Timing Rules

Each task has a server-side deadline computed when the task starts.

The UI must show a live countdown, but the server remains the source of truth for late submission:

- `started_at` marks when the task page starts
- `deadline_at` marks expected completion
- `submitted_late` is computed at submission time

The current app flags late submissions but does not block submission outright. Grading receives the late flag.

## Submission Rules

### Written Submission

Written attempts must save:

- answer text
- observed word count
- word-limit compliance flag
- submission timestamp
- late flag

The user should see live word count and the task's min/max boundaries.

### Oral Submission

Oral attempts may include:

- browser recording upload
- manual transcript
- generated transcript through OpenAI transcription

Priority order:

1. If a manual transcript is provided, use it as the candidate text.
2. Else if an audio file is uploaded and an API key is configured, transcribe it.
3. Else save an empty or unavailable transcript and grade accordingly.

Browser recordings are currently `audio/webm`. They can be uploaded and transcribed, but direct audio delivery feedback is only attempted for `wav` and `mp3`.

### Oral Question Playback

Oral task pages may provide a play button that reads the question aloud as AI-generated examiner audio.

Rules:

- playback is available only for oral tasks
- users must still read the visible prompt; audio is a convenience, not the source of truth
- the playback endpoint must require authentication and session ownership
- generated prompt audio may be cached and reused because it contains no learner data
- cached audio must regenerate when the question text, TTS model, voice, format, or speech instructions change

## Grading Rules

Main grading must follow the dynamic prompt strategy originally explored in `product_research/app.py`.

For each question, the grader prompt must include:

- exam and section context
- task number and type
- exact candidate prompt
- timing and word constraints
- expected structure
- required elements to cover
- expected vocabulary and grammar
- reference answer and alternative answer when present
- evaluation focus
- rubric dimensions
- level descriptors
- score bands
- automatic failure conditions
- candidate production

Reference answers are examples, not canonical answers. The grader must not require the learner to match them.

Main grading output is structured JSON, stored on `TaskGrade.parsed_result`.

Required grading output concepts:

- question id
- overall score out of 20
- estimated CEFR level
- observed word count
- word-limit compliance
- automatic failure flag and reasons
- dimension scores with dimension ids, levels, justifications, and evidence
- elements covered and missing
- structure feedback
- vocabulary feedback
- grammar observations
- errors with severity and corrections
- strengths
- actionable improvement advice in French

OpenAI structured-output compatibility rule:

- `dimensions` must remain a list of objects, each with `dimension_id`.
- Do not model dimensions as an arbitrary-key dictionary, because strict structured outputs reject that schema.

## Improved Response Rules

After main grading succeeds, the app runs a separate improved-response call.

The improved response must:

- rewrite the learner's own response in stronger French
- preserve the learner's intent and personal facts where possible
- respect the original task, addressee, register, and constraints
- avoid copying the reference answer
- avoid inventing major new facts
- target a clear B2-level response

The improved response output must include:

- improved French response
- what changed
- reusable phrases
- focus points for the next attempt

Improved-response failure must not fail the main grade. Store the error and show it on the feedback page if needed.

## Audio Feedback Rules

Direct audio delivery feedback is optional and separate from main grading.

Main oral grade is transcript-based.

Audio feedback should evaluate only delivery signals:

- pronunciation
- intelligibility
- rhythm
- hesitation
- self-correction
- fluency
- transcript quality notes when relevant

Direct audio feedback is currently limited to uploaded `wav` or `mp3`.

For browser `webm` recordings:

- do not call OpenAI direct audio feedback with `format: opus`
- store a limitation message instead
- continue transcript-based grading normally

Audio-feedback failure must not fail the main grade.

## Scoring Rules

Official TCF IRN score aggregation is not public.

The app uses an approximation:

- each task receives an overall score out of 20
- section scores average task scores for that section
- averages are rounded to the nearest 0.5
- score bands map approximate scores to CEFR levels

The final report must make clear that scores are practice estimates and not official results.

## Feedback Page Rules

The task feedback page should help the learner understand both performance and next steps.

It should show:

- the original prompt
- the learner production
- score and estimated CEFR level
- strengths
- improvement advice
- dimension scores
- optional audio delivery feedback
- reference examples from the question bank
- improved version of the learner's own response
- highest previous score for the same exact prompt, if any
- regrade action after a task has a saved submitted answer, including retry after failed grading

Example responses should be labeled as study examples, not memorization targets.

## Final Report Rules

The final report should show:

- oral score and level when oral tasks exist
- written score and level when written tasks exist
- per-task status and score
- covered and missing required elements
- improvement advice
- optional oral delivery summary
- score approximation disclaimer

The report must be accessible later from history.

## History Rules

History must show previous sessions for the authenticated user only.

Each history item should provide:

- session date
- mode and status
- oral and written score summaries
- full report link
- per-task result links
- continue links for unfinished attempts
- delete button

Delete behavior:

- POST-only
- CSRF-protected
- user ownership checked
- deletes the session, attempts, grades, and saved oral audio files for that session
- must not allow deleting another user's session

## Admin Content Rules

All core content should be editable through Django Admin:

- exams
- sections
- task definitions
- questions
- grading dimensions
- level descriptors
- score bands
- test definitions and steps

Question authoring safeguards:

- section id must match the selected task definition
- task number must match the selected task definition
- expected response must include structure, reference answer, required elements, vocabulary, and grammar
- written tasks must have min/max word counts
- oral questions must have duration and evaluation focus notes
- duplicate or highly similar prompts should be blocked
- active/inactive flags control publishing
- generated grader prompt preview should be visible in admin

## Data Integrity Rules

Import must be idempotent unless `--replace-existing` is used.

Content rows should preserve raw source JSON so future migrations or debugging can compare database state with the original question bank.

Attempts should preserve selected question and task snapshots so historical results remain understandable if content is edited later.

Runtime files should not be committed:

- `backend/db.sqlite3`
- `backend/media/`
- `backend/.env`
- `backend/.venv/`

## Error Handling Rules

Main grade failure:

- store `TaskGrade.status = failed`
- store the error message
- mark attempt as `grading_failed`
- show retry action on task feedback page

Regrade behavior:

- use the already saved answer or transcript without allowing edits
- overwrite the existing `TaskGrade` for the attempt through the normal grading service
- update session score aggregates after the new grade is stored
- reject regrading for tasks that have not been submitted or have no saved production

Secondary feedback failure:

- do not fail the main grade
- store the secondary status and error
- show a warning or limitation in feedback

No API key:

- app should still run locally
- main grading uses a local stub
- improved response uses a local stub
- transcription and direct audio feedback are unavailable

## Testing Expectations

Add or update tests for changes to:

- question-bank import
- test definitions and sequence
- random selection and practice filters
- auth and ownership
- sequential navigation
- word counting
- oral transcription fallback
- grading schemas and prompt behavior
- improved response output
- audio feedback format handling
- scoring aggregation
- feedback and report rendering
- history links and deletion
- admin validation

Required local checks:

```bash
cd app
uv run python manage.py check
uv run python manage.py test
```
