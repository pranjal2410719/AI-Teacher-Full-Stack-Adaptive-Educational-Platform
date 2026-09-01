"""
Pydantic Models Package for AI Teacher.
"""

from backend.app.models.ingestion import (
    DocumentMetadata,
    DocumentChunk,
    TopicIngestionRequest,
    TopicIngestionResponse,
    RAGQuery,
    ChunkMatch,
    RAGResponse,
)

from backend.app.models.lesson_plan import (
    LearnerLevel,
    VisualType,
    SegmentType,
    LearnerProfile,
    VisualSpec,
    CheckpointQuestion,
    LessonSegmentPlan,
    LessonPlan,
    LessonPlanCreateRequest,
    LessonPlanUpdateRequest,
    LessonPlanSummary,
)

from backend.app.models.video import (
    VideoResolution,
    VideoStage,
    VideoGenerationRequest,
    VideoGenerationTaskResponse,
    VideoGenerationStatus,
    VideoSegmentMeta,
    VideoChapter,
    CheckpointPauseMarker,
    VideoManifest,
)

from backend.app.models.interaction import (
    FollowUpQuestion,
    AnswerEvaluationRequest,
    AnswerEvaluationResponse,
    LanguageSwitchRequest,
    LanguageSwitchResponse,
    TutorChatRequest,
    TutorChatResponse,
    InteractionSessionState,
)

from backend.app.models.profile import (
    QuizQuestion,
    QuizGenerationRequest,
    Quiz,
    QuizSubmissionRequest,
    TopicRecommendation,
    LearningReport,
    StudentProfile,
    StudentProfileUpdateRequest,
)

__all__ = [
    "DocumentMetadata",
    "DocumentChunk",
    "TopicIngestionRequest",
    "TopicIngestionResponse",
    "RAGQuery",
    "ChunkMatch",
    "RAGResponse",
    "LearnerLevel",
    "VisualType",
    "SegmentType",
    "LearnerProfile",
    "VisualSpec",
    "CheckpointQuestion",
    "LessonSegmentPlan",
    "LessonPlan",
    "LessonPlanCreateRequest",
    "LessonPlanUpdateRequest",
    "LessonPlanSummary",
    "VideoResolution",
    "VideoStage",
    "VideoGenerationRequest",
    "VideoGenerationTaskResponse",
    "VideoGenerationStatus",
    "VideoSegmentMeta",
    "VideoChapter",
    "CheckpointPauseMarker",
    "VideoManifest",
    "FollowUpQuestion",
    "AnswerEvaluationRequest",
    "AnswerEvaluationResponse",
    "LanguageSwitchRequest",
    "LanguageSwitchResponse",
    "TutorChatRequest",
    "TutorChatResponse",
    "InteractionSessionState",
    "QuizQuestion",
    "QuizGenerationRequest",
    "Quiz",
    "QuizSubmissionRequest",
    "TopicRecommendation",
    "LearningReport",
    "StudentProfile",
    "StudentProfileUpdateRequest",
]
