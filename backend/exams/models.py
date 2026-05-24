from __future__ import annotations

from django.db import models


class Exam(models.Model):
    source_id = models.CharField(max_length=80, unique=True)
    name = models.CharField(max_length=120)
    full_name = models.CharField(max_length=255, blank=True)
    issuing_organization = models.CharField(max_length=180, blank=True)
    version = models.CharField(max_length=40, blank=True)
    valid_from = models.DateField(null=True, blank=True)
    target_level = models.CharField(max_length=20, blank=True)
    scope = models.CharField(max_length=255, blank=True)
    language = models.CharField(max_length=20, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class ExamSection(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="sections")
    source_id = models.CharField(max_length=80, unique=True)
    name_fr = models.CharField(max_length=120)
    name_en = models.CharField(max_length=120, blank=True)
    sequence_order = models.PositiveSmallIntegerField()
    total_duration_minutes = models.DecimalField(max_digits=5, decimal_places=1)
    preparation_time_minutes = models.DecimalField(
        max_digits=5, decimal_places=1, default=0
    )
    format = models.TextField(blank=True)
    number_of_tasks = models.PositiveSmallIntegerField(default=0)
    section_notes = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    raw_source = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sequence_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["exam", "sequence_order"], name="unique_section_order_per_exam"
            )
        ]

    def __str__(self) -> str:
        return self.name_fr


class GradingDimension(models.Model):
    source_id = models.CharField(max_length=80, unique=True)
    name_fr = models.CharField(max_length=120)
    name_en = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    applies_to = models.JSONField(default=list, blank=True)
    weight_hint = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    raw_source = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["source_id"]

    def __str__(self) -> str:
        return self.name_fr


class LevelDescriptor(models.Model):
    dimension = models.ForeignKey(
        GradingDimension, on_delete=models.CASCADE, related_name="level_descriptors"
    )
    level = models.CharField(max_length=10)
    description = models.TextField()

    class Meta:
        ordering = ["dimension__source_id", "level"]
        constraints = [
            models.UniqueConstraint(
                fields=["dimension", "level"], name="unique_descriptor_per_dimension"
            )
        ]

    def __str__(self) -> str:
        return f"{self.dimension.source_id} {self.level}"


class ScoreBand(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="score_bands")
    level = models.CharField(max_length=10)
    score_min = models.DecimalField(max_digits=4, decimal_places=1)
    score_max = models.DecimalField(max_digits=4, decimal_places=1)
    midpoint = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)

    class Meta:
        ordering = ["score_min"]
        constraints = [
            models.UniqueConstraint(fields=["exam", "level"], name="unique_score_band")
        ]

    def __str__(self) -> str:
        return f"{self.level} ({self.score_min}-{self.score_max})"


class TaskDefinition(models.Model):
    section = models.ForeignKey(
        ExamSection, on_delete=models.CASCADE, related_name="task_definitions"
    )
    source_id = models.CharField(max_length=80, unique=True)
    task_number = models.PositiveSmallIntegerField()
    name_fr = models.CharField(max_length=160)
    name_en = models.CharField(max_length=160, blank=True)
    format = models.TextField(blank=True)
    objective = models.TextField(blank=True)
    duration_minutes = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True
    )
    suggested_duration_minutes = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True
    )
    preparation_time_minutes = models.DecimalField(
        max_digits=5, decimal_places=1, default=0
    )
    word_count_min = models.PositiveSmallIntegerField(null=True, blank=True)
    word_count_max = models.PositiveSmallIntegerField(null=True, blank=True)
    word_count_target = models.PositiveSmallIntegerField(null=True, blank=True)
    expected_response_word_count_min = models.PositiveSmallIntegerField(
        null=True, blank=True
    )
    expected_response_word_count_ideal = models.PositiveSmallIntegerField(
        null=True, blank=True
    )
    expected_response_word_count_max = models.PositiveSmallIntegerField(
        null=True, blank=True
    )
    expected_structure = models.JSONField(default=list, blank=True)
    required_elements = models.JSONField(default=list, blank=True)
    skills_assessed = models.JSONField(default=list, blank=True)
    strategy_tips = models.JSONField(default=list, blank=True)
    common_pitfalls = models.JSONField(default=list, blank=True)
    common_topics = models.JSONField(default=list, blank=True)
    examiner_behavior = models.TextField(blank=True)
    rubric_dimensions = models.JSONField(default=list, blank=True)
    task_specific_rubric = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    raw_source = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["task_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["section", "task_number"], name="unique_task_number_per_section"
            )
        ]

    def __str__(self) -> str:
        return f"Task {self.task_number}: {self.name_fr}"

    @property
    def is_written(self) -> bool:
        return self.section.source_id == "expression_ecrite"

    @property
    def is_oral(self) -> bool:
        return self.section.source_id == "expression_orale"

    @property
    def duration_seconds(self) -> int:
        minutes = self.duration_minutes or self.suggested_duration_minutes or 0
        return int(float(minutes) * 60)


