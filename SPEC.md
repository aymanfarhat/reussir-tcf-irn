# TCF IRN Practice Web App Specification

## 1. Purpose

Build a Django web app that helps students practice the TCF IRN French exam through realistic timed simulations. The app uses `product_research/question_bank.json` as the source of truth for exam structure, tasks, questions, expected responses, rubrics, CEFR descriptors, scoring bands, and prompt-building data.

The learner experience is:

1. Sign up or log in.
2. Start a full test, oral-only practice, or written-only practice.
3. Move through a randomized but exam-correct sequence of timed tasks.
4. Submit each task answer.
5. Get each answer graded by OpenAI after submission.
6. Finish with a saved report showing per-task feedback, section scores, CEFR estimates, and improvement advice.

The application is not a single-page app. It should be server-rendered with Django templates, TailwindCSS for styling, HTMX for server partials where useful, and AlpineJS for page-local behavior such as timers, word counts, and audio recording state.

## 2. Scope And Non-Goals

V1 includes:

- Built-in Django authentication: signup, login, logout, authenticated dashboard.
- Import of `product_research/question_bank.json` into queryable SQLite-backed Django models.
- Django Admin editing for all exam content and runtime data.
- Full simulations: oral tasks 1-3 followed by written tasks 4-6.
- Oral-only simulations: tasks 1-3.
- Written-only simulations: tasks 4-6.
- Random question selection with one active question per task definition.
- Sequential task navigation with server-side state guards.
- Timed written and oral task pages.
- Written answer entry with live word count and word limit indicators.
- Oral browser recording, audio upload, transcription, transcript review, and transcript-based grading.
- OpenAI grading after every task submission using Responses API Structured Outputs.
- Final report and user history.

V1 does not include:

- Payments, subscriptions, teams, teachers, or classrooms.
- Social login.
- Official certification claims.
- A native mobile app.
- A frontend SPA framework.
- Direct phonology grading from raw audio. V1 stores audio and transcripts, and grades oral responses from transcripts. Phonology feedback is labeled approximate until a later audio-aware grading feature is added.

## 3. Stack

Current stack:

- Python package manager: `uv`
- Web framework: Django 5.2
- Database: SQLite for local development
- Frontend: Django templates, TailwindCSS, HTMX, AlpineJS
- AI SDK: `openai` Python SDK
- Structured result validation: Pydantic
- Audio transcription: OpenAI audio transcriptions
- LLM grading: OpenAI Responses API with Structured Outputs

Planned dependencies in `app/pyproject.toml`:

- `django>=5.2.14`
- `openai`
- `pydantic`
- `python-dotenv` or `django-environ` for local env loading
- Optional later: `django-htmx`

Default environment variables:

- `OPENAI_API_KEY`: required for transcription and grading.
- `OPENAI_GRADING_MODEL`: defaults to `gpt-5.5`.
- `OPENAI_TRANSCRIPTION_MODEL`: defaults to `gpt-4o-mini-transcribe`.
- `OPENAI_TRANSCRIPTION_LANGUAGE`: defaults to `fr`.

OpenAI implementation should follow current OpenAI docs:

- Responses API with Structured Outputs.
- Python SDK Pydantic parsing, matching the style already used in `simple-cli/main.py`.
- Stable prompt prefixes where possible so repeated grading prompts can benefit from caching.

## 4. Source Data Rules

`product_research/question_bank.json` is the source of truth until content is imported and then maintained through Django Admin.

The source file currently contains:

- Metadata for the TCF IRN exam.
- Scoring bands from A1 through C2.
- Automatic failure conditions.
- App scoring approximation rules.
- Seven grading dimensions:
  - `task_realization`
  - `coherence_structure`
  - `sociolinguistic_appropriateness`
  - `lexicon`
  - `morphosyntax`
  - `phonology`
  - `orthography`
- Generic CEFR descriptors per dimension.
- Two sections:
  - `expression_orale`
  - `expression_ecrite`
