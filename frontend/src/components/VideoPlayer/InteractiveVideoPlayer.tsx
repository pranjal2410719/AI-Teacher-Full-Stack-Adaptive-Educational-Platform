import React, { useState, useRef, useEffect } from 'react';
import {
  Play,
  Pause,
  RotateCcw,
  Volume2,
  VolumeX,
  Maximize2,
  HelpCircle,
  CheckCircle2,
  AlertTriangle,
  Lightbulb,
  ArrowRight,
  Sparkles,
  MessageSquare,
  Globe,
  Award,
  Loader2,
} from 'lucide-react';
import { VideoManifest, CheckpointQuestion, AnswerEvaluationResponse } from '../../types';
import { api } from '../../services/api';

interface InteractiveVideoPlayerProps {
  manifest: VideoManifest;
  onLessonComplete: () => void;
  onToggleTutorChat: () => void;
  currentLanguage: string;
  onLanguageSwitch: (newLang: string) => void;
}

export const InteractiveVideoPlayer: React.FC<InteractiveVideoPlayerProps> = ({
  manifest,
  onLessonComplete,
  onToggleTutorChat,
  currentLanguage,
  onLanguageSwitch,
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(manifest.total_duration_sec || 60);
  const [isMuted, setIsMuted] = useState(false);

  // Active Checkpoint State
  const [activeCheckpoint, setActiveCheckpoint] = useState<{
    marker_id: string;
    timestamp_sec: number;
    question: CheckpointQuestion;
  } | null>(null);
  const [answeredCheckpoints, setAnsweredCheckpoints] = useState<Set<string>>(new Set());

  // Evaluation & Misconception State
  const [studentAnswer, setStudentAnswer] = useState('');
  const [selectedOptionIndex, setSelectedOptionIndex] = useState<number | null>(null);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [evalResult, setEvalResult] = useState<AnswerEvaluationResponse | null>(null);
  const [followUpAnswer, setFollowUpAnswer] = useState('');
  const [isFollowUpResolved, setIsFollowUpResolved] = useState(false);

  // Video Time Update & Checkpoint Trigger
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleTimeUpdate = () => {
      setCurrentTime(video.currentTime);

      // Check if we hit any un-answered pause markers
      if (manifest.pause_markers) {
        for (const marker of manifest.pause_markers) {
          if (
            !answeredCheckpoints.has(marker.marker_id) &&
            Math.abs(video.currentTime - marker.timestamp_sec) < 1.0 &&
            !activeCheckpoint
          ) {
            video.pause();
            setIsPlaying(false);
            setActiveCheckpoint(marker);
            setEvalResult(null);
            setStudentAnswer('');
            setSelectedOptionIndex(null);
            setIsFollowUpResolved(false);
            break;
          }
        }
      }

      // Check if video reached the end
      if (video.currentTime >= (video.duration || manifest.total_duration_sec) - 0.5) {
        setIsPlaying(false);
      }
    };

    const handleLoadedMetadata = () => {
      if (video.duration && !isNaN(video.duration)) {
        setDuration(video.duration);
      }
    };

    video.addEventListener('timeupdate', handleTimeUpdate);
    video.addEventListener('loadedmetadata', handleLoadedMetadata);

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate);
      video.removeEventListener('loadedmetadata', handleLoadedMetadata);
    };
  }, [manifest, answeredCheckpoints, activeCheckpoint]);

  const togglePlay = () => {
    if (activeCheckpoint && !evalResult?.can_resume_video && !isFollowUpResolved) return;
    const video = videoRef.current;
    if (!video) return;
    if (isPlaying) {
      video.pause();
      setIsPlaying(false);
    } else {
      video.play();
      setIsPlaying(true);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value);
    if (videoRef.current) {
      videoRef.current.currentTime = time;
      setCurrentTime(time);
    }
  };

  const handleAnswerSubmit = async () => {
    if (!activeCheckpoint) return;
    setIsEvaluating(true);

    let answerText = studentAnswer;
    if (activeCheckpoint.question.type === 'mcq' && selectedOptionIndex !== null) {
      answerText = activeCheckpoint.question.options?.[selectedOptionIndex] || `Option ${selectedOptionIndex}`;
    }

    try {
      const res = await api.evaluateAnswer({
        session_id: `ses_player_${manifest.lesson_id}`,
        question_id: activeCheckpoint.question.question_id,
        student_answer: answerText,
        current_concept: activeCheckpoint.question.prompt,
        language: currentLanguage,
      });
      setEvalResult(res);
      if (res.is_correct) {
        setAnsweredCheckpoints((prev) => new Set(prev).add(activeCheckpoint.marker_id));
      }
    } catch (err: any) {
      console.error('Answer evaluation failed:', err);
    } finally {
      setIsEvaluating(false);
    }
  };

  const handleFollowUpSubmit = () => {
    if (!followUpAnswer.trim() || !activeCheckpoint) return;
    // Mark as resolved and allow resume
    setIsFollowUpResolved(true);
    setAnsweredCheckpoints((prev) => new Set(prev).add(activeCheckpoint.marker_id));
  };

  const handleResumeVideo = () => {
    setActiveCheckpoint(null);
    setEvalResult(null);
    if (videoRef.current) {
      videoRef.current.play();
      setIsPlaying(true);
    }
  };

  const formatTime = (seconds: number) => {
    const min = Math.floor(seconds / 60);
    const sec = Math.floor(seconds % 60);
    return `${min}:${sec < 10 ? '0' : ''}${sec}`;
  };

  return (
    <div className="max-w-5xl mx-auto py-6 px-4 space-y-6">
      {/* Video Container Card */}
      <div className="relative rounded-2xl bg-slate-950 border border-slate-800 shadow-2xl overflow-hidden group aspect-video flex items-center justify-center">
        {/* Video Element */}
        <video
          ref={videoRef}
          src={manifest.video_url}
          className="w-full h-full object-contain bg-black"
          playsInline
        />

        {/* Checkpoint Question Modal Overlay */}
        {activeCheckpoint && (
          <div className="absolute inset-0 z-30 bg-slate-950/95 backdrop-blur-md flex items-center justify-center p-6 animate-in fade-in">
            <div className="w-full max-w-2xl bg-slate-900 border border-purple-900/60 rounded-2xl p-6 shadow-2xl space-y-5 max-h-[90%] overflow-y-auto">
              {/* Question Header */}
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2 text-xs text-purple-400 font-bold uppercase tracking-wider">
                  <HelpCircle className="w-4 h-4" />
                  <span>In-Video Comprehension Checkpoint</span>
                </div>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800/40">
                  Pause at {formatTime(activeCheckpoint.timestamp_sec)}
                </span>
              </div>

              {/* Question Prompt */}
              <div>
                <h3 className="text-base font-bold text-slate-100 leading-snug">
                  {activeCheckpoint.question.prompt}
                </h3>
              </div>

              {/* Form: MCQ or Short Answer */}
              {!evalResult && (
                <div className="space-y-4">
                  {activeCheckpoint.question.options ? (
                    <div className="space-y-2">
                      {activeCheckpoint.question.options.map((opt, idx) => (
                        <div
                          key={idx}
                          onClick={() => setSelectedOptionIndex(idx)}
                          className={`p-3 rounded-xl border text-xs cursor-pointer transition-all flex items-center justify-between ${
                            selectedOptionIndex === idx
                              ? 'border-purple-500 bg-purple-950/40 text-purple-200 shadow-md shadow-purple-950/30'
                              : 'border-slate-800 bg-slate-950/60 text-slate-300 hover:border-slate-700'
                          }`}
                        >
                          <span>{opt}</span>
                          <div
                            className={`w-4 h-4 rounded-full border flex items-center justify-center text-[10px] ${
                              selectedOptionIndex === idx
                                ? 'border-purple-500 bg-purple-600 text-white'
                                : 'border-slate-700'
                            }`}
                          >
                            {selectedOptionIndex === idx && '✓'}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <textarea
                      rows={3}
                      value={studentAnswer}
                      onChange={(e) => setStudentAnswer(e.target.value)}
                      placeholder="Type your conceptual explanation..."
                      className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-purple-500 font-sans leading-relaxed"
                    />
                  )}

                  <button
                    onClick={handleAnswerSubmit}
                    disabled={
                      isEvaluating ||
                      (activeCheckpoint.question.options ? selectedOptionIndex === null : !studentAnswer.trim())
                    }
                    className="w-full py-3 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 disabled:opacity-40 text-white text-xs font-bold flex items-center justify-center gap-2 shadow-lg shadow-purple-600/30 transition-all"
                  >
                    {isEvaluating ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Evaluating Response with AI Teacher...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4" />
                        <span>Submit Answer</span>
                      </>
                    )}
                  </button>
                </div>
              )}

              {/* Evaluation Feedback & Misconception Drawer */}
              {evalResult && (
                <div className="space-y-4 animate-in fade-in">
                  {/* Correct Feedback */}
                  {evalResult.is_correct ? (
                    <div className="p-4 rounded-xl bg-emerald-950/50 border border-emerald-800/60 space-y-3">
                      <div className="flex items-center gap-2 text-xs font-bold text-emerald-400">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                        <span>Mastery Confirmed! (Score: {(evalResult.score * 100).toFixed(0)}%)</span>
                      </div>
                      <p className="text-xs text-emerald-200/90 leading-relaxed">
                        {evalResult.feedback}
                      </p>
                      <button
                        onClick={handleResumeVideo}
                        className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold flex items-center justify-center gap-2 shadow-md shadow-emerald-600/20 transition-all"
                      >
                        <Play className="w-3.5 h-3.5 fill-white" />
                        <span>Resume Lesson Video</span>
                      </button>
                    </div>
                  ) : (
                    /* Misconception Diagnosed + Re-Explanation */
                    <div className="space-y-4">
                      {/* Misconception Tag */}
                      <div className="p-3.5 rounded-xl bg-amber-950/40 border border-amber-800/50 space-y-1.5">
                        <div className="flex items-center gap-2 text-xs font-bold text-amber-400">
                          <AlertTriangle className="w-4 h-4 text-amber-400" />
                          <span>Diagnosed Root Misconception</span>
                        </div>
                        <p className="text-xs text-amber-200 font-medium">
                          {evalResult.misconception_detected || evalResult.misconception}
                        </p>
                      </div>

                      {/* Scaffolded Analogy Re-Explanation */}
                      {evalResult.pedagogical_re_explanation && (
                        <div className="p-4 rounded-xl bg-indigo-950/40 border border-indigo-800/60 space-y-2">
                          <div className="flex items-center gap-2 text-xs font-bold text-indigo-300">
                            <Lightbulb className="w-4 h-4 text-indigo-400" />
                            <span>AI Teacher Scaffolded Re-Explanation & Analogy</span>
                          </div>
                          <p className="text-xs text-indigo-100 leading-relaxed font-sans">
                            {evalResult.pedagogical_re_explanation}
                          </p>
                        </div>
                      )}

                      {/* Follow-up Comprehension Check */}
                      {evalResult.follow_up_question && !isFollowUpResolved && (
                        <div className="p-4 rounded-xl bg-slate-950 border border-purple-900/40 space-y-3">
                          <span className="text-[11px] font-bold text-purple-300 uppercase tracking-wider block">
                            Targeted Follow-Up Check:
                          </span>
                          <p className="text-xs text-slate-200 font-medium">
                            {evalResult.follow_up_question.prompt}
                          </p>
                          <input
                            type="text"
                            value={followUpAnswer}
                            onChange={(e) => setFollowUpAnswer(e.target.value)}
                            placeholder="State your answer now..."
                            className="w-full px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-100 focus:outline-none focus:border-purple-500"
                          />
                          <button
                            onClick={handleFollowUpSubmit}
                            disabled={!followUpAnswer.trim()}
                            className="w-full py-2.5 rounded-lg bg-purple-600 hover:bg-purple-500 disabled:opacity-40 text-white text-xs font-bold flex items-center justify-center gap-1.5 transition-all shadow-md shadow-purple-600/20"
                          >
                            <span>Verify Follow-Up Comprehension</span>
                            <ArrowRight className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      )}

                      {/* Follow-up Resolved Resume CTA */}
                      {isFollowUpResolved && (
                        <div className="p-3.5 rounded-xl bg-emerald-950/40 border border-emerald-800/60 space-y-2">
                          <div className="flex items-center gap-1.5 text-xs text-emerald-400 font-bold">
                            <CheckCircle2 className="w-4 h-4" />
                            <span>Concept Clarified & Misconception Resolved!</span>
                          </div>
                          <button
                            onClick={handleResumeVideo}
                            className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold flex items-center justify-center gap-2 shadow-md shadow-emerald-600/20 transition-all"
                          >
                            <Play className="w-3.5 h-3.5 fill-white" />
                            <span>Resume Lesson Video</span>
                          </button>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Custom Video Controls Bar */}
        <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/90 via-black/60 to-transparent p-4 flex flex-col gap-2 z-20">
          {/* Progress Scrubber with Pause Markers */}
          <div className="relative w-full flex items-center">
            <input
              type="range"
              min={0}
              max={duration}
              step={0.1}
              value={currentTime}
              onChange={handleSeek}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
            {/* Pause Marker Dots */}
            {manifest.pause_markers?.map((pm, idx) => {
              const posPercent = (pm.timestamp_sec / duration) * 100;
              const isAnswered = answeredCheckpoints.has(pm.marker_id);
              return (
                <div
                  key={idx}
                  style={{ left: `${posPercent}%` }}
                  className={`absolute -top-1 w-3 h-3 rounded-full -translate-x-1/2 border transition-all ${
                    isAnswered
                      ? 'bg-emerald-400 border-emerald-200'
                      : 'bg-purple-500 border-purple-200 shadow-md shadow-purple-500/80 animate-pulse'
                  }`}
                  title={`Checkpoint Pause: ${formatTime(pm.timestamp_sec)}`}
                />
              );
            })}
          </div>

          {/* Bottom Button Row */}
          <div className="flex items-center justify-between text-xs text-slate-300">
            <div className="flex items-center gap-3">
              <button
                onClick={togglePlay}
                className="p-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-white transition-colors shadow-sm"
              >
                {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 fill-white" />}
              </button>

              <button
                onClick={() => {
                  if (videoRef.current) {
                    videoRef.current.currentTime = 0;
                    setCurrentTime(0);
                  }
                }}
                className="p-1.5 text-slate-400 hover:text-white"
              >
                <RotateCcw className="w-4 h-4" />
              </button>

              <span className="font-mono text-[11px] text-slate-300">
                {formatTime(currentTime)} / {formatTime(duration)}
              </span>
            </div>

            <div className="flex items-center gap-3">
              {/* Mid-Session Language Switcher */}
              <button
                onClick={() => onLanguageSwitch(currentLanguage === 'en' ? 'hi' : 'en')}
                className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-700 text-[11px] font-semibold text-slate-200 hover:bg-slate-800"
              >
                <Globe className="w-3.5 h-3.5 text-emerald-400" />
                <span>{currentLanguage === 'en' ? 'हिन्दी में बदलें' : 'Switch to EN'}</span>
              </button>

              {/* Side-Panel Tutor Chat Toggle */}
              <button
                onClick={onToggleTutorChat}
                className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-purple-950/80 border border-purple-800/60 text-[11px] font-semibold text-purple-300 hover:bg-purple-900"
              >
                <MessageSquare className="w-3.5 h-3.5 text-purple-400" />
                <span>AI Tutor Chat</span>
              </button>

              {/* Post-Lesson Quiz CTA */}
              <button
                onClick={onLessonComplete}
                className="flex items-center gap-1 px-3 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-[11px] font-bold text-white shadow-sm transition-colors"
              >
                <Award className="w-3.5 h-3.5" />
                <span>Take Post-Quiz</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
