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
  const [evalError, setEvalError] = useState<string | null>(null);
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
            setEvalError(null);
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
    setEvalError(null);

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
      setEvalError(err.message || 'Answer evaluation failed. Please try submitting again.');
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
      <div className="relative rounded-2xl bg-black border border-gray-300 shadow-xl overflow-hidden group aspect-video flex items-center justify-center">
        {/* Video Element */}
        <video
          ref={videoRef}
          src={manifest.video_url}
          className="w-full h-full object-contain bg-black"
          playsInline
        />

        {/* Checkpoint Question Modal Overlay */}
        {activeCheckpoint && (
          <div className="absolute inset-0 z-30 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-6 animate-in fade-in">
            <div className="w-full max-w-2xl bg-white border border-gray-200 rounded-2xl p-6 shadow-2xl space-y-5 max-h-[90%] overflow-y-auto">
              {/* Question Header */}
              <div className="flex items-center justify-between border-b border-gray-200 pb-3">
                <div className="flex items-center gap-2 text-xs text-blue-950 font-bold uppercase tracking-wider">
                  <HelpCircle className="w-4 h-4 text-blue-900" />
                  <span>In-Video Comprehension Checkpoint</span>
                </div>
                <span className="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-yellow-100 text-yellow-800 border border-yellow-300 font-bold">
                  Pause at {formatTime(activeCheckpoint.timestamp_sec)}
                </span>
              </div>

              {/* Question Prompt */}
              <div>
                <h3 className="text-base font-bold text-slate-900 leading-snug">
                  {activeCheckpoint.question.prompt}
                </h3>
              </div>

              {evalError && (
                <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-red-500 flex-shrink-0" />
                  <span>{evalError}</span>
                </div>
              )}

              {/* Form: MCQ or Short Answer */}
              {!evalResult && (
                <div className="space-y-4">
                  {activeCheckpoint.question.options ? (
                    <div className="space-y-2">
                      {activeCheckpoint.question.options.map((opt, idx) => (
                        <button
                          type="button"
                          key={idx}
                          onClick={() => setSelectedOptionIndex(idx)}
                          className={`w-full p-3.5 rounded-xl border text-xs text-left cursor-pointer transition-all flex items-center justify-between ${
                            selectedOptionIndex === idx
                              ? 'border-2 border-blue-900 bg-blue-50/70 text-blue-950 font-semibold shadow-sm'
                              : 'border-gray-200 bg-slate-50 text-slate-800 hover:border-blue-400 hover:bg-blue-50/30'
                          }`}
                        >
                          <span className="leading-snug">{opt}</span>
                          <div
                            className={`w-4 h-4 rounded-full border flex items-center justify-center text-[10px] flex-shrink-0 ml-2 ${
                              selectedOptionIndex === idx
                                ? 'border-blue-900 bg-blue-900 text-white'
                                : 'border-gray-300'
                            }`}
                          >
                            {selectedOptionIndex === idx && '✓'}
                          </div>
                        </button>
                      ))}
                    </div>
                  ) : (
                    <textarea
                      rows={3}
                      value={studentAnswer}
                      onChange={(e) => setStudentAnswer(e.target.value)}
                      placeholder="Type your conceptual explanation..."
                      className="w-full px-4 py-3 rounded-xl bg-white border border-gray-300 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-900 focus:ring-1 focus:ring-blue-900 font-sans leading-relaxed shadow-xs"
                    />
                  )}

                  <button
                    onClick={handleAnswerSubmit}
                    disabled={
                      isEvaluating ||
                      (activeCheckpoint.question.options ? selectedOptionIndex === null : !studentAnswer.trim())
                    }
                    className="w-full py-3.5 rounded-xl bg-yellow-400 hover:bg-yellow-500 active:bg-yellow-600 disabled:opacity-40 text-slate-950 text-xs font-black flex items-center justify-center gap-2 shadow-md shadow-yellow-500/20 transition-all cursor-pointer"
                  >
                    {isEvaluating ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin text-slate-950" />
                        <span>Evaluating Response with ApniHelp...</span>
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
                    <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-300 space-y-3">
                      <div className="flex items-center gap-2 text-xs font-bold text-emerald-800">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                        <span>Mastery Confirmed! (Score: {(evalResult.score * 100).toFixed(0)}%)</span>
                      </div>
                      <p className="text-xs text-emerald-900 leading-relaxed">
                        {evalResult.feedback}
                      </p>
                      <button
                        onClick={handleResumeVideo}
                        className="w-full py-2.5 rounded-xl bg-blue-900 hover:bg-blue-800 text-white text-xs font-bold flex items-center justify-center gap-2 shadow-sm transition-all cursor-pointer"
                      >
                        <Play className="w-3.5 h-3.5 fill-white" />
                        <span>Resume Lesson Video</span>
                      </button>
                    </div>
                  ) : (
                    /* Misconception Diagnosed + Re-Explanation */
                    <div className="space-y-4">
                      {/* Misconception Tag */}
                      <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-300 space-y-1.5">
                        <div className="flex items-center gap-2 text-xs font-bold text-amber-800">
                          <AlertTriangle className="w-4 h-4 text-amber-600" />
                          <span>Diagnosed Root Misconception</span>
                        </div>
                        <p className="text-xs text-amber-900 font-medium">
                          {evalResult.misconception_detected || evalResult.misconception}
                        </p>
                      </div>

                      {/* Scaffolded Analogy Re-Explanation */}
                      {evalResult.pedagogical_re_explanation && (
                        <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 space-y-2">
                          <div className="flex items-center gap-2 text-xs font-bold text-blue-900">
                            <Lightbulb className="w-4 h-4 text-blue-800" />
                            <span>ApniHelp Scaffolded Re-Explanation & Analogy</span>
                          </div>
                          <p className="text-xs text-blue-950 leading-relaxed font-sans">
                            {evalResult.pedagogical_re_explanation}
                          </p>
                        </div>
                      )}

                      {/* Follow-up Comprehension Check */}
                      {evalResult.follow_up_question && !isFollowUpResolved && (
                        <div className="p-4 rounded-xl bg-slate-50 border border-gray-200 space-y-3">
                          <span className="text-[11px] font-bold text-blue-900 uppercase tracking-wider block">
                            Targeted Follow-Up Check:
                          </span>
                          <p className="text-xs text-slate-900 font-medium">
                            {evalResult.follow_up_question.prompt}
                          </p>
                          <input
                            type="text"
                            value={followUpAnswer}
                            onChange={(e) => setFollowUpAnswer(e.target.value)}
                            placeholder="State your answer now..."
                            className="w-full px-3.5 py-2 rounded-lg bg-white border border-gray-300 text-xs text-slate-900 focus:outline-none focus:border-blue-900 focus:ring-1 focus:ring-blue-900"
                          />
                          <button
                            onClick={handleFollowUpSubmit}
                            disabled={!followUpAnswer.trim()}
                            className="w-full py-2.5 rounded-lg bg-blue-900 hover:bg-blue-800 disabled:opacity-40 text-white text-xs font-bold flex items-center justify-center gap-1.5 transition-all shadow-sm cursor-pointer"
                          >
                            <span>Verify Follow-Up Comprehension</span>
                            <ArrowRight className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      )}

                      {/* Follow-up Resolved Resume CTA */}
                      {isFollowUpResolved && (
                        <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-300 space-y-2">
                          <div className="flex items-center gap-1.5 text-xs text-emerald-800 font-bold">
                            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                            <span>Concept Clarified & Misconception Resolved!</span>
                          </div>
                          <button
                            onClick={handleResumeVideo}
                            className="w-full py-2.5 rounded-xl bg-blue-900 hover:bg-blue-800 text-white text-xs font-bold flex items-center justify-center gap-2 shadow-sm transition-all cursor-pointer"
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
              className="w-full h-1.5 bg-slate-700/80 rounded-lg appearance-none cursor-pointer accent-yellow-400"
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
                      ? 'bg-emerald-400 border-white'
                      : 'bg-yellow-400 border-white shadow-md shadow-yellow-400/80 animate-pulse'
                  }`}
                  title={`Checkpoint Pause: ${formatTime(pm.timestamp_sec)}`}
                />
              );
            })}
          </div>

          {/* Bottom Button Row */}
          <div className="flex items-center justify-between text-xs text-slate-200">
            <div className="flex items-center gap-3">
              <button
                onClick={togglePlay}
                className="p-2 rounded-lg bg-yellow-400 hover:bg-yellow-500 text-slate-950 font-bold transition-colors shadow-sm cursor-pointer"
              >
                {isPlaying ? <Pause className="w-4 h-4 text-slate-950" /> : <Play className="w-4 h-4 fill-slate-950 text-slate-950" />}
              </button>

              <button
                onClick={() => {
                  if (videoRef.current) {
                    videoRef.current.currentTime = 0;
                    setCurrentTime(0);
                  }
                }}
                className="p-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-white/10 transition-colors"
                title="Reset time to beginning"
              >
                <RotateCcw className="w-4 h-4" />
              </button>

              <span className="font-mono text-[11px] text-slate-200 font-semibold">
                {formatTime(currentTime)} / {formatTime(duration)}
              </span>
            </div>

            <div className="flex items-center gap-3">
              {/* Mid-Session Language Switcher */}
              <button
                onClick={() => onLanguageSwitch(currentLanguage === 'en' ? 'hi' : 'en')}
                className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white/95 hover:bg-white border border-gray-200 text-[11px] font-bold text-slate-900 transition-colors shadow-sm"
              >
                <Globe className="w-3.5 h-3.5 text-blue-900" />
                <span>{currentLanguage === 'en' ? 'हिन्दी में बदलें' : 'Switch to EN'}</span>
              </button>

              {/* Side-Panel Tutor Chat Toggle */}
              <button
                onClick={onToggleTutorChat}
                className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-blue-900 hover:bg-blue-800 text-[11px] font-bold text-white transition-colors shadow-sm"
              >
                <MessageSquare className="w-3.5 h-3.5 text-yellow-400" />
                <span>ApniHelp Tutor Chat</span>
              </button>

              {/* Post-Lesson Quiz CTA */}
              <button
                onClick={onLessonComplete}
                className="flex items-center gap-1 px-3 py-1 rounded-lg bg-yellow-400 hover:bg-yellow-500 text-[11px] font-black text-slate-950 shadow-sm transition-colors cursor-pointer"
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
