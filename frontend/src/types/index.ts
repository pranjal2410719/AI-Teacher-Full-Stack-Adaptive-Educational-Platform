export type LearnerLevel = 'beginner' | 'intermediate' | 'advanced';
export type LanguageCode = 'en' | 'hi';

export interface LearnerProfile {
  student_id: string;
  name: string;
  preferred_language: LanguageCode;
  preferred_level: LearnerLevel;
  total_lessons_completed: number;
  average_mastery_percent: number;
  concept_mastery: Record<string, number>;
  known_weak_areas: string[];
  weak_areas?: string[];
  learning_history: Array<{
    lesson_id: string;
    score: number;
    strong_concepts?: string[];
    weak_concepts?: string[];
    date: string;
  }>;
  completed_lessons: string[];
  total_time_spent_min: number;
}

export interface DocumentMetadata {
  document_id: string;
  filename: string;
  file_type: string;
  file_size_bytes?: number;
  total_pages: number;
  chunk_count: number;
  extracted_summary: string;
  status: string;
}

export interface TopicIngestionResponse {
  topic_id: string;
  topic: string;
  subject_category: string;
  seed_summary: string;
  generated_chunks_count: number;
  status: string;
}

export interface VisualSpec {
  visual_type: 'math_equation' | 'code_snippet' | 'diagram' | 'timeline' | 'general_slide';
  subject_domain: string;
  headline: string;
  bullet_points: string[];
  code_content?: string | null;
  code_language?: string | null;
  latex_equations?: string[];
  diagram_mermaid?: string | null;
  timeline_events?: Array<{ year_or_date: string; title: string; description: string }> | null;
}

export interface CheckpointQuestion {
  question_id: string;
  pause_timestamp_sec?: number;
  type: 'mcq' | 'short_answer';
  prompt: string;
  options?: string[] | null;
  correct_option_index?: number | null;
  explanation?: string | null;
}

export interface LessonSegmentPlan {
  segment_id: string;
  order: number;
  segment_type: 'avatar_intro' | 'visual_concept' | 'demonstration' | 'checkpoint_question' | 'avatar_summary';
  title: string;
  duration_sec: number;
  script: string;
  visual_spec: VisualSpec;
  checkpoint_question?: CheckpointQuestion | null;
}

export interface LessonPlan {
  plan_id: string;
  title: string;
  target_duration_sec: number;
  level: LearnerLevel;
  language: string;
  document_id?: string;
  topic_id?: string;
  topic?: string;
  subject_domain?: string;
  modules: LessonSegmentPlan[];
  total_actual_duration_sec?: number;
  prerequisite_refreshers?: string[];
  learning_objectives?: string[];
  created_at?: string;
  updated_at?: string;
}

export interface VideoManifest {
  lesson_id: string;
  plan_id: string;
  video_url: string;
  total_duration_sec: number;
  language: string;
  chapters: Array<{
    title: string;
    start_sec: number;
    end_sec: number;
    type: string;
  }>;
  pause_markers: Array<{
    marker_id: string;
    timestamp_sec: number;
    question: CheckpointQuestion;
  }>;
}

export interface AnswerEvaluationResponse {
  is_correct: boolean;
  score: number;
  feedback: string;
  misconception?: string | null;
  misconception_detected?: string | null;
  pedagogical_re_explanation?: string | null;
  re_explanation?: string | null;
  follow_up_question?: {
    question_id: string;
    type: string;
    prompt: string;
    hint?: string | null;
  } | null;
  can_resume_video: boolean;
  detected_language: string;
}

export interface TutorChatResponse {
  session_id: string;
  reply: string;
  language: string;
  suggested_actions: string[];
  grounded_sources: string[];
}

export interface QuizQuestion {
  question_id: string;
  type: 'mcq' | 'short_answer';
  prompt: string;
  options?: string[] | null;
  correct_option_index?: number | null;
  concept: string;
  points: number;
  explanation?: string | null;
}

export interface Quiz {
  quiz_id: string;
  lesson_id: string;
  student_id: string;
  title: string;
  questions: QuizQuestion[];
  total_points: number;
}

export interface LearningReport {
  submission_id: string;
  quiz_id: string;
  student_id: string;
  lesson_id: string;
  score_percent: number;
  total_points_earned: number;
  total_points_possible: number;
  strong_concepts: string[];
  weak_concepts: string[];
  misconceptions_resolved: string[];
  recommended_revision?: string | null;
  recommended_next_topics: Array<{
    topic: string;
    level: string;
    rationale?: string;
  }>;
  learning_report_summary: string;
}

export interface TopicRecommendation {
  topic: string;
  level: string;
  rationale?: string;
  prerequisite_concepts: string[];
}
