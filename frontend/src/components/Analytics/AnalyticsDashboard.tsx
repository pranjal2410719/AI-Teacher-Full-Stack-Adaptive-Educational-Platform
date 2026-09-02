import React, { useState, useEffect } from 'react';
import {
  Award,
  Clock,
  BookOpen,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  Sliders,
  Sparkles,
  Loader2,
  Activity,
  Zap,
  Target,
  History,
} from 'lucide-react';
import { LearnerProfile, TopicRecommendation } from '../../types';
import { api } from '../../services/api';

interface AnalyticsDashboardProps {
  profile: LearnerProfile;
  onOpenProfileModal: () => void;
  onSelectTopic: (topic: string) => void;
}

export const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({
  profile,
  onOpenProfileModal,
  onSelectTopic,
}) => {
  const [recommendations, setRecommendations] = useState<TopicRecommendation[]>([]);
  const [isLoadingRecs, setIsLoadingRecs] = useState(true);

  useEffect(() => {
    loadRecommendations();
  }, [profile.student_id]);

  const loadRecommendations = async () => {
    setIsLoadingRecs(true);
    try {
      const recs = await api.getRecommendations(profile.student_id);
      setRecommendations(recs);
    } catch (err) {
      console.error('Failed to load recommendations:', err);
    } finally {
      setIsLoadingRecs(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 space-y-6">

      {/* Top Profile Header Card */}
      <div className="relative overflow-hidden p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-900/20 via-transparent to-emerald-900/10 pointer-events-none" />

        <div className="relative flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-purple-600 to-indigo-500 flex items-center justify-center text-xl font-black text-white shadow-lg shadow-purple-600/30">
                {profile.name?.charAt(0) || 'L'}
              </div>
              <span className="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 rounded-full bg-emerald-400 border-2 border-slate-900 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <h2 className="text-xl font-extrabold text-slate-100 tracking-tight">
                  {profile.name || 'Learner'}
                </h2>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30 uppercase tracking-widest">
                  {profile.preferred_level}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Preferred Language:{' '}
                <span className="text-emerald-400 font-semibold">
                  {profile.preferred_language === 'hi' ? 'हिन्दी (Hindi)' : 'English'}
                </span>
              </p>
            </div>
          </div>

          <button
            onClick={onOpenProfileModal}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-purple-500/60 text-slate-300 hover:text-white text-xs font-semibold transition-all shadow-sm"
          >
            <Sliders className="w-3.5 h-3.5 text-purple-400" />
            <span>Edit Profile Preferences</span>
          </button>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="group relative overflow-hidden p-5 rounded-2xl bg-slate-900 border border-slate-800 hover:border-purple-500/40 transition-all">
          <div className="absolute inset-0 bg-gradient-to-br from-purple-900/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
          <div className="flex items-center gap-2 text-xs text-slate-400 font-medium mb-2">
            <div className="p-1.5 rounded-lg bg-purple-500/10 border border-purple-500/20">
              <BookOpen className="w-3.5 h-3.5 text-purple-400" />
            </div>
            <span>Lessons Completed</span>
          </div>
          <p className="text-3xl font-black text-slate-100 font-mono tracking-tight">
            {profile.total_lessons_completed}
          </p>
        </div>

        <div className="group relative overflow-hidden p-5 rounded-2xl bg-slate-900 border border-slate-800 hover:border-emerald-500/40 transition-all">
          <div className="absolute inset-0 bg-gradient-to-br from-emerald-900/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
          <div className="flex items-center gap-2 text-xs text-slate-400 font-medium mb-2">
            <div className="p-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
              <Award className="w-3.5 h-3.5 text-emerald-400" />
            </div>
            <span>Average Mastery</span>
          </div>
          <p className="text-3xl font-black text-emerald-400 font-mono tracking-tight">
            {profile.average_mastery_percent.toFixed(0)}%
          </p>
        </div>

        <div className="group relative overflow-hidden p-5 rounded-2xl bg-slate-900 border border-slate-800 hover:border-indigo-500/40 transition-all">
          <div className="absolute inset-0 bg-gradient-to-br from-indigo-900/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
          <div className="flex items-center gap-2 text-xs text-slate-400 font-medium mb-2">
            <div className="p-1.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20">
              <Clock className="w-3.5 h-3.5 text-indigo-400" />
            </div>
            <span>Total Study Time</span>
          </div>
          <p className="text-3xl font-black text-indigo-400 font-mono tracking-tight">
            {profile.total_time_spent_min || profile.total_lessons_completed * 15}{' '}
            <span className="text-lg font-semibold text-slate-500">min</span>
          </p>
        </div>
      </div>

      {/* Concept Mastery + Weak Areas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-5">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-orange-500/10 border border-orange-500/20">
              <TrendingUp className="w-3.5 h-3.5 text-orange-400" />
            </div>
            <span>Conceptual Mastery Index</span>
          </h3>

          {Object.keys(profile.concept_mastery || {}).length > 0 ? (
            <div className="space-y-4">
              {Object.entries(profile.concept_mastery).map(([concept, val], idx) => {
                const pct = Math.round((val as number) * 100);
                const isStrong = pct >= 75;
                return (
                  <div key={idx} className="space-y-1.5">
                    <div className="flex justify-between text-xs font-medium text-slate-300">
                      <span>{concept}</span>
                      <span className={`font-mono font-bold ${isStrong ? 'text-emerald-400' : 'text-amber-400'}`}>
                        {pct}%
                      </span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-700 ${
                          isStrong
                            ? 'bg-gradient-to-r from-emerald-500 to-teal-400'
                            : 'bg-gradient-to-r from-amber-500 to-orange-400'
                        }`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="py-8 text-center">
              <Activity className="w-8 h-8 mx-auto mb-3 text-slate-700" />
              <p className="text-slate-500 text-xs leading-relaxed max-w-xs mx-auto">
                Complete your first lesson and assessment to track concept mastery metrics.
              </p>
            </div>
          )}
        </div>

        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-5">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-amber-500/10 border border-amber-500/20">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            </div>
            <span>Targeted Gaps &amp; Prerequisite Refreshers</span>
          </h3>

          {profile.known_weak_areas && profile.known_weak_areas.length > 0 ? (
            <div className="space-y-2.5">
              {profile.known_weak_areas.map((weak, idx) => (
                <button
                  key={idx}
                  onClick={() => onSelectTopic(weak)}
                  className="w-full p-3 rounded-xl bg-slate-800/60 border border-amber-900/30 hover:border-amber-500/50 hover:bg-slate-800 cursor-pointer flex items-center justify-between transition-all group text-left"
                >
                  <div className="flex items-center gap-2.5 text-xs text-slate-300">
                    <span className="w-2 h-2 rounded-full bg-amber-400 flex-shrink-0" />
                    <span>{weak}</span>
                  </div>
                  <span className="text-[10px] font-semibold text-amber-400 group-hover:text-amber-300 flex items-center gap-1 transition-colors flex-shrink-0">
                    <span>Review</span>
                    <ChevronRight className="w-3 h-3" />
                  </span>
                </button>
              ))}
            </div>
          ) : (
            <div className="py-8 text-center">
              <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mx-auto mb-3">
                <CheckCircle2 className="w-6 h-6 text-emerald-400" />
              </div>
              <p className="text-emerald-400/80 text-xs font-medium">No critical mastery gaps detected.</p>
              <p className="text-slate-500 text-[11px] mt-1">Keep up the great work!</p>
            </div>
          )}
        </div>
      </div>

      {/* AI Recommendations */}
      <div className="relative overflow-hidden p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-5">
        <div className="absolute top-0 right-0 w-64 h-64 bg-purple-600/5 rounded-full blur-3xl pointer-events-none" />

        <div className="relative flex items-center justify-between">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-purple-500/10 border border-purple-500/20">
              <Sparkles className="w-3.5 h-3.5 text-purple-400" />
            </div>
            <span>AI Teacher Adaptive Recommendations</span>
          </h3>
          <span className="text-[10px] text-slate-500 font-mono bg-slate-800 px-2 py-0.5 rounded-full border border-slate-700">
            Personalized for you
          </span>
        </div>

        {isLoadingRecs ? (
          <div className="flex items-center gap-3 text-slate-400 text-xs py-6 justify-center">
            <Loader2 className="w-4 h-4 animate-spin text-purple-400" />
            <span>Calculating next optimal learning steps...</span>
          </div>
        ) : recommendations.length > 0 ? (
          <div className="relative grid grid-cols-1 sm:grid-cols-2 gap-3">
            {recommendations.map((rec, idx) => (
              <button
                key={idx}
                onClick={() => onSelectTopic(rec.topic)}
                className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/60 hover:border-purple-500/50 hover:bg-slate-800 cursor-pointer transition-all space-y-2 group text-left"
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30 uppercase tracking-wider">
                    {rec.level}
                  </span>
                  <ChevronRight className="w-4 h-4 text-slate-600 group-hover:text-purple-400 transition-colors" />
                </div>
                <h4 className="font-bold text-slate-200 text-xs group-hover:text-purple-300 transition-colors leading-snug">
                  {rec.topic}
                </h4>
                {rec.rationale && (
                  <p className="text-[11px] text-slate-500 leading-tight">{rec.rationale}</p>
                )}
              </button>
            ))}
          </div>
        ) : (
          <div className="py-6 text-center">
            <Zap className="w-8 h-8 mx-auto mb-3 text-slate-700" />
            <p className="text-slate-500 text-xs">Complete a lesson to unlock personalized recommendations.</p>
          </div>
        )}
      </div>

      {/* Learning History Timeline */}
      {profile.learning_history && profile.learning_history.length > 0 && (
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20">
              <History className="w-3.5 h-3.5 text-indigo-400" />
            </div>
            <span>Recent Learning Session History</span>
          </h3>
          <div className="space-y-2">
            {profile.learning_history.map((hist, i) => (
              <div
                key={i}
                className="p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/50 flex items-center justify-between text-xs hover:border-slate-600 transition-colors"
              >
                <div>
                  <span className="font-semibold text-slate-200">{hist.lesson_id}</span>
                  <p className="text-[10px] text-slate-500 mt-0.5">
                    {new Date(hist.date).toLocaleString()}
                  </p>
                </div>
                <div className="flex items-center gap-1.5">
                  <Target className="w-3 h-3 text-emerald-400" />
                  <span className="font-mono text-emerald-400 font-bold">
                    {hist.score.toFixed(0)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