- Six task definitions:
  - Task 1: Presentation / personal questions
  - Task 2: Interaction / role play
  - Task 3: Opinion / point of view
  - Task 4: Short descriptive message
  - Task 5: Short narrative / personal experience
  - Task 6: Short opinion text
- Sixty questions: ten per task definition.

The import should preserve source IDs such as `oral_task_1`, `written_task_3`, and `q001`. These IDs must remain visible in Django Admin and reports for traceability.

## 5. Exam Business Rules

### 5.1 Simulation Modes

Supported modes:

- `full`: tasks 1, 2, 3, 4, 5, 6.
- `oral`: tasks 1, 2, 3.
- `written`: tasks 4, 5, 6.

The app must never randomize task order. It randomizes the question within each task family, then presents tasks in the test definition sequence.

### 5.2 Timing

Timing comes from the imported task/question metadata.

Oral tasks:

- Task 1: 3 minutes.
- Task 2: 3.5 minutes.
- Task 3: 3.5 minutes.
- No preparation time.

Written tasks:

- Task 4: suggested 7 minutes, 30-60 words.
- Task 5: suggested 9 minutes, 40-90 words.
- Task 6: suggested 12 minutes, 40-90 words.
- The written section total is 30 minutes.

V1 enforcement:

- Every `TaskAttempt` stores `started_at`, `deadline_at`, and `submitted_at`.
- The frontend shows a live countdown using the server-provided deadline.
- The server is authoritative for expiry.
- If a user submits after `deadline_at`, the answer is accepted but marked `submitted_late=true`.
- Late submission is included in the grader prompt and final report.
- V1 should not silently discard typed work at timeout.

### 5.3 Word Counts

Written word counts are strict and must be stored.

Rules:

- Count words server-side on submit using a shared utility.
- Use the same utility in tests for consistency.
- The frontend word count is advisory and must match the server utility as closely as possible.
- `TaskAttempt.word_count_observed` stores the final count.
- `TaskAttempt.within_word_limits` stores whether the count is inside the expected range.
- Out-of-range answers are still submitted and graded, but this fact is included in the prompt and report.

### 5.4 Oral Tasks

V1 oral flow:

1. User starts the oral task page.
2. Timer starts from the server-side attempt start.
3. User records audio in the browser.
4. Browser uploads audio when the user stops recording or submits.
5. The server stores the audio file.
6. OpenAI transcription creates `transcript_text`.
7. The transcript is used as the candidate production for grading.
8. The report labels pronunciation/phonology feedback as approximate.

If recording fails, the page should allow manual transcript entry as a fallback with a clear `manual_transcript=true` flag.

### 5.5 Grading Timing

Grading runs after each task submission.

The task result page can show:

- Grading pending.
- Grading failed with retry option.
- Grading complete.

A final report is available only after all selected task attempts are submitted. If one or more grades are still pending, the final report shows partial status and refreshes via HTMX.

### 5.6 Scoring

The official TCF IRN aggregation formula is not public. The app uses the approximation in the source bank and must disclose this in reports.

Task score:

- Average applicable dimension scores.
- Round to 0.5.

Section score:

- Average the three task scores for a section.
- Round to 0.5.

Full test score:

- Store oral and written section scores separately.
- Show an overall practice summary, but do not present it as an official TCF score.

CEFR mapping:

- Use imported score bands from the source data:
  - A1: 0-3
  - A2: 4-6
  - B1: 7-9
  - B2: 10-13
  - C1: 14-17
  - C2: 18-20

Safe target:

- Highlight 12/20 as the recommended safer B2 practice target, matching the source data.

## 6. Django Architecture

Create three Django apps:

- `exams`: imported exam content, task definitions, questions, rubrics, score bands, and test definitions.
- `simulations`: user test sessions, selected questions, task attempts, navigation state, and reports.
- `grading`: prompt generation, OpenAI calls, transcription, structured grade persistence, and retry logs.

Keep request handlers thin. Put business logic in services:

