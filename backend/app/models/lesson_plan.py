"""
Pydantic Models and Data Schemas for Milestone 2: Personalized Lesson Planning Engine.
Defines LearnerProfile, VisualSpec, CheckpointQuestion, LessonSegmentPlan, and LessonPlan.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator, model_validator


# -----------------------------------------------------------------------------
# Enums
# -----------------------------------------------------------------------------

class LearnerLevel(str, Enum):
    """Educational level of the learner dictating depth, vocabulary, and rigor."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class VisualType(str, Enum):
    """Subject-aware visual slide format rendered during lesson playback."""
    MATH_EQUATION = "math_equation"
    CODE_SNIPPET = "code_snippet"
    DIAGRAM = "diagram"
    TIMELINE = "timeline"
    COMPARISON_TABLE = "comparison_table"
    KEY_TAKEAWAYS = "key_takeaways"
    GENERAL_SLIDE = "general_slide"


class SegmentType(str, Enum):
    """Pedagogical role of a lesson segment in the teaching sequence."""
    AVATAR_INTRO = "avatar_intro"
    VISUAL_CONCEPT = "visual_concept"
    DEMONSTRATION = "demonstration"
    CHECKPOINT_QUESTION = "checkpoint_question"
    AVATAR_SUMMARY = "avatar_summary"


# -----------------------------------------------------------------------------
# Core Sub-Models
# -----------------------------------------------------------------------------

class LearnerProfile(BaseModel):
    """
    Profile capturing student background, target proficiency, time constraints,
    language preferences, and learning objectives.
    """
    student_id: str = Field(default="student_default", description="Unique identifier for the student")
    level: LearnerLevel = Field(default=LearnerLevel.BEGINNER, description="Learner comprehension tier")
    language: str = Field(default="en", description="Target teaching language (e.g., 'en', 'hi')")
    time_budget_min: int = Field(default=15, ge=1, le=180, description="Available lesson time budget in minutes")
    prior_knowledge: Optional[str] = Field(default=None, description="Prior background or prerequisite familiarity")
    learning_goal: Optional[str] = Field(default=None, description="Specific learning goal or objective")
    weak_concepts: List[str] = Field(default_factory=list, description="Historical weak areas needing reinforcement")
    preferred_visual_style: Optional[str] = Field(default=None, description="Preferred visual archetype")

    @field_validator("level", mode="before")
    @classmethod
    def parse_level(cls, v: Any) -> LearnerLevel:
        if isinstance(v, LearnerLevel):
            return v
        if isinstance(v, str):
            clean = v.strip().lower()
            if clean in ("beginner", "beg", "intro", "novice"):
                return LearnerLevel.BEGINNER
            elif clean in ("intermediate", "inter", "med", "medium"):
                return LearnerLevel.INTERMEDIATE
            elif clean in ("advanced", "adv", "expert", "master"):
                return LearnerLevel.ADVANCED
        return LearnerLevel.BEGINNER

    @field_validator("language", mode="before")
    @classmethod
    def clean_language(cls, v: Any) -> str:
        if isinstance(v, str) and v.strip():
            return v.strip().lower()
        return "en"


