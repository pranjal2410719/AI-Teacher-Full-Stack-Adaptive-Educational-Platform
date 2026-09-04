import React, { useState, useEffect } from 'react';
import { Sparkles, PlayCircle, AlertCircle, Loader2 } from 'lucide-react';
import { Header } from './components/Header';
import { IngestionView, GenerateVideoPayload } from './components/Ingestion/IngestionView';
import { ProfileModal } from './components/Profile/ProfileModal';
import { LessonPlanEditor } from './components/Planner/LessonPlanEditor';
import { InteractiveVideoPlayer } from './components/VideoPlayer/InteractiveVideoPlayer';
import { SidePanelTutor } from './components/TutorChat/SidePanelTutor';
import { QuizView } from './components/Assessment/QuizView';
import { AnalyticsDashboard } from './components/Analytics/AnalyticsDashboard';
import { api } from './services/api';
import {
  LearnerProfile,
  LanguageCode,
  LearnerLevel,
  LessonPlan,
  VideoManifest,
} from './types';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<'ingest' | 'plan' | 'video' | 'quiz' | 'analytics'>('ingest');
  const [currentLanguage, setCurrentLanguage] = useState<LanguageCode>('en');
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
  const [isTutorChatOpen, setIsTutorChatOpen] = useState(false);

  // Student Profile State
  const [profile, setProfile] = useState<LearnerProfile>({
    student_id: 'stu_default',
    name: 'Learner',
    preferred_language: 'en',
    preferred_level: 'intermediate',
    total_lessons_completed: 0,
    average_mastery_percent: 0,
    concept_mastery: {},
    known_weak_areas: [],
    weak_areas: [],
    learning_history: [],
    completed_lessons: [],
    total_time_spent_min: 0,
  });

  // Active Ingestion State
  const [activeMaterial, setActiveMaterial] = useState<{
    documentId?: string;
    topicId?: string;
    title: string;
    summary: string;
    topic?: string;
  } | null>(null);

  // Active Lesson Plan State
  const [plan, setPlan] = useState<LessonPlan | null>(null);
  const [isCreatingPlan, setIsCreatingPlan] = useState(false);
  const [planError, setPlanError] = useState<string | null>(null);

  // Video Pipeline State
  const [isGeneratingVideo, setIsGeneratingVideo] = useState(false);
  const [videoProgressPercent, setVideoProgressPercent] = useState(0);
  const [videoCurrentStage, setVideoCurrentStage] = useState('');
  const [videoManifest, setVideoManifest] = useState<VideoManifest | null>(null);
  const [videoError, setVideoError] = useState<string | null>(null);

  // Topic prefill for parametric mode
  const [initialTopic, setInitialTopic] = useState('');

  // Initial Load of Profile
  useEffect(() => {
    loadProfile();
  }, []);

  // Reload profile on analytics tab visit to ensure fresh data
  useEffect(() => {
    if (currentTab === 'analytics') {
      loadProfile();
    }
  }, [currentTab]);

  const loadProfile = async () => {
    try {
      const p = await api.getProfile('stu_default');
      setProfile(p);
      if (p.preferred_language) setCurrentLanguage(p.preferred_language as LanguageCode);
    } catch (err) {
      console.warn('Using default student profile:', err);
    }
  };

  const handleToggleLanguage = async () => {
    const nextLang: LanguageCode = currentLanguage === 'en' ? 'hi' : 'en';
    setCurrentLanguage(nextLang);
    try {
      await api.updateProfile(profile.student_id, { preferred_language: nextLang });
      setProfile((prev) => ({ ...prev, preferred_language: nextLang }));
    } catch (err) {
      console.warn('Failed to update language preference:', err);
    }
  };

  const handleSaveProfile = async (updates: {
    name: string;
    level: LearnerLevel;
    language: LanguageCode;
    timeBudgetMin: number;
    priorKnowledge?: string;
    learningGoal?: string;
  }) => {
    try {
      const updated = await api.updateProfile(profile.student_id, {
        name: updates.name,
        preferred_level: updates.level,
        preferred_language: updates.language,
      });
      setProfile(updated);
      setCurrentLanguage(updates.language);

      // If active material exists, trigger lesson plan creation
      if (activeMaterial) {
        generatePlanForMaterial(activeMaterial, updates.level, updates.language, updates.timeBudgetMin, updates.priorKnowledge, updates.learningGoal);
      }
    } catch (err: any) {
      console.error('Failed to save profile updates:', err);
      setPlanError(err?.message || 'Failed to save profile updates.');
    }
  };

  const generatePlanForMaterial = async (
    material: { documentId?: string; topicId?: string; title: string; topic?: string },
    level: LearnerLevel,
    language: string,
    timeBudgetMin: number,
    priorKnowledge?: string,
    learningGoal?: string
  ) => {
    setIsCreatingPlan(true);
    setPlanError(null);
    try {
      const topicValue = material.topic || (!material.documentId && !material.topicId ? material.title : undefined);
      const newPlan = await api.createLessonPlan({
        learner_profile: {
          student_id: profile.student_id,
          level,
          language,
          time_budget_min: timeBudgetMin,
          prior_knowledge: priorKnowledge,
          learning_goal: learningGoal,
        },
        document_id: material.documentId,
        topic_id: material.topicId,
        topic: topicValue,
      });
      setPlan(newPlan);
      setCurrentTab('plan');
      return newPlan;
    } catch (err: any) {
      console.error('Failed to create lesson plan:', err);
      setPlanError(err?.message || 'Failed to create lesson plan. Please check backend connection.');
      throw err;
    } finally {
      setIsCreatingPlan(false);
    }
  };

  // R2: Single 'Generate Video' button chained handler
  const handleGenerateVideo = async (payload: GenerateVideoPayload) => {
    setIsGeneratingVideo(true);
    setVideoError(null);
    setVideoProgressPercent(10);
    setVideoCurrentStage('Ingesting Material & Grounding Pedagogical Knowledge...');

    try {
      let docId = payload.documentMetadata?.document_id;
      let topicId: string | undefined;
      const topicText = payload.topic;

      // 1. Ingest material if needed
      if (payload.file && !docId) {
        setVideoCurrentStage('Extracting Document Semantic Chunks...');
        setVideoProgressPercent(20);
        const uploaded = await api.uploadDocument(payload.file);
        docId = uploaded.document_id;
      } else if (topicText && !docId) {
        setVideoCurrentStage('Grounding Topic Concept in Knowledge Base...');
        setVideoProgressPercent(25);
        try {
          const topicDoc = await api.ingestTopic(topicText, payload.subjectCategory || 'General');
          topicId = topicDoc.topic_id;
        } catch (topicErr) {
          console.warn('Topic grounding fallback:', topicErr);
        }
      }

      const activeMat = {
        documentId: docId,
        topicId: topicId,
        title: payload.title || topicText || 'Educational Lesson',
        summary: payload.summary || `Personalized adaptive lesson on ${payload.title || topicText}`,
        topic: topicText,
      };
      setActiveMaterial(activeMat);

      // 2. Automatically formulate Lesson Plan
      setVideoCurrentStage('Synthesizing Pedagogical Blueprint & Checkpoints...');
      setVideoProgressPercent(40);
      const newPlan = await api.createLessonPlan({
        learner_profile: {
          student_id: profile.student_id,
          level: profile.preferred_level,
          language: currentLanguage,
          time_budget_min: 15,
        },
        document_id: docId,
        topic_id: topicId,
        topic: topicText || (!docId && !topicId ? activeMat.title : undefined),
      });
      setPlan(newPlan);

      // 3. Automatically trigger Video Generation
      setVideoCurrentStage('Synthesizing Neural Narration & Photorealistic AI Teacher Avatar...');
      setVideoProgressPercent(60);
      const { task_id } = await api.generateVideo(newPlan.plan_id);

      // 4. Poll task status until complete
      let pollFailures = 0;
      const maxPollFailures = 8;
      const startTime = Date.now();
      const maxDurationMs = 120000;

      const interval = setInterval(async () => {
        try {
          if (Date.now() - startTime > maxDurationMs) {
            clearInterval(interval);
            setIsGeneratingVideo(false);
            setVideoError('Video generation timed out. Please try again.');
            return;
          }

          const status = await api.getVideoStatus(task_id);
          pollFailures = 0;
          const pct = Math.max(60, Math.min(99, status.progress_percent || 70));
          setVideoProgressPercent(pct);
          setVideoCurrentStage(status.current_stage || 'Synthesizing Neural Audio & Teacher Avatar...');

          if (status.status === 'completed') {
            clearInterval(interval);
            setIsGeneratingVideo(false);
            setVideoProgressPercent(100);
            setVideoCurrentStage('Video Lesson Ready!');

            const lessonId = status.manifest_url?.split('/').pop() || newPlan.plan_id;
            try {
              const manifest = await api.getVideoManifest(lessonId);
              setVideoManifest(manifest);
              setCurrentTab('video');
            } catch {
              const fallbackManifest: VideoManifest = {
                lesson_id: lessonId,
                plan_id: newPlan.plan_id,
                video_url: `/api/v1/lessons/video/${lessonId}.mp4`,
                total_duration_sec: newPlan.target_duration_sec,
                language: newPlan.language,
                chapters: newPlan.modules.map((m) => ({
                  title: m.title,
                  start_sec: 0,
                  end_sec: m.duration_sec,
                  type: m.segment_type,
                })),
                pause_markers: newPlan.modules
                  .filter((m) => m.checkpoint_question)
                  .map((m) => ({
                    marker_id: `pm_${m.checkpoint_question!.question_id}`,
                    timestamp_sec: m.duration_sec / 2,
                    question: m.checkpoint_question!,
                  })),
              };
              setVideoManifest(fallbackManifest);
              setCurrentTab('video');
            }
          } else if (status.status === 'failed') {
            clearInterval(interval);
            setIsGeneratingVideo(false);
            setVideoError(status.error_message || 'Video generation failed on server.');
          }
        } catch (pollErr) {
          pollFailures++;
          if (pollFailures >= maxPollFailures) {
            clearInterval(interval);
            setIsGeneratingVideo(false);
            setVideoError('Lost connection to video generation service.');
          }
        }
      }, 1500);
    } catch (err: any) {
      setIsGeneratingVideo(false);
      setVideoError(err?.message || 'Failed to generate video lesson.');
      console.error('Generate video error:', err);
    }
  };

  const handleApproveAndGenerateVideo = async () => {
    if (!plan) return;
    setIsGeneratingVideo(true);
    setVideoError(null);
    setVideoProgressPercent(10);
    setVideoCurrentStage('Synthesizing Neural Audio & Photorealistic Teacher Avatar...');

    try {
      const { task_id } = await api.generateVideo(plan.plan_id);

      let pollFailures = 0;
      const maxPollFailures = 8;
      const startTime = Date.now();
      const maxDurationMs = 120000;

      const interval = setInterval(async () => {
        try {
          if (Date.now() - startTime > maxDurationMs) {
            clearInterval(interval);
            setIsGeneratingVideo(false);
            setVideoError('Video generation timed out. Please try again.');
            return;
          }

          const status = await api.getVideoStatus(task_id);
          pollFailures = 0;
          setVideoProgressPercent(status.progress_percent || 50);
          setVideoCurrentStage(status.current_stage || 'Rendering Visual Slides & Audio...');

          if (status.status === 'completed') {
            clearInterval(interval);
            setIsGeneratingVideo(false);
            const lessonId = status.manifest_url?.split('/').pop() || plan.plan_id;
            try {
              const manifest = await api.getVideoManifest(lessonId);
              setVideoManifest(manifest);
              setCurrentTab('video');
            } catch {
              const fallbackManifest: VideoManifest = {
                lesson_id: lessonId,
                plan_id: plan.plan_id,
                video_url: `/api/v1/lessons/video/${lessonId}.mp4`,
                total_duration_sec: plan.target_duration_sec,
                language: plan.language,
                chapters: plan.modules.map((m) => ({
                  title: m.title,
                  start_sec: 0,
                  end_sec: m.duration_sec,
                  type: m.segment_type,
                })),
                pause_markers: plan.modules
                  .filter((m) => m.checkpoint_question)
                  .map((m) => ({
                    marker_id: `pm_${m.checkpoint_question!.question_id}`,
                    timestamp_sec: m.duration_sec / 2,
                    question: m.checkpoint_question!,
                  })),
              };
              setVideoManifest(fallbackManifest);
              setCurrentTab('video');
            }
          } else if (status.status === 'failed') {
            clearInterval(interval);
            setIsGeneratingVideo(false);
            setVideoError(status.error_message || 'Video generation failed on server.');
          }
        } catch (pollErr) {
          pollFailures++;
          if (pollFailures >= maxPollFailures) {
            clearInterval(interval);
            setIsGeneratingVideo(false);
            setVideoError('Lost connection to video generation service.');
          }
        }
      }, 1500);
    } catch (err: any) {
      setIsGeneratingVideo(false);
      setVideoError(err?.message || 'Failed to trigger video generation.');
      console.error('Trigger video generation error:', err);
    }
  };

  const handleSelectTopicFromDashboard = (topic: string) => {
    setInitialTopic(topic);
    setCurrentTab('ingest');
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      {/* Header */}
      <Header
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        profile={profile}
        currentLanguage={currentLanguage}
        onToggleLanguage={handleToggleLanguage}
        onOpenProfile={() => setIsProfileModalOpen(true)}
      />

      {/* Main Content Area */}
      <main className="flex-1 pb-12">
        {/* Error Banners */}
        {planError && (
          <div className="max-w-4xl mx-auto px-4 pt-4">
            <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 flex items-center justify-between shadow-sm">
              <div className="flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
                <div>
                  <div className="text-sm font-bold text-red-900">Plan Formulation Issue</div>
                  <div className="text-xs text-red-700">{planError}</div>
                </div>
              </div>
              <button
                onClick={() => setPlanError(null)}
                className="px-3 py-1 rounded-lg bg-red-100 hover:bg-red-200 text-xs font-semibold text-red-800 border border-red-300 transition-colors"
              >
                Dismiss
              </button>
            </div>
          </div>
        )}

        {videoError && (
          <div className="max-w-4xl mx-auto px-4 pt-4">
            <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 flex items-center justify-between shadow-sm">
              <div className="flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
                <div>
                  <div className="text-sm font-bold text-red-900">Video Generation Error</div>
                  <div className="text-xs text-red-700">{videoError}</div>
                </div>
              </div>
              <button
                onClick={() => setVideoError(null)}
                className="px-3 py-1 rounded-lg bg-red-100 hover:bg-red-200 text-xs font-semibold text-red-800 border border-red-300 transition-colors"
              >
                Dismiss
              </button>
            </div>
          </div>
        )}

        {/* Tab Views */}
        {currentTab === 'ingest' && (
          <IngestionView
            onGenerateVideo={handleGenerateVideo}
            isGenerating={isGeneratingVideo || isCreatingPlan}
            progressStage={videoCurrentStage}
            progressPercent={videoProgressPercent}
            initialTopic={initialTopic}
          />
        )}

        {currentTab === 'plan' && (
          isCreatingPlan ? (
            <div className="max-w-xl mx-auto py-20 px-4">
              <div className="bg-white border border-gray-200 rounded-2xl p-8 text-center text-slate-800 space-y-4 shadow-sm">
                <div className="w-16 h-16 rounded-2xl bg-blue-50 border border-blue-200 flex items-center justify-center mx-auto text-blue-900">
                  <Loader2 className="w-8 h-8 animate-spin text-blue-900" />
                </div>
                <h2 className="text-xl font-bold text-blue-950">Synthesizing Pedagogical Blueprint...</h2>
                <p className="text-xs text-slate-600 leading-relaxed max-w-md mx-auto">
                  ApniHelp is analyzing the material, structuring learning modules, and creating interactive pause checkpoints.
                </p>
              </div>
            </div>
          ) : plan ? (
            <LessonPlanEditor
              plan={plan}
              onUpdatePlan={setPlan}
              onApproveAndGenerateVideo={handleApproveAndGenerateVideo}
              isGeneratingVideo={isGeneratingVideo}
              videoProgressPercent={videoProgressPercent}
              videoCurrentStage={videoCurrentStage}
              onOpenProfileModal={() => setIsProfileModalOpen(true)}
            />
          ) : (
            <div className="max-w-xl mx-auto py-20 px-4">
              <div className="bg-white border border-gray-200 rounded-2xl p-8 text-center text-slate-800 space-y-4 shadow-sm">
                <div className="w-16 h-16 rounded-2xl bg-blue-50 border border-blue-200 flex items-center justify-center mx-auto text-blue-900">
                  <Sparkles className="w-8 h-8 text-blue-900" />
                </div>
                <h2 className="text-xl font-bold text-blue-950">No Lesson Plan Generated Yet</h2>
                <p className="text-xs text-slate-600 leading-relaxed max-w-md mx-auto">
                  Click 'Generate Video' on any uploaded document or curriculum topic to automatically produce an interactive video lesson.
                </p>
                <div className="pt-2">
                  <button
                    onClick={() => setCurrentTab('ingest')}
                    className="px-6 py-2.5 rounded-xl bg-yellow-400 hover:bg-yellow-500 text-slate-950 text-xs font-black transition-all shadow-md shadow-yellow-500/20 inline-flex items-center gap-2"
                  >
                    Go to Video Studio
                  </button>
                </div>
              </div>
            </div>
          )
        )}

        {currentTab === 'video' && (
          videoManifest ? (
            <InteractiveVideoPlayer
              manifest={videoManifest}
              onLessonComplete={() => setCurrentTab('quiz')}
              onToggleTutorChat={() => setIsTutorChatOpen((prev) => !prev)}
              currentLanguage={currentLanguage}
              onLanguageSwitch={(l: string) => setCurrentLanguage(l as LanguageCode)}
            />
          ) : isGeneratingVideo ? (
            <div className="max-w-xl mx-auto py-20 px-4">
              <div className="bg-white border border-gray-200 rounded-2xl p-8 text-center text-slate-800 space-y-4 shadow-sm">
                <div className="w-16 h-16 rounded-2xl bg-blue-50 border border-blue-200 flex items-center justify-center mx-auto text-blue-900">
                  <Loader2 className="w-8 h-8 animate-spin text-blue-900" />
                </div>
                <h2 className="text-xl font-bold text-blue-950">Synthesizing AI Video Lesson...</h2>
                <p className="text-xs text-slate-600 max-w-md mx-auto">{videoCurrentStage || 'Rendering neural narration, slides, and teacher avatar...'}</p>
                <div className="w-full max-w-md mx-auto bg-slate-100 rounded-full h-2.5 overflow-hidden border border-gray-200">
                  <div className="bg-yellow-400 h-2.5 rounded-full transition-all duration-300" style={{ width: `${videoProgressPercent}%` }}></div>
                </div>
                <span className="text-xs text-slate-500 font-bold block">{videoProgressPercent}% Completed</span>
              </div>
            </div>
          ) : (
            <div className="max-w-xl mx-auto py-20 px-4">
              <div className="bg-white border border-gray-200 rounded-2xl p-8 text-center text-slate-800 space-y-4 shadow-sm">
                <div className="w-16 h-16 rounded-2xl bg-blue-50 border border-blue-200 flex items-center justify-center mx-auto text-blue-900">
                  <PlayCircle className="w-8 h-8 text-blue-900" />
                </div>
                <h2 className="text-xl font-bold text-blue-950">No Video Ready Yet</h2>
                <p className="text-xs text-slate-600 leading-relaxed max-w-md mx-auto">
                  Generate your video from the Studio view with a single click.
                </p>
                <div className="flex items-center justify-center gap-3 pt-2">
                  <button
                    onClick={() => setCurrentTab('ingest')}
                    className="px-6 py-2.5 rounded-xl bg-yellow-400 hover:bg-yellow-500 text-slate-950 text-xs font-black transition-all shadow-md shadow-yellow-500/20 inline-flex items-center gap-2"
                  >
                    Go to Video Studio
                  </button>
                </div>
              </div>
            </div>
          )
        )}

        {currentTab === 'quiz' && (
          <QuizView
            lessonId={plan?.plan_id || activeMaterial?.documentId || activeMaterial?.topicId || 'les_default'}
            studentId={profile.student_id}
            onViewAnalytics={() => {
              loadProfile();
              setCurrentTab('analytics');
            }}
            onSelectNextTopic={handleSelectTopicFromDashboard}
          />
        )}

        {currentTab === 'analytics' && (
          <AnalyticsDashboard
            profile={profile}
            onOpenProfileModal={() => setIsProfileModalOpen(true)}
            onSelectTopic={handleSelectTopicFromDashboard}
          />
        )}
      </main>

      {/* Side-Panel ApniHelp Tutor Chat Drawer */}
      <SidePanelTutor
        isOpen={isTutorChatOpen}
        onClose={() => setIsTutorChatOpen(false)}
        currentLanguage={currentLanguage}
        onLanguageSwitch={(l: string) => setCurrentLanguage(l as LanguageCode)}
        documentId={activeMaterial?.documentId}
        topicId={activeMaterial?.topicId}
      />

      {/* Learner Profile Configuration Modal */}
      <ProfileModal
        isOpen={isProfileModalOpen}
        onClose={() => setIsProfileModalOpen(false)}
        profile={profile}
        onSaveProfile={handleSaveProfile}
      />
    </div>
  );
};
