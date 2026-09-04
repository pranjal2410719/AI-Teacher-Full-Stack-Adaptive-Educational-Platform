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
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-gray-200 shadow-sm px-4 lg:px-8 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => setCurrentTab('ingest')}>
          <div className="w-10 h-10 rounded-xl bg-blue-900 text-yellow-400 flex items-center justify-center shadow-sm">
            <GraduationCap className="w-6 h-6 text-yellow-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-black text-xl tracking-tight text-blue-950">
                ApniHelp
              </span>
              <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-800 border border-yellow-300">
                Adaptive
              </span>
            </div>
            <p className="text-xs text-slate-500 hidden sm:block">Full-Stack Adaptive Educational Platform</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="hidden md:flex items-center gap-1 bg-slate-100 p-1 rounded-xl border border-gray-200 text-xs font-medium">
          <button
            onClick={() => setCurrentTab('ingest')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all ${
              currentTab === 'ingest'
                ? 'bg-white text-blue-950 shadow-sm border border-gray-200 font-bold'
                : 'text-slate-600 hover:text-blue-950 hover:bg-slate-200/60'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5 text-blue-900" />
            <span>Generate Video</span>
          </button>
          {currentTab === 'plan' && (
            <button
              onClick={() => setCurrentTab('plan')}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all bg-white text-blue-950 shadow-sm border border-gray-200 font-bold"
            >
              <Sparkles className="w-3.5 h-3.5 text-blue-900" />
              <span>Lesson Plan</span>
            </button>
          )}
          <button
            onClick={() => setCurrentTab('video')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all ${
              currentTab === 'video'
                ? 'bg-white text-blue-950 shadow-sm border border-gray-200 font-bold'
                : 'text-slate-600 hover:text-blue-950 hover:bg-slate-200/60'
            }`}
          >
            <PlayCircle className="w-3.5 h-3.5 text-blue-900" />
            <span>Video & Checks</span>
          </button>
          <button
            onClick={() => setCurrentTab('quiz')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all ${
              currentTab === 'quiz'
                ? 'bg-white text-blue-950 shadow-sm border border-gray-200 font-bold'
                : 'text-slate-600 hover:text-blue-950 hover:bg-slate-200/60'
            }`}
          >
            <Award className="w-3.5 h-3.5 text-blue-900" />
            <span>Quiz & Report</span>
          </button>
          <button
            onClick={() => setCurrentTab('analytics')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all ${
              currentTab === 'analytics'
                ? 'bg-white text-blue-950 shadow-sm border border-gray-200 font-bold'
                : 'text-slate-600 hover:text-blue-950 hover:bg-slate-200/60'
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5 text-blue-900" />
            <span>Profile & Analytics</span>
          </button>
        </nav>

        {/* Right Actions */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Multilingual Switcher */}
          <button
            onClick={onToggleLanguage}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white hover:bg-slate-50 border border-gray-200 text-xs font-semibold text-slate-700 transition-colors shadow-sm"
            title="Switch Language (English / हिन्दी)"
          >
            <Globe className="w-3.5 h-3.5 text-blue-900" />
            <span className="font-bold text-blue-950">{currentLanguage === 'en' ? 'EN' : 'हिन्दी'}</span>
          </button>

          {/* Profile Badge */}
          <button
            onClick={onOpenProfile}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white hover:bg-slate-50 border border-gray-200 text-xs text-slate-800 transition-all shadow-sm"
          >
            <div className="w-6 h-6 rounded-full bg-blue-900 text-yellow-400 flex items-center justify-center text-[10px] font-black">
              {profile?.name?.charAt(0) || 'L'}
            </div>
            <span className="hidden sm:inline font-bold text-blue-950">{profile?.name || 'Learner'}</span>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-800 border border-yellow-300 font-mono font-bold">
              {profile?.preferred_level || 'Intermediate'}
            </span>
          </button>
        </div>
      </div>
    </header>
  );
};