- `exams.services.import_question_bank`
- `simulations.services.start_session`
- `simulations.services.navigation`
- `simulations.services.scoring`
- `grading.services.prompt_builder`
- `grading.services.openai_client`
- `grading.services.transcription`
- `grading.services.grade_attempt`

## 7. Data Model

### 7.1 Content Models

`Exam`

- `source_id`
- `name`
- `full_name`
- `issuing_organization`
- `version`
- `valid_from`
- `target_level`
- `scope`
- `language`
- `metadata`

`ExamSection`

- `exam`
- `source_id`
- `name_fr`
- `name_en`
- `sequence_order`
- `total_duration_minutes`
- `preparation_time_minutes`
- `format`
- `number_of_tasks`
- `section_notes`
- `is_active`
- `raw_source`

`GradingDimension`

- `source_id`
- `name_fr`
- `name_en`
- `description`
- `applies_to`
- `weight_hint`
- `is_active`
- `raw_source`

`LevelDescriptor`

- `dimension`
- `level`
- `description`

`ScoreBand`

- `exam`
- `level`
- `score_min`
- `score_max`
- `midpoint`

`TaskDefinition`

- `section`
- `source_id`
- `task_number`
- `name_fr`
- `name_en`
- `format`
- `objective`
- `duration_minutes`
- `suggested_duration_minutes`
- `preparation_time_minutes`
- `word_count_min`
- `word_count_max`
- `word_count_target`
- `expected_response_word_count_min`
- `expected_response_word_count_ideal`
- `expected_response_word_count_max`
- `expected_structure`
- `required_elements`
- `skills_assessed`
- `strategy_tips`
- `common_pitfalls`
- `common_topics`
- `examiner_behavior`
- `rubric_dimensions`
- `task_specific_rubric`
- `is_active`
- `raw_source`

`Question`

- `task_definition`
- `source_id`
- `section_source_id`
- `task_number`
- `task_type_fr`
- `prompt`
- `themes`
- `timing`
- `addressee`
- `register`
- `channel`
- `examiner_role_fr`
- `expected_response`
- `evaluation_focus`
- `is_active`
- `raw_source`

`TestDefinition`

- `source_id`: `full`, `oral`, `written`
- `name`
- `mode`
- `description`
- `is_active`

`TestDefinitionStep`

- `test_definition`
- `sequence_order`
- `task_definition`

`ImportRun`

- `source_path`
- `source_hash`
- `source_version`
- `started_at`
- `finished_at`
- `status`
- `created_counts`
- `updated_counts`
- `skipped_counts`
- `errors`
- `dry_run`
- `replace_existing`

### 7.2 Runtime Models

`TestSession`

- `uuid`
- `user`
- `test_definition`
- `mode`
- `status`: `draft`, `in_progress`, `submitted`, `grading`, `completed`, `abandoned`
- `started_at`
- `completed_at`
- `current_step_order`
- `random_seed`
- `oral_score`
- `oral_level`
- `written_score`
- `written_level`
- `summary`
- `metadata`

`TaskAttempt`

- `uuid`
- `test_session`
- `step`
- `question`
- `task_definition_snapshot`
- `question_snapshot`
- `sequence_order`
- `status`: `not_started`, `in_progress`, `submitted`, `grading`, `graded`, `grading_failed`
- `started_at`
- `deadline_at`
- `submitted_at`
- `submitted_late`
- `answer_text`
- `audio_file`
- `audio_mime_type`
- `transcript_text`
- `manual_transcript`
- `word_count_observed`
- `within_word_limits`
- `client_events`
- `metadata`

Snapshots are required so reports do not change when admins later edit question content.

`TaskGrade`

- `task_attempt`
- `status`: `pending`, `running`, `succeeded`, `failed`
- `prompt_version`
- `prompt_markdown`
- `candidate_input`
- `model`
- `response_id`
- `raw_response`
- `parsed_result`
- `overall_score_20`
- `estimated_cefr_level`
- `automatic_failure`
- `automatic_failure_reasons`
- `duration_ms`
- `token_usage`
- `error_message`
- `created_at`
- `updated_at`

## 8. Import Command

Command:

