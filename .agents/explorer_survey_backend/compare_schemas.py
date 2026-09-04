import sys
sys.path.insert(0, "/home/dev/Desktop/projects/AI-InnovationHackathon")

from backend.app.models.ingestion import DocumentMetadata, TopicIngestionResponse
from backend.app.models.lesson_plan import VisualSpec, CheckpointQuestion as PlannerCheckpointQuestion, LessonSegmentPlan, LessonPlan
from backend.app.models.video import VideoManifest, CheckpointPauseMarker
from backend.app.models.interaction import AnswerEvaluationResponse, TutorChatResponse, FollowUpQuestion
from backend.app.models.profile import QuizQuestion, Quiz, LearningReport, StudentProfile, TopicRecommendation

print("=== BACKEND MODEL FIELDS ===")

print("\n1. DocumentMetadata:")
print(list(DocumentMetadata.model_fields.keys()))

print("\n2. TopicIngestionResponse:")
print(list(TopicIngestionResponse.model_fields.keys()))

print("\n3. VisualSpec:")
print(list(VisualSpec.model_fields.keys()))

print("\n4. CheckpointQuestion (lesson_plan):")
print(list(PlannerCheckpointQuestion.model_fields.keys()))

print("\n5. LessonSegmentPlan:")
print(list(LessonSegmentPlan.model_fields.keys()))

print("\n6. LessonPlan:")
print(list(LessonPlan.model_fields.keys()))

print("\n7. VideoManifest:")
print(list(VideoManifest.model_fields.keys()))

print("\n8. AnswerEvaluationResponse:")
print(list(AnswerEvaluationResponse.model_fields.keys()))

print("\n9. TutorChatResponse:")
print(list(TutorChatResponse.model_fields.keys()))

print("\n10. QuizQuestion:")
print(list(QuizQuestion.model_fields.keys()))

print("\n11. Quiz:")
print(list(Quiz.model_fields.keys()))

print("\n12. LearningReport:")
print(list(LearningReport.model_fields.keys()))

print("\n13. StudentProfile:")
print(list(StudentProfile.model_fields.keys()))

print("\n14. TopicRecommendation:")
print(list(TopicRecommendation.model_fields.keys()))

