import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { IngestionView } from './components/Ingestion/IngestionView';
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
  } | null>(null);

  // Active Lesson Plan State
  const [plan, setPlan] = useState<LessonPlan | null>(null);
  const [isCreatingPlan, setIsCreatingPlan] = useState(false);

  // Video Pipeline State
  const [isGeneratingVideo, setIsGeneratingVideo] = useState(false);
  const [videoProgressPercent, setVideoProgressPercent] = useState(0);
  const [videoCurrentStage, setVideoCurrentStage] = useState('');
  const [videoManifest, setVideoManifest] = useState<VideoManifest | null>(null);

  // Initial Load of Profile
  useEffect(() => {
    loadProfile();
  }, []);

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
    } catch (err) {
      console.error('Failed to save profile updates:', err);
    }
  };

  const handleMaterialReady = (material: { documentId?: string; topicId?: string; title: string; summary: string }) => {
    setActiveMaterial(material);
    generatePlanForMaterial(material, profile.preferred_level, currentLanguage, 15);
  };

  const generatePlanForMaterial = async (
    material: { documentId?: string; topicId?: string; title: string },
    level: LearnerLevel,
    language: string,
    timeBudgetMin: number,
    priorKnowledge?: string,
    learningGoal?: string
  ) => {
    setIsCreatingPlan(true);
    try {
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
      });
      setPlan(newPlan);
      setCurrentTab('plan');
    } catch (err) {
      console.error('Failed to create lesson plan:', err);
    } finally {
      setIsCreatingPlan(false);
    }
  };

  const handleApproveAndGenerateVideo = async () => {
    if (!plan) return;
    setIsGeneratingVideo(true);
    setVideoProgressPercent(10);
    setVideoCurrentStage('Synthesizing Multilingual Neural Audio...');

    try {
      const { task_id } = await api.generateVideo(plan.plan_id);

      // Poll task status until complete
      const interval = setInterval(async () => {
        try {
          const status = await api.getVideoStatus(task_id);
          setVideoProgressPercent(status.progress_percent || 50);
          setVideoCurrentStage(status.current_stage || 'Rendering Visual Slides...');

          if (status.status === 'completed') {
            clearInterval(interval);
            setIsGeneratingVideo(false);
            // Fetch Manifest
            const lessonId = status.manifest_url?.split('/').pop() || plan.plan_id;
            try {
              const manifest = await api.getVideoManifest(lessonId);
              setVideoManifest(manifest);
              setCurrentTab('video');
            } catch {
              // Fallback manifest
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
            console.error('Video generation failed:', status.error_message);
          }
        } catch (pollErr) {
          console.warn('Status poll error:', pollErr);
        }
      }, 1500);
    } catch (err) {
      setIsGeneratingVideo(false);
      console.error('Trigger video generation error:', err);
    }
  };

  const handleSelectTopicFromDashboard = (topic: string) => {
    setActiveMaterial({
      title: topic,
      summary: `Targeted personalized refresher on ${topic}`,
    });
    generatePlanForMaterial(
      { title: topic },
      profile.preferred_level,
      currentLanguage,
      15
    );
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
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
      <main className="flex-1">
        {currentTab === 'ingest' && (
          <IngestionView onMaterialReady={handleMaterialReady} />
        )}

        {currentTab === 'plan' && plan && (
          <LessonPlanEditor
            plan={plan}
            onUpdatePlan={setPlan}
            onApproveAndGenerateVideo={handleApproveAndGenerateVideo}
            isGeneratingVideo={isGeneratingVideo}
            videoProgressPercent={videoProgressPercent}
            videoCurrentStage={videoCurrentStage}
            onOpenProfileModal={() => setIsProfileModalOpen(true)}
          />
        )}

        {currentTab === 'video' && videoManifest && (
          <InteractiveVideoPlayer
            manifest={videoManifest}
            onLessonComplete={() => setCurrentTab('quiz')}
            onToggleTutorChat={() => setIsTutorChatOpen((prev) => !prev)}
            currentLanguage={currentLanguage}
            onLanguageSwitch={(l: string) => setCurrentLanguage(l as LanguageCode)}
          />
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

      {/* Side-Panel AI Tutor Chat Drawer */}
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
