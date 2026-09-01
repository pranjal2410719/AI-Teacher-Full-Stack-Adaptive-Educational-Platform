import React from 'react';
import { GraduationCap, Globe, User, Sparkles, BookOpen, PlayCircle, Award, BarChart3 } from 'lucide-react';
import { LearnerProfile, LanguageCode } from '../types';

interface HeaderProps {
  currentTab: 'ingest' | 'plan' | 'video' | 'quiz' | 'analytics';
  setCurrentTab: (tab: 'ingest' | 'plan' | 'video' | 'quiz' | 'analytics') => void;
  profile: LearnerProfile | null;
  currentLanguage: LanguageCode;
  onToggleLanguage: () => void;
  onOpenProfile: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentTab,
  setCurrentTab,
  profile,
  currentLanguage,
  onToggleLanguage,
  onOpenProfile,
}) => {
  return (
    <header className="sticky top-0 z-40 bg-slate-900/90 backdrop-blur-md border-b border-slate-800/80 px-4 lg:px-8 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => setCurrentTab('ingest')}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 via-indigo-600 to-emerald-400 p-0.5 shadow-lg shadow-purple-500/20">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <GraduationCap className="w-6 h-6 text-purple-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-purple-400 via-indigo-200 to-emerald-300 bg-clip-text text-transparent">
                AI Teacher
              </span>
              <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
                Adaptive
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">Full-Stack Human Teaching Loop</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="hidden md:flex items-center gap-1 bg-slate-950/60 p-1 rounded-xl border border-slate-800/60 text-xs font-medium">
          <button
            onClick={() => setCurrentTab('ingest')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all ${
              currentTab === 'ingest'
                ? 'bg-purple-600 text-white shadow-md shadow-purple-600/30 font-semibold'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>1. Ingestion</span>
          </button>
          <button
            onClick={() => setCurrentTab('plan')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all ${
              currentTab === 'plan'
                ? 'bg-purple-600 text-white shadow-md shadow-purple-600/30 font-semibold'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>2. Lesson Plan</span>
          </button>
          <button
            onClick={() => setCurrentTab('video')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all ${
              currentTab === 'video'
                ? 'bg-purple-600 text-white shadow-md shadow-purple-600/30 font-semibold'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <PlayCircle className="w-3.5 h-3.5" />
            <span>3. Video & Checks</span>
          </button>
          <button
            onClick={() => setCurrentTab('quiz')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all ${
              currentTab === 'quiz'
                ? 'bg-purple-600 text-white shadow-md shadow-purple-600/30 font-semibold'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Award className="w-3.5 h-3.5" />
            <span>4. Quiz & Report</span>
          </button>
          <button
            onClick={() => setCurrentTab('analytics')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all ${
              currentTab === 'analytics'
                ? 'bg-purple-600 text-white shadow-md shadow-purple-600/30 font-semibold'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span>5. Profile & Analytics</span>
          </button>
        </nav>

        {/* Right Actions */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Multilingual Switcher */}
          <button
            onClick={onToggleLanguage}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-800 border border-slate-700 text-xs text-slate-200 transition-colors shadow-sm"
            title="Switch Language (English / हिन्दी)"
          >
            <Globe className="w-3.5 h-3.5 text-emerald-400" />
            <span className="font-semibold">{currentLanguage === 'en' ? 'EN' : 'हिन्दी'}</span>
          </button>

          {/* Profile Badge */}
          <button
            onClick={onOpenProfile}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gradient-to-r from-purple-950/80 to-slate-900 border border-purple-800/40 hover:border-purple-700 text-xs text-slate-200 transition-all shadow-sm"
          >
            <div className="w-5 h-5 rounded-full bg-purple-600 flex items-center justify-center text-[10px] font-bold text-white">
              {profile?.name?.charAt(0) || 'L'}
            </div>
            <span className="hidden sm:inline font-medium">{profile?.name || 'Learner'}</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-300 font-mono">
              {profile?.preferred_level || 'Intermediate'}
            </span>
          </button>
        </div>
      </div>
    </header>
  );
};