class VisualSpec(BaseModel):
    """
    Structured specification for rendering subject-aware visual slides (Math LaTeX formulas,
    syntax-highlighted code blocks, Mermaid diagrams, timelines, comparison tables).
    """
    visual_type: VisualType = Field(default=VisualType.KEY_TAKEAWAYS, description="Visual presentation format")
    subject_domain: str = Field(default="general", description="Subject area (math, computer_science, biology, history, physics, general)")
    headline: str = Field(..., description="Main headline or slide title")
    bullet_points: List[str] = Field(default_factory=list, description="Key explanatory bullet points or takeaways")
    code_content: Optional[str] = Field(default=None, description="Source code snippet for syntax highlighting")
    code_language: Optional[str] = Field(default=None, description="Programming language for snippet (python, javascript, c++, etc.)")
    latex_equations: List[str] = Field(default_factory=list, description="LaTeX formatted formulas or mathematical steps")
    diagram_mermaid: Optional[str] = Field(default=None, description="Mermaid diagram definition (flowchart, sequence, class, state)")
    timeline_events: Optional[List[Dict[str, str]]] = Field(
        default_factory=list,
        description="Chronological events list: [{'year'/'time': '...', 'event': '...', 'significance': '...'}]"
    )
    table_headers: Optional[List[str]] = Field(default_factory=list, description="Column headers for comparison tables")
    table_rows: Optional[List[List[str]]] = Field(default_factory=list, description="Data rows for comparison tables")
    callout_box: Optional[str] = Field(default=None, description="Highlighted warning, definition, or key rule callout")

    @field_validator("visual_type", mode="before")
    @classmethod
    def parse_visual_type(cls, v: Any) -> VisualType:
        if isinstance(v, VisualType):
            return v
        if isinstance(v, str):
            clean = v.strip().lower()
            for member in VisualType:
                if member.value == clean:
                    return member
            # Fuzzy mappings
            if "math" in clean or "latex" in clean or "equation" in clean:
                return VisualType.MATH_EQUATION
            elif "code" in clean or "syntax" in clean or "prog" in clean:
                return VisualType.CODE_SNIPPET
            elif "diag" in clean or "flow" in clean or "mermaid" in clean:
                return VisualType.DIAGRAM
            elif "time" in clean or "chrono" in clean or "history" in clean:
                return VisualType.TIMELINE
            elif "table" in clean or "compar" in clean:
                return VisualType.COMPARISON_TABLE
        return VisualType.KEY_TAKEAWAYS


