from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator


class DimensionGrade(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dimension_id: str
    score_20: float
    level: Literal["A1", "A2", "B1", "B2", "C1", "C2"]
    justification: str
    evidence: list[str]

    @field_validator("score_20")
    @classmethod
    def score_must_be_out_of_20(cls, value: float) -> float:
        if not 0 <= value <= 20:
            raise ValueError("score_20 must be between 0 and 20")
        return value


class VocabularyFeedback(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_used: list[str]
    expected_missing: list[str]
    notable_extras: list[str]


class GradingError(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["lex", "gram", "orth", "coherence", "registre", "phonologie", "other"]
    excerpt: str
    correction: str
    severity: Literal["low", "med", "high"]


class GradingResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_id: str
    overall_score_20: float
    estimated_cefr_level: Literal["A1", "A2", "B1", "B2", "C1", "C2"]
    word_count_observed: int
    within_word_limits: bool
    automatic_failure: bool
    automatic_failure_reasons: list[str]
    dimensions: list[DimensionGrade]
    elements_covered: list[str]
    elements_missing: list[str]
    structure_followed: bool
    structure_comments: str
    vocabulary: VocabularyFeedback
    grammar_observations: list[str]
    errors: list[GradingError]
    strengths: list[str]
    improvement_advice_fr: list[str]

    @field_validator("overall_score_20")
    @classmethod
    def overall_score_must_be_out_of_20(cls, value: float) -> float:
        if not 0 <= value <= 20:
            raise ValueError("overall_score_20 must be between 0 and 20")
        return value

    @field_validator("word_count_observed")
    @classmethod
    def word_count_must_be_positive(cls, value: int) -> int:
        if value < 0:
            raise ValueError("word_count_observed must be positive")
        return value


class ImprovedResponseResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    improved_response_fr: str
    changes_made: list[str]
    reusable_phrases: list[str]
    focus_next_time: list[str]