```bash
cd app
uv run python manage.py import_question_bank ../product_research/question_bank.json
```

Options:

- `--dry-run`: parse and report changes without writing content rows.
- `--replace-existing`: update existing imported rows even if they already exist.
- `--deactivate-missing`: mark previously imported content inactive if missing from source.

Default behavior:

- Create missing rows.
- Preserve existing rows by source ID.
- Do not overwrite admin-edited content unless `--replace-existing` is passed.
- Always preserve `raw_source` and source IDs.
- Create or update `ImportRun`.

Validation:

- Exactly two sections.
- Exactly six task definitions.
- Exactly sixty questions.
- Ten active questions per task number.
- Every question references an existing task definition.
- Every task rubric dimension references an existing grading dimension.
- Every written task has word count limits.
- Every oral task has duration.
- Every test definition has a contiguous sequence.

## 9. OpenAI Grading

### 9.1 Prompt Builder

The prompt builder should port the strategy from `product_research/app.py::build_grader_markdown` into Django.

For each task, the prompt includes:

- Exam metadata.
- Section context.
- Task context.
- Exact candidate question.
- Timing and word count requirements.
- Addressee, channel, register, and examiner role when present.
- Expected response structure.
- Required elements.
- Expected vocabulary and grammar.
- Reference answer and alternative answer.
- Warning that reference answers are examples, not canonical answers.
- Task-specific evaluation focus.
- Applicable rubric dimensions.
- Generic CEFR descriptors.
- Score bands.
- Automatic failure conditions.
- Task strategy tips and pitfalls.
- Candidate response.
- JSON-only output instruction.

Prompt versioning:

- Store prompt version, for example `grader-v1`.
- Store rendered prompt markdown on every `TaskGrade`.
- Future prompt changes increment the version.

### 9.2 Structured Output Schema

Use Pydantic models and OpenAI Structured Outputs.

Top-level result fields:

- `question_id`
- `overall_score_20`
- `estimated_cefr_level`
- `word_count_observed`
- `within_word_limits`
- `automatic_failure`
- `automatic_failure_reasons`
- `dimensions`
- `elements_covered`
- `elements_missing`
- `structure_followed`
- `structure_comments`
- `vocabulary`
- `grammar_observations`
- `errors`
- `strengths`
- `improvement_advice_fr`

Dimension result fields:

- `score_20`
- `level`
- `justification`
- `evidence`

Error fields:

- `type`: `lex`, `gram`, `orth`, `coherence`, `registre`, `phonologie`, or `other`
- `excerpt`
- `correction`
- `severity`: `low`, `med`, `high`

The app must validate the parsed result before saving it as successful.

### 9.3 Transcription

Use OpenAI audio transcription for oral tasks.

Transcription prompt:

```text
Transcribe the French answer exactly as spoken. Preserve hesitations when meaningful, but do not translate.
```

Store:

- audio file
- transcription model
- transcript text
- transcription response metadata when available
- transcription errors

### 9.4 Error Handling

If OpenAI grading fails:

- Store `TaskGrade.status=failed`.
- Store the error message.
- Keep the user answer.
- Allow retry from task result page and Django Admin.
- Do not block the user from continuing the simulation.
- Final report clearly shows pending or failed grading states.

If transcription fails:

- Store the audio.
- Mark the attempt as transcription failed.
- Let the user enter or edit a manual transcript before grading.

## 10. UI Specification

### 10.1 Design Language

Use the design language from `product_research/index.html`:

- White header with subtle border.
- Light slate background.
- Compact cards with `rounded-lg`, thin borders, and restrained shadows.
- Section pills:
  - Oral: indigo.
  - Written: emerald.
- Level pills:
  - A1 red, A2 orange, B1 amber, B2 lime, C1 emerald, C2 teal.
- Dense, readable layouts designed for repeated practice.

Avoid marketing-style landing pages for the authenticated app. The dashboard should immediately show actions and recent simulations.

### 10.2 Pages

Unauthenticated:

- Landing page with concise product positioning and login/signup links.
- Signup page.
- Login page.

