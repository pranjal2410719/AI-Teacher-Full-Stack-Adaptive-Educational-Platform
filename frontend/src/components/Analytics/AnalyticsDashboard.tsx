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
      <div className="relative overflow-hidden p-6 rounded-2xl bg-white border border-gray-200 shadow-sm">
        <div className="relative flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="w-14 h-14 rounded-2xl bg-blue-900 flex items-center justify-center text-xl font-black text-yellow-400 shadow-sm">
                {profile.name?.charAt(0) || 'L'}
              </div>
              <span className="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 rounded-full bg-emerald-500 border-2 border-white animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <h2 className="text-xl font-black text-blue-950 tracking-tight">
                  {profile.name || 'Learner'}
                </h2>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-800 border border-yellow-300 uppercase tracking-widest font-bold">
                  {profile.preferred_level}
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                Preferred Language:{' '}
                <span className="text-blue-900 font-bold">
                  {profile.preferred_language === 'hi' ? 'हिन्दी (Hindi)' : 'English'}
                </span>
              </p>
            </div>
          </div>

          <button
            onClick={onOpenProfileModal}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 border border-gray-200 text-slate-800 text-xs font-semibold transition-all shadow-xs cursor-pointer"
          >
            <Sliders className="w-3.5 h-3.5 text-blue-900" />
            <span>Edit Profile Preferences</span>
          </button>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-5 rounded-2xl bg-white border border-gray-200 shadow-sm hover:border-blue-300 transition-all">
          <div className="flex items-center gap-2 text-xs text-slate-500 font-semibold mb-2">
            <div className="p-1.5 rounded-lg bg-blue-50 border border-blue-200 text-blue-900">
              <BookOpen className="w-3.5 h-3.5" />
            </div>
            <span>Lessons Completed</span>
          </div>
          <p className="text-3xl font-black text-blue-950 font-mono tracking-tight">
            {profile.total_lessons_completed}
          </p>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-gray-200 shadow-sm hover:border-emerald-300 transition-all">
          <div className="flex items-center gap-2 text-xs text-slate-500 font-semibold mb-2">
            <div className="p-1.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-700">
              <Award className="w-3.5 h-3.5" />
            </div>
            <span>Average Mastery</span>
          </div>
          <p className="text-3xl font-black text-emerald-700 font-mono tracking-tight">
            {profile.average_mastery_percent.toFixed(0)}%
          </p>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-gray-200 shadow-sm hover:border-blue-300 transition-all">
          <div className="flex items-center gap-2 text-xs text-slate-500 font-semibold mb-2">
            <div className="p-1.5 rounded-lg bg-blue-50 border border-blue-200 text-blue-900">
              <Clock className="w-3.5 h-3.5" />
            </div>
            <span>Total Study Time</span>
          </div>
          <p className="text-3xl font-black text-blue-900 font-mono tracking-tight">
            {profile.total_time_spent_min || profile.total_lessons_completed * 15}{' '}
            <span className="text-lg font-semibold text-slate-500">min</span>
          </p>
        </div>
      </div>

      {/* Concept Mastery + Weak Areas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <div className="p-6 rounded-2xl bg-white border border-gray-200 shadow-sm space-y-5">
          <h3 className="text-xs font-bold text-slate-700 uppercase tracking-widest flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-blue-50 border border-blue-200 text-blue-900">
              <TrendingUp className="w-3.5 h-3.5" />
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
                    <div className="flex justify-between text-xs font-bold text-slate-800">
                      <span>{concept}</span>
                      <span className={`font-mono font-bold ${isStrong ? 'text-emerald-700' : 'text-amber-600'}`}>
                        {pct}%
                      </span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden border border-gray-200">
                      <div
                        className={`h-full rounded-full transition-all duration-700 ${
                          isStrong ? 'bg-emerald-500' : 'bg-yellow-400'
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
              <Activity className="w-8 h-8 mx-auto mb-3 text-slate-400" />
              <p className="text-slate-500 text-xs leading-relaxed max-w-xs mx-auto">
                Complete your first lesson and assessment to track concept mastery metrics.
              </p>
            </div>
          )}
        </div>

        <div className="p-6 rounded-2xl bg-white border border-gray-200 shadow-sm space-y-5">
          <h3 className="text-xs font-bold text-slate-700 uppercase tracking-widest flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-amber-50 border border-amber-200 text-amber-800">
              <AlertTriangle className="w-3.5 h-3.5" />
            </div>
            <span>Targeted Gaps &amp; Prerequisite Refreshers</span>
          </h3>

          {profile.known_weak_areas && profile.known_weak_areas.length > 0 ? (
            <div className="space-y-2.5">
              {profile.known_weak_areas.map((weak, idx) => (
                <button
                  key={idx}
                  onClick={() => onSelectTopic(weak)}
                  className="w-full p-3 rounded-xl bg-slate-50 border border-gray-200 hover:border-blue-400 hover:bg-blue-50/40 cursor-pointer flex items-center justify-between transition-all group text-left"
                >
                  <div className="flex items-center gap-2.5 text-xs text-slate-800">
                    <span className="w-2 h-2 rounded-full bg-amber-500 flex-shrink-0" />
                    <span className="font-medium group-hover:text-blue-950">{weak}</span>
                  </div>
                  <span className="text-[10px] font-bold text-blue-900 group-hover:text-blue-950 flex items-center gap-1 transition-colors flex-shrink-0">
                    <span>Review</span>
                    <ChevronRight className="w-3 h-3" />
                  </span>
                </button>
              ))}
            </div>
          ) : (
            <div className="py-8 text-center">
              <div className="w-12 h-12 rounded-2xl bg-emerald-50 border border-emerald-200 flex items-center justify-center mx-auto mb-3 text-emerald-700">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <p className="text-emerald-800 text-xs font-bold">No critical mastery gaps detected.</p>
              <p className="text-slate-500 text-[11px] mt-1">Keep up the great work!</p>
            </div>
          )}
        </div>
      </div>

      {/* AI Recommendations */}
      <div className="relative overflow-hidden p-6 rounded-2xl bg-white border border-gray-200 shadow-sm space-y-5">
        <div className="relative flex items-center justify-between">
          <h3 className="text-xs font-bold text-slate-700 uppercase tracking-widest flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-blue-50 border border-blue-200 text-blue-900">
              <Sparkles className="w-3.5 h-3.5" />
            </div>
            <span>ApniHelp Adaptive Recommendations</span>
          </h3>
          <span className="text-[10px] text-slate-600 font-mono bg-slate-100 px-2.5 py-0.5 rounded-full border border-gray-200 font-semibold">
            Personalized for you
          </span>
        </div>

        {isLoadingRecs ? (
          <div className="flex items-center gap-3 text-slate-500 text-xs py-6 justify-center">
            <Loader2 className="w-4 h-4 animate-spin text-blue-900" />
            <span>Calculating next optimal learning steps...</span>
          </div>
        ) : recommendations.length > 0 ? (
          <div className="relative grid grid-cols-1 sm:grid-cols-2 gap-3">
            {recommendations.map((rec, idx) => (
              <button
                key={idx}
                onClick={() => onSelectTopic(rec.topic)}
                className="p-4 rounded-xl bg-slate-50 border border-gray-200 hover:border-blue-400 hover:bg-blue-50/50 cursor-pointer transition-all space-y-2 group text-left shadow-xs"
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-blue-100 text-blue-900 border border-blue-200 uppercase tracking-wider font-bold">
                    {rec.level}
                  </span>
                  <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-blue-900 transition-colors" />
                </div>
                <h4 className="font-bold text-slate-900 text-xs group-hover:text-blue-950 transition-colors leading-snug">
                  {rec.topic}
                </h4>
                {rec.rationale && (
                  <p className="text-[11px] text-slate-600 leading-tight">{rec.rationale}</p>
                )}
              </button>
            ))}
          </div>
        ) : (
          <div className="py-6 text-center">
            <Zap className="w-8 h-8 mx-auto mb-3 text-slate-400" />
            <p className="text-slate-500 text-xs">Complete a lesson to unlock personalized recommendations.</p>
          </div>
        )}
      </div>

      {/* Learning History Timeline */}
      {profile.learning_history && profile.learning_history.length > 0 && (
        <div className="p-6 rounded-2xl bg-white border border-gray-200 shadow-sm space-y-4">
          <h3 className="text-xs font-bold text-slate-700 uppercase tracking-widest flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-blue-50 border border-blue-200 text-blue-900">
              <History className="w-3.5 h-3.5" />
            </div>
            <span>Recent Learning Session History</span>
          </h3>
          <div className="space-y-2">
            {profile.learning_history.map((hist, i) => (
              <div
                key={i}
                className="p-3.5 rounded-xl bg-slate-50 border border-gray-200 flex items-center justify-between text-xs hover:border-blue-300 transition-colors"
              >
                <div>
                  <span className="font-bold text-slate-900">{hist.lesson_id}</span>
                  <p className="text-[10px] text-slate-500 mt-0.5">
                    {new Date(hist.date).toLocaleString()}
                  </p>
                </div>
                <div className="flex items-center gap-1.5">
                  <Target className="w-3 h-3 text-emerald-600" />
                  <span className="font-mono text-emerald-700 font-bold">
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
