import React, { useState, useEffect } from 'react';
import {
  User,
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
      <div className="p-6 rounded-[12px] bg-[#fdfbf9] border border-[#171717] shadow-[rgba(0,0,0,0.06)_0px_2px_20px_0px] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-[12px] bg-gradient-to-tr from-purple-600 to-indigo-600 p-0.5 shadow-[rgba(0,0,0,0.15)] shadow-purple-600/30">
            <div className="w-full h-full bg-[#fdfbf9] rounded-[14px] flex items-center justify-center text-xl font-bold text-white">
              {profile.name?.charAt(0) || 'L'}
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold text-[#2b1a07]">{profile.name || 'Learner'}</h2>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-[20px] bg-[#f7efe9] text-[#ff6f1e] border border-purple-800/50">
                {profile.preferred_level.toUpperCase()}
              </span>
            </div>
            <p className="text-xs text-[#2b1a07]/60 mt-0.5">
              Preferred Language: <span className="text-[#22c55e] font-semibold">{profile.preferred_language === 'hi' ? 'हिन्दी (Hindi)' : 'English'}</span>
            </p>
          </div>
        </div>

        <button
          onClick={onOpenProfileModal}
          className="px-4 py-2 rounded-[8px] bg-[#f7efe9] hover:bg-slate-700 text-[#2b1a07] text-xs font-semibold flex items-center gap-2 transition-colors"
        >
          <Sliders className="w-3.5 h-3.5" />
          <span>Edit Profile Preferences</span>
        </button>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-5 rounded-[12px] bg-[#fdfbf9]/90 border border-[#171717] space-y-1">
          <div className="flex items-center gap-2 text-xs text-[#2b1a07]/60 font-medium">
            <BookOpen className="w-4 h-4 text-[#ff6f1e]" />
            <span>Lessons Completed</span>
          </div>
          <p className="text-2xl font-black text-[#2b1a07] font-mono">
            {profile.total_lessons_completed}
          </p>
        </div>

        <div className="p-5 rounded-[12px] bg-[#fdfbf9]/90 border border-[#171717] space-y-1">
          <div className="flex items-center gap-2 text-xs text-[#2b1a07]/60 font-medium">
            <Award className="w-4 h-4 text-[#22c55e]" />
            <span>Average Mastery</span>
          </div>
          <p className="text-2xl font-black text-[#22c55e] font-mono">
            {profile.average_mastery_percent.toFixed(0)}%
          </p>
        </div>

        <div className="p-5 rounded-[12px] bg-[#fdfbf9]/90 border border-[#171717] space-y-1">
          <div className="flex items-center gap-2 text-xs text-[#2b1a07]/60 font-medium">
            <Clock className="w-4 h-4 text-indigo-400" />
            <span>Total Study Time</span>
          </div>
          <p className="text-2xl font-black text-indigo-300 font-mono">
            {profile.total_time_spent_min || (profile.total_lessons_completed * 15)} min
          </p>
        </div>
      </div>

      {/* Concept Mastery & Weak Areas Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Concept Mastery Bars */}
        <div className="p-6 rounded-[12px] bg-[#fdfbf9] border border-[#171717] space-y-4">
          <h3 className="text-xs font-bold text-[#2b1a07]/70 uppercase tracking-wider flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-[#ff6f1e]" />
            <span>Conceptual Mastery Index</span>
          </h3>

          {Object.keys(profile.concept_mastery || {}).length > 0 ? (
            <div className="space-y-3">
              {Object.entries(profile.concept_mastery).map(([concept, val], idx) => {
                const pct = Math.round((val as number) * 100);
                return (
                  <div key={idx} className="space-y-1">
                    <div className="flex justify-between text-xs font-medium text-[#2b1a07]/70">
                      <span>{concept}</span>
                      <span className="font-mono text-[#ff6f1e] font-bold">{pct}%</span>
                    </div>
                    <div className="w-full h-2 rounded-[20px] bg-[#fdfbf9] overflow-hidden">
                      <div
                        className={`h-full rounded-[20px] transition-all ${
                          pct >= 75
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
            <div className="p-6 text-center text-[#2b1a07]/50 text-xs border border-dashed border-[#171717] rounded-[8px]">
              Complete your first lesson and assessment to track concept mastery metrics.
            </div>
          )}
        </div>

        {/* Known Weak Areas & Refresher Triggers */}
        <div className="p-6 rounded-[12px] bg-[#fdfbf9] border border-[#171717] space-y-4">
          <h3 className="text-xs font-bold text-[#2b1a07]/70 uppercase tracking-wider flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <span>Targeted Gaps & Prerequisite Refreshers</span>
          </h3>

          {profile.known_weak_areas && profile.known_weak_areas.length > 0 ? (
            <div className="space-y-2">
              {profile.known_weak_areas.map((weak, idx) => (
                <div
                  key={idx}
                  onClick={() => onSelectTopic(weak)}
                  className="p-3 rounded-[8px] bg-[#fdfbf9] border border-amber-900/30 hover:border-amber-700/60 cursor-pointer flex items-center justify-between transition-colors group"
                >
                  <div className="flex items-center gap-2 text-xs text-amber-200">
                    <span className="w-2 h-2 rounded-[20px] bg-amber-400" />
                    <span>{weak}</span>
                  </div>
                  <span className="text-[10px] font-semibold text-[#ff6f1e] group-hover:underline flex items-center gap-1">
                    <span>Review Refresher</span>
                    <ChevronRight className="w-3 h-3" />
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-6 text-center text-[#22c55e]/90 text-xs border border-dashed border-emerald-900/30 rounded-[8px] bg-emerald-950/20">
              <CheckCircle2 className="w-6 h-6 mx-auto mb-1.5 text-[#22c55e]" />
              <span>No critical mastery gaps detected. Keep up the great work!</span>
            </div>
          )}
        </div>
      </div>

      {/* Personalized Next-Topic Recommendations */}
      <div className="p-6 rounded-[12px] bg-[#fdfbf9] border border-[#171717]/60 shadow-[rgba(0,0,0,0.06)_0px_2px_20px_0px] space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold text-[#2b1a07] uppercase tracking-wider flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-[#ff6f1e]" />
            <span>AI Teacher Adaptive Recommendations</span>
          </h3>
          <span className="text-[10px] text-[#2b1a07]/50 font-mono">Personalized for you</span>
        </div>

        {isLoadingRecs ? (
          <div className="flex items-center gap-2 text-[#2b1a07]/60 text-xs py-4">
            <Loader2 className="w-4 h-4 animate-spin text-[#ff6f1e]" />
            <span>Calculating next optimal learning steps...</span>
          </div>
        ) : recommendations.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {recommendations.map((rec, idx) => (
              <div
                key={idx}
                onClick={() => onSelectTopic(rec.topic)}
                className="p-4 rounded-[8px] bg-[#fdfbf9] border border-[#171717] hover:border-[#ff6f1e]/80 cursor-pointer transition-all space-y-1.5 group"
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#f7efe9] text-[#ff6f1e] border border-[#171717]/60">
                    {rec.level.toUpperCase()}
                  </span>
                  <ChevronRight className="w-4 h-4 text-[#2b1a07]/50 group-hover:text-[#ff6f1e] transition-colors" />
                </div>
                <h4 className="font-bold text-[#2b1a07] text-xs group-hover:text-[#ff6f1e] transition-colors">
                  {rec.topic}
                </h4>
                {rec.rationale && (
                  <p className="text-[11px] text-[#2b1a07]/60 leading-tight">{rec.rationale}</p>
                )}
              </div>
            ))}
          </div>
        ) : null}
      </div>

      {/* Learning History Timeline */}
      {profile.learning_history && profile.learning_history.length > 0 && (
        <div className="p-6 rounded-[12px] bg-[#fdfbf9] border border-[#171717] space-y-3">
          <h3 className="text-xs font-bold text-[#2b1a07]/70 uppercase tracking-wider">
            Recent Learning Session History
          </h3>
          <div className="space-y-2">
            {profile.learning_history.map((hist, i) => (
              <div
                key={i}
                className="p-3 rounded-[8px] bg-[#fdfbf9] border border-[#171717] flex items-center justify-between text-xs"
              >
                <div>
                  <span className="font-semibold text-[#2b1a07]">{hist.lesson_id}</span>
                  <p className="text-[10px] text-[#2b1a07]/50">{new Date(hist.date).toLocaleString()}</p>
                </div>
                <span className="font-mono text-[#22c55e] font-bold">{hist.score.toFixed(0)}% Score</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