class CheckpointQuestion(BaseModel):
    """
    Formative assessment question triggering an in-lesson interactive pause check.
    Supports bidirectional alignment between backend schema (question_text, question_type, correct_answer)
    and frontend schema (prompt, type, correct_option_index).
    """
    question_id: str = Field(..., description="Unique question identifier")
    question_text: Optional[str] = Field(default=None, description="Prompt or query presented to the student")
    prompt: Optional[str] = Field(default=None, description="Frontend alias for question text / prompt")
    question_type: Optional[str] = Field(default="mcq", description="Question format: 'mcq' or 'short_answer'")
    type: Optional[str] = Field(default="mcq", description="Frontend alias for question format: 'mcq' or 'short_answer'")
    options: List[str] = Field(default_factory=list, description="MCQ options if applicable (e.g. ['A) ...', 'B) ...'])")
    correct_answer: Optional[str] = Field(default=None, description="Correct answer text or option key")
    correct_option_index: Optional[int] = Field(default=None, description="0-indexed option index for frontend")
    explanation: str = Field(..., description="Pedagogical explanation of why the answer is correct")
    concept: str = Field(..., description="Specific concept or principle being tested")
    difficulty: str = Field(default="medium", description="Question difficulty: easy | medium | hard")
    misconception_distractors: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="Mapping of wrong answers to cognitive misconception diagnoses"
    )

    @model_validator(mode="before")
    @classmethod
    def sync_pre_validation(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # 1. Sync prompt <-> question_text
            prompt = data.get("prompt")
            q_text = data.get("question_text")
            if prompt and not q_text:
                data["question_text"] = prompt
            elif q_text and not prompt:
                data["prompt"] = q_text

            # 2. Sync type <-> question_type
            q_type = data.get("question_type")
            t = data.get("type")
            if t and not q_type:
                data["question_type"] = t
            elif q_type and not t:
                data["type"] = q_type

            # 3. Sync correct_option_index <-> correct_answer
            corr_idx = data.get("correct_option_index")
            corr_ans = data.get("correct_answer")
            options = data.get("options", [])
            if corr_idx is not None and not corr_ans and isinstance(options, list) and 0 <= corr_idx < len(options):
                data["correct_answer"] = options[corr_idx]
            elif corr_ans and corr_idx is None and isinstance(options, list) and len(options) > 0:
                for idx, opt in enumerate(options):
                    if str(corr_ans).strip().lower() in str(opt).strip().lower() or str(opt).strip().lower() in str(corr_ans).strip().lower():
                        data["correct_option_index"] = idx
                        break
                if data.get("correct_option_index") is None:
                    data["correct_option_index"] = 0
        return data

    @model_validator(mode="after")
    def sync_and_validate(self) -> "CheckpointQuestion":
        # 1. Sync prompt <-> question_text
        if self.prompt and not self.question_text:
            self.question_text = self.prompt
        elif self.question_text and not self.prompt:
            self.prompt = self.question_text

        # 2. Sync type <-> question_type
        if self.type and not self.question_type:
            self.question_type = self.type
        elif self.question_type and not self.type:
            self.type = self.question_type

        # 3. Sync correct_option_index <-> correct_answer
        if self.correct_option_index is not None and not self.correct_answer:
            if self.options and 0 <= self.correct_option_index < len(self.options):
                self.correct_answer = self.options[self.correct_option_index]
        elif self.correct_answer and self.correct_option_index is None and self.options:
            for idx, opt in enumerate(self.options):
                if str(self.correct_answer).strip().lower() in str(opt).strip().lower() or str(opt).strip().lower() in str(self.correct_answer).strip().lower():
                    self.correct_option_index = idx
                    break
            if self.correct_option_index is None and len(self.options) > 0:
                self.correct_option_index = 0

        # 4. Enforce non-empty required fields
        if not self.question_text or not self.question_text.strip():
            raise ValueError("question_text or prompt cannot be empty.")
        self.question_text = self.question_text.strip()
        self.prompt = self.question_text

        if not self.correct_answer or not self.correct_answer.strip():
            raise ValueError("correct_answer cannot be empty.")
        self.correct_answer = self.correct_answer.strip()

        if not self.concept or not self.concept.strip():
            raise ValueError("concept cannot be empty.")
        self.concept = self.concept.strip()

        return self


class LessonSegmentPlan(BaseModel):
    """
    Atomic pedagogical segment within a LessonPlan (Intro, Visual Slide, Demonstration, Checkpoint, Summary).
    """
    segment_id: str = Field(..., description="Unique segment identifier (e.g. 'seg_001')")
    order: int = Field(..., ge=1, description="1-indexed sequence order in the lesson flow")
    segment_type: SegmentType = Field(default=SegmentType.VISUAL_CONCEPT, description="Pedagogical role")
    title: str = Field(..., description="Segment title or section name")
    duration_sec: int = Field(..., ge=5, description="Planned duration of this segment in seconds")
    script: str = Field(..., description="Full spoken script for TTS audio narration in the target language")
    visual_spec: Optional[VisualSpec] = Field(default=None, description="Visual slide spec if segment_type is visual")
    checkpoint_question: Optional[CheckpointQuestion] = Field(
        default=None,
        description="Formative question if segment_type is checkpoint_question"
    )
    concept_id: Optional[str] = Field(default=None, description="Associated concept identifier")
    grounding_citations: List[str] = Field(
        default_factory=list,
        description="Document chunk or slide citations grounding this segment"
    )

    @field_validator("segment_type", mode="before")
    @classmethod
    def parse_segment_type(cls, v: Any) -> SegmentType:
        if isinstance(v, SegmentType):
            return v
        if isinstance(v, str):
            clean = v.strip().lower()
            for member in SegmentType:
                if member.value == clean:
                    return member
            if "intro" in clean:
                return SegmentType.AVATAR_INTRO
            elif "summary" in clean or "outro" in clean or "wrap" in clean:
                return SegmentType.AVATAR_SUMMARY
            elif "check" in clean or "question" in clean or "pause" in clean or "quiz" in clean:
                return SegmentType.CHECKPOINT_QUESTION
            elif "demo" in clean or "walkthrough" in clean:
                return SegmentType.DEMONSTRATION
        return SegmentType.VISUAL_CONCEPT


# -----------------------------------------------------------------------------
# Lesson Plan Models
# -----------------------------------------------------------------------------

class LessonPlan(BaseModel):
    """
    Complete structured lesson plan synthesized by the pedagogical planning engine.
    """
    plan_id: str = Field(..., description="Unique plan identifier (e.g. 'plan_abc123')")
    title: str = Field(..., description="Title of the lesson")
    target_duration_sec: int = Field(..., ge=60, description="Target total duration in seconds")
    level: LearnerLevel = Field(..., description="Learner educational level")
    language: str = Field(default="en", description="Teaching language")
    document_id: Optional[str] = Field(default=None, description="Associated uploaded document ID if grounded")
    topic_id: Optional[str] = Field(default=None, description="Associated parametric topic ID if grounded")
    topic: Optional[str] = Field(default=None, description="Topic name")
    subject_domain: str = Field(default="general", description="Subject area (math, computer_science, biology, history, physics, general)")
    learner_profile: Optional[LearnerProfile] = Field(default=None, description="Learner profile used to synthesize plan")
    modules: List[LessonSegmentPlan] = Field(default_factory=list, description="Ordered pedagogical segments")
    total_actual_duration_sec: int = Field(default=0, description="Sum of segment durations in seconds")
    prerequisite_refreshers: List[str] = Field(default_factory=list, description="Prerequisite concepts refreshed in intro")
    learning_objectives: List[str] = Field(default_factory=list, description="Key pedagogical learning objectives")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: Optional[str] = Field(default=None)

    @model_validator(mode="after")
    def calculate_durations(self) -> "LessonPlan":
        """Calculates total actual duration from segments and syncs order indices."""
        if self.modules:
            self.total_actual_duration_sec = sum(m.duration_sec for m in self.modules)
            # Ensure order is 1..N
            for idx, mod in enumerate(self.modules, start=1):
                mod.order = idx
        return self


# -----------------------------------------------------------------------------
# Request and Response Models
# -----------------------------------------------------------------------------

class LessonPlanCreateRequest(BaseModel):
    """Request payload to generate a personalized lesson plan."""
    document_id: Optional[str] = Field(default=None, description="Uploaded document ID to ground the lesson")
    topic_id: Optional[str] = Field(default=None, description="Ingested topic ID to ground the lesson")
    topic: Optional[str] = Field(default=None, description="Plain text topic name if not ingested previously")
    subject_domain: Optional[str] = Field(default=None, description="Explicit subject domain override (math, cs, etc.)")
    learner_profile: Optional[LearnerProfile] = Field(
        default_factory=LearnerProfile,
        description="Student profile configuring depth, language, and duration"
    )
    custom_instructions: Optional[str] = Field(default=None, description="Custom teacher instructions or focus areas")

    @model_validator(mode="after")
    def check_at_least_one_source(self) -> "LessonPlanCreateRequest":
        if not self.document_id and not self.topic_id and not self.topic:
            raise ValueError("At least one of 'document_id', 'topic_id', or 'topic' must be provided.")
        return self


class LessonPlanUpdateRequest(BaseModel):
    """Request payload to update, reorder, or edit an existing lesson plan."""
    title: Optional[str] = Field(default=None, description="Updated lesson title")
    modules: Optional[List[LessonSegmentPlan]] = Field(default=None, description="Updated list of modules/segments")
    level: Optional[LearnerLevel] = Field(default=None, description="Updated learner level")
    learning_objectives: Optional[List[str]] = Field(default=None, description="Updated learning objectives")
    reorder_segment_ids: Optional[List[str]] = Field(
        default=None,
        description="List of segment_ids in new desired sequence order"
    )
    target_duration_sec: Optional[int] = Field(default=None, ge=60, description="Updated target duration in seconds")


class LessonPlanSummary(BaseModel):
    """Compact summary of a generated lesson plan for list views."""
    plan_id: str
    title: str
    level: str
    language: str
    target_duration_sec: int
    total_actual_duration_sec: int
    segment_count: int
    checkpoint_count: int
    created_at: str
    document_id: Optional[str] = None
    topic_id: Optional[str] = None
    subject_domain: str = "general"