Authenticated:

- Dashboard:
  - Start full test.
  - Start oral practice.
  - Start written practice.
  - Recent attempts.
  - Last scores.
- Start confirmation:
  - Shows selected mode sequence and total estimated duration.
- Task page:
  - Shows sequence progress.
  - Shows timer.
  - Shows task metadata.
  - Shows prompt.
  - Provides answer UI.
- Task submitted / grading page:
  - Shows submitted answer or transcript.
  - Shows grading status.
  - Shows immediate feedback when available.
  - Continue button to next task.
- Final report:
  - Shows section scores and levels.
  - Shows per-task cards with feedback.
  - Shows strengths, missing elements, errors, and improvement advice.
  - Shows scoring approximation disclaimer.
- History:
  - Lists past simulations with mode, date, status, scores, and link to report.

### 10.3 Written Task UI

Written task page behavior:

- Countdown timer.
- Textarea.
- Live word count.
- Min/max/target word count indicator.
- Visual states:
  - under minimum
  - within range
  - over maximum
  - expired
- Submit remains available after expiry, but submission is marked late server-side.

### 10.4 Oral Task UI

Oral task page behavior:

- Countdown timer.
- Browser recording controls:
  - start
  - pause/stop
  - re-record before submit
  - playback preview
- Upload progress.
- Transcript area after transcription.
- Manual transcript fallback.
- Clear label that pronunciation scoring is approximate in V1.

## 11. Navigation And State

All task access is server-guarded.

Rules:

- A user can access only their own sessions.
- A task cannot be opened before prior tasks are submitted.
- A submitted task cannot be edited unless a future explicit retry feature is added.
- Back navigation to completed tasks shows read-only review.
- The next task is created or started only after the current task is submitted.
- A session is complete when all selected attempts are submitted.

HTMX can be used for:

- Polling grading status.
- Updating report grade cards.
- Retry grade button.

AlpineJS can be used for:

- Countdown timer.
- Word count.
- Audio recorder state.

## 12. Admin Requirements

Django Admin must expose:

- Exams
- Sections
- Task definitions
- Questions
- Grading dimensions
- Level descriptors
- Score bands
- Test definitions and steps
- Import runs
- Test sessions
- Task attempts
- Task grades

Admin must support:

- Search by source ID, question text, task name, user email/username.
- Filters by section, task number, active status, mode, session status, grade status, CEFR level.
- Inline steps for test definitions.
- Read-only raw source snapshots on runtime objects where appropriate.
- Admin retry action for failed grades.

## 13. Testing Strategy

Core tests:

- Import dry-run validates source file and writes nothing.
- Import creates two sections, six tasks, sixty questions, seven dimensions, score bands, and three test definitions.
- Import is idempotent.
- Import does not overwrite existing content without `--replace-existing`.
- Random simulation selection picks one active question per required task.
- Full simulation sequence is 1-6.
- Oral simulation sequence is 1-3.
- Written simulation sequence is 4-6.
- Users cannot access another user's session.
- Server rejects starting a task out of sequence.
- Late submissions are marked late.
- Written word count utility handles punctuation, newlines, and apostrophes consistently.
- Prompt builder includes required context and JSON-only output contract.
- OpenAI grading service can be tested with mocked structured output.
- Transcription service can be tested with mocked OpenAI responses.
- Final report aggregates scores and maps CEFR bands.

Frontend verification:

- Dashboard renders actions.
- Written task page word counter works.
- Timer displays deadline and expired state.
- Oral recorder controls render and fail gracefully when recording is unsupported.
- Report page handles complete, pending, and failed grades.

## 14. Rollout Strategy

Build in this order:

1. Documentation and dependencies.
2. Data schema and admin.
3. Import command.
4. Authentication and dashboard.
5. Simulation creation and navigation.
6. Written task flow.
7. Oral recording and transcription flow.
8. Prompt builder.
9. OpenAI grading.
10. Reports and history.
11. Polish and hardening.

Every feature should land with tests before moving to the next backlog ticket.
