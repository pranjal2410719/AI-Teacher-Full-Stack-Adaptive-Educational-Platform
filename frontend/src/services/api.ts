import {
  DocumentMetadata,
  TopicIngestionResponse,
  LearnerProfile,
  LessonPlan,
  VideoManifest,
  AnswerEvaluationResponse,
  TutorChatResponse,
  Quiz,
  LearningReport,
  TopicRecommendation,
} from '../types';

const API_BASE = '/api/v1';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const errorText = await res.text();
    let errorMessage = `HTTP Error ${res.status}: ${res.statusText}`;
    try {
      const errJson = JSON.parse(errorText);
      if (errJson.detail) errorMessage = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
    } catch {
      if (errorText) errorMessage = errorText;
    }
    throw new Error(errorMessage);
  }
  return res.json() as Promise<T>;
}

export const api = {
  // Ingestion
  async uploadDocument(file: File): Promise<DocumentMetadata> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/materials/upload`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse<DocumentMetadata>(res);
  },

  async ingestTopic(topic: string, subjectCategory: string = 'General'): Promise<TopicIngestionResponse> {
    const res = await fetch(`${API_BASE}/materials/topic`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic, subject_category: subjectCategory }),
    });
    return handleResponse<TopicIngestionResponse>(res);
  },

  // Lesson Planning
  async createLessonPlan(payload: {
    learner_profile: {
      student_id?: string;
      level: string;
      language: string;
      time_budget_min: number;
      prior_knowledge?: string;
      learning_goal?: string;
    };
    document_id?: string;
    topic_id?: string;
    topic?: string;
    subject_domain?: string;
    custom_instructions?: string;
  }): Promise<LessonPlan> {
    const res = await fetch(`${API_BASE}/lessons/plan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<LessonPlan>(res);
  },

  async getLessonPlan(planId: string): Promise<LessonPlan> {
    const res = await fetch(`${API_BASE}/lessons/${planId}`);
    return handleResponse<LessonPlan>(res);
  },

  async updateLessonPlan(planId: string, updatedPlan: Partial<LessonPlan>): Promise<LessonPlan> {
    const res = await fetch(`${API_BASE}/lessons/${planId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updatedPlan),
    });
    return handleResponse<LessonPlan>(res);
  },

  // Video Pipeline
  async generateVideo(planId: string, voicePreference?: string): Promise<{ task_id: string; plan_id: string; status: string; websocket_stream_url?: string }> {
    const res = await fetch(`${API_BASE}/lessons/generate-video`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ plan_id: planId, voice_preference: voicePreference }),
    });
    return handleResponse<{ task_id: string; plan_id: string; status: string; websocket_stream_url?: string }>(res);
  },

  async getVideoStatus(taskId: string): Promise<{
    task_id: string;
    status: string;
    progress_percent: number;
    current_stage: string;
    stages_completed: string[];
    video_url?: string;
    manifest_url?: string;
    error_message?: string;
  }> {
    const res = await fetch(`${API_BASE}/lessons/video-status/${taskId}`);
    return handleResponse(res);
  },

  async getVideoManifest(lessonId: string): Promise<VideoManifest> {
    const res = await fetch(`${API_BASE}/lessons/video-manifest/${lessonId}`);
    return handleResponse<VideoManifest>(res);
  },

  // Interactive Loop
  async evaluateAnswer(payload: {
    session_id: string;
    question_id: string;
    student_answer: string;
    current_concept?: string;
    language?: string;
  }): Promise<AnswerEvaluationResponse> {
    const res = await fetch(`${API_BASE}/interactive/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<AnswerEvaluationResponse>(res);
  },

  async switchLanguage(sessionId: string, targetLanguage: string): Promise<{
    session_id: string;
    language: string;
    translated_summary: string;
    next_prompt: string;
  }> {
    const res = await fetch(`${API_BASE}/interactive/switch-language`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, target_language: targetLanguage }),
    });
    return handleResponse(res);
  },

  async tutorChat(payload: {
    message: string;
    session_id?: string;
    current_timestamp_sec?: number;
    document_id?: string;
    topic_id?: string;
  }): Promise<TutorChatResponse> {
    const res = await fetch(`${API_BASE}/interactive/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<TutorChatResponse>(res);
  },

  // Assessment & Profile
  async generateQuiz(lessonId: string, studentId: string = 'stu_default', numQuestions: number = 3): Promise<Quiz> {
    const res = await fetch(`${API_BASE}/assessment/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lesson_id: lessonId, student_id: studentId, num_questions: numQuestions }),
    });
    return handleResponse<Quiz>(res);
  },

  async submitQuiz(payload: {
    quiz_id: string;
    student_id: string;
    lesson_id: string;
    answers: Array<{ question_id: string; student_answer: any }> | Record<string, any>;
  }): Promise<LearningReport> {
    const res = await fetch(`${API_BASE}/assessment/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<LearningReport>(res);
  },

  async getProfile(studentId: string = 'stu_default'): Promise<LearnerProfile> {
    const res = await fetch(`${API_BASE}/profile/${studentId}`);
    return handleResponse<LearnerProfile>(res);
  },

  async updateProfile(studentId: string, updates: Partial<LearnerProfile>): Promise<LearnerProfile> {
    const res = await fetch(`${API_BASE}/profile/${studentId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    return handleResponse<LearnerProfile>(res);
  },

  async getRecommendations(studentId: string = 'stu_default'): Promise<TopicRecommendation[]> {
    const res = await fetch(`${API_BASE}/profile/${studentId}/recommendations`);
    return handleResponse<TopicRecommendation[]>(res);
  },
};