class Question(models.Model):
    task_definition = models.ForeignKey(
        TaskDefinition, on_delete=models.CASCADE, related_name="questions"
    )
    source_id = models.CharField(max_length=80, unique=True)
    section_source_id = models.CharField(max_length=80)
    task_number = models.PositiveSmallIntegerField()
    task_type_fr = models.CharField(max_length=160)
    prompt = models.TextField()
    themes = models.JSONField(default=list, blank=True)
    timing = models.JSONField(default=dict, blank=True)
    addressee = models.CharField(max_length=120, blank=True)
    register = models.CharField(max_length=160, blank=True)
    channel = models.CharField(max_length=160, blank=True)
    examiner_role_fr = models.CharField(max_length=160, blank=True)
    expected_response = models.JSONField(default=dict, blank=True)
    evaluation_focus = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    raw_source = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["task_number", "source_id"]
        indexes = [
            models.Index(fields=["section_source_id", "task_number", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.source_id}: {self.prompt[:80]}"


class TestDefinition(models.Model):
    MODE_FULL = "full"
    MODE_ORAL = "oral"
    MODE_WRITTEN = "written"
    MODE_CHOICES = [
        (MODE_FULL, "Full"),
        (MODE_ORAL, "Oral"),
        (MODE_WRITTEN, "Written"),
    ]

    source_id = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=120)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["source_id"]

    def __str__(self) -> str:
        return self.name


class TestDefinitionStep(models.Model):
    test_definition = models.ForeignKey(
        TestDefinition, on_delete=models.CASCADE, related_name="steps"
    )
    sequence_order = models.PositiveSmallIntegerField()
    task_definition = models.ForeignKey(
        TaskDefinition, on_delete=models.PROTECT, related_name="test_steps"
    )

    class Meta:
        ordering = ["test_definition__source_id", "sequence_order"]
        constraints = [
            models.UniqueConstraint(
                fields=["test_definition", "sequence_order"],
                name="unique_step_order_per_test_definition",
            ),
            models.UniqueConstraint(
                fields=["test_definition", "task_definition"],
                name="unique_task_per_test_definition",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.test_definition.source_id} step {self.sequence_order}"


class ImportRun(models.Model):
    STATUS_RUNNING = "running"
    STATUS_SUCCEEDED = "succeeded"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_RUNNING, "Running"),
        (STATUS_SUCCEEDED, "Succeeded"),
        (STATUS_FAILED, "Failed"),
    ]

    source_path = models.CharField(max_length=500)
    source_hash = models.CharField(max_length=128, blank=True)
    source_version = models.CharField(max_length=40, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_RUNNING
    )
    created_counts = models.JSONField(default=dict, blank=True)
    updated_counts = models.JSONField(default=dict, blank=True)
    skipped_counts = models.JSONField(default=dict, blank=True)
    errors = models.JSONField(default=list, blank=True)
    dry_run = models.BooleanField(default=False)
    replace_existing = models.BooleanField(default=False)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"{self.source_path} ({self.status})"
