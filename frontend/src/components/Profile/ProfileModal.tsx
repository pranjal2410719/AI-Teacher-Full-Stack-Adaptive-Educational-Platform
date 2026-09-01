import React, { useState } from 'react';
import { X, User, Sliders, Globe, Clock, Target, Check, Sparkles } from 'lucide-react';
import { LearnerProfile, LearnerLevel, LanguageCode } from '../../types';

interface ProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
  profile: LearnerProfile;
  onSaveProfile: (updates: {
    name: string;
    level: LearnerLevel;
    language: LanguageCode;
    timeBudgetMin: number;
    priorKnowledge?: string;
    learningGoal?: string;
  }) => void;
}

export const ProfileModal: React.FC<ProfileModalProps> = ({
  isOpen,
  onClose,
  profile,
  onSaveProfile,
}) => {
  const [name, setName] = useState(profile.name || 'Learner');
  const [level, setLevel] = useState<LearnerLevel>(profile.preferred_level || 'intermediate');
  const [language, setLanguage] = useState<LanguageCode>(profile.preferred_language || 'en');
  const [timeBudgetMin, setTimeBudgetMin] = useState(15);
  const [priorKnowledge, setPriorKnowledge] = useState('');
  const [learningGoal, setLearningGoal] = useState('');

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSaveProfile({
      name,
      level,
      language,
      timeBudgetMin,
      priorKnowledge,
      learningGoal,
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#2b1a07]/70 backdrop-blur-sm animate-in fade-in">
      <div className="w-full max-w-xl bg-slate-900 border border-slate-800 rounded-[12px] shadow-[rgba(0,0,0,0.06)_0px_2px_20px_0px] overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/60">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-[8px] bg-slate-800 border border-slate-800 text-[#ff6f1e]">
              <Sliders className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-slate-400 text-sm">Learner Profile Configuration</h3>
              <p className="text-[11px] text-slate-400/60">Personalize AI Teacher pedagogical style & time budget</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-[8px] text-slate-400/60 hover:text-slate-400 hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5 overflow-y-auto flex-1 text-xs">
          {/* Name */}
          <div>
            <label className="block font-semibold text-slate-400/70 mb-1.5 flex items-center gap-1.5">
              <User className="w-3.5 h-3.5 text-[#ff6f1e]" />
              <span>Learner Name</span>
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-[8px] bg-slate-900 border border-slate-800 text-slate-400 text-xs focus:outline-none focus:border-purple-500"
              placeholder="e.g. Alex"
            />
          </div>

          {/* Educational Level Selection */}
          <div>
            <label className="block font-semibold text-slate-400/70 mb-2">Target Educational Level</label>
            <div className="grid grid-cols-3 gap-2.5">
              {[
                {
                  id: 'beginner',
                  label: 'Beginner',
                  desc: 'Intuitive analogies, scaffolding, zero jargon',
                },
                {
                  id: 'intermediate',
                  label: 'Intermediate',
                  desc: 'Balanced theory, code/math mechanics, derivations',
                },
                {
                  id: 'advanced',
                  label: 'Advanced',
                  desc: 'Formal proofs, edge cases, asymptotic bounds',
                },
              ].map((lvl) => (
                <div
                  key={lvl.id}
                  onClick={() => setLevel(lvl.id as LearnerLevel)}
                  className={`p-3 rounded-[8px] border cursor-pointer transition-all ${
                    level === lvl.id
                      ? 'border-purple-500 bg-slate-800/40 text-[#ff6f1e] shadow-sm'
                      : 'border-slate-800 bg-slate-900/60 hover:border-slate-800 text-slate-400/60'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold text-slate-400">{lvl.label}</span>
                    {level === lvl.id && <Check className="w-3.5 h-3.5 text-[#ff6f1e]" />}
                  </div>
                  <p className="text-[10px] text-slate-400/60 leading-tight">{lvl.desc}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Preferred Language */}
          <div>
            <label className="block font-semibold text-slate-400/70 mb-1.5 flex items-center gap-1.5">
              <Globe className="w-3.5 h-3.5 text-[#22c55e]" />
              <span>Teaching Language</span>
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setLanguage('en')}
                className={`py-2 px-3 rounded-[8px] border text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
                  language === 'en'
                    ? 'border-emerald-500 bg-emerald-950/40 text-emerald-300'
                    : 'border-slate-800 bg-slate-900/60 text-slate-400/60 hover:border-slate-800'
                }`}
              >
                <span>English (US Neural)</span>
              </button>
              <button
                type="button"
                onClick={() => setLanguage('hi')}
                className={`py-2 px-3 rounded-[8px] border text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
                  language === 'hi'
                    ? 'border-emerald-500 bg-emerald-950/40 text-emerald-300'
                    : 'border-slate-800 bg-slate-900/60 text-slate-400/60 hover:border-slate-800'
                }`}
              >
                <span>हिन्दी (Hindi Devanagari)</span>
              </button>
            </div>
          </div>

          {/* Time Budget Slider */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="font-semibold text-slate-400/70 flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-indigo-400" />
                <span>Time Budget</span>
              </label>
              <span className="font-mono text-[#ff6f1e] font-bold">{timeBudgetMin} Minutes</span>
            </div>
            <input
              type="range"
              min={5}
              max={60}
              step={5}
              value={timeBudgetMin}
              onChange={(e) => setTimeBudgetMin(Number(e.target.value))}
              className="w-full accent-purple-500 cursor-pointer bg-slate-800"
            />
            <div className="flex justify-between text-[10px] text-slate-400/50 mt-1 font-mono">
              <span>5 min (Bite-sized)</span>
              <span>15 min (Standard)</span>
              <span>30 min (Comprehensive)</span>
              <span>60 min (Deep Dive)</span>
            </div>
          </div>

          {/* Learning Goal */}
          <div>
            <label className="block font-semibold text-slate-400/70 mb-1.5 flex items-center gap-1.5">
              <Target className="w-3.5 h-3.5 text-[#ff6f1e]" />
              <span>Specific Learning Goal or Exam Target</span>
            </label>
            <input
              type="text"
              value={learningGoal}
              onChange={(e) => setLearningGoal(e.target.value)}
              className="w-full px-3.5 py-2 rounded-[8px] bg-slate-900 border border-slate-800 text-slate-400 text-xs focus:outline-none focus:border-purple-500"
              placeholder="e.g., Master limit evaluation for calculus exam, or interview prep on tree traversal"
            />
          </div>

          {/* Modal Footer */}
          <div className="pt-3 border-t border-slate-800 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-[8px] text-slate-400/60 hover:text-slate-400 text-xs font-semibold transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2.5 rounded-[8px] bg-purple-600 hover:bg-purple-600 text-white text-xs font-bold flex items-center gap-2 shadow-[rgba(0,0,0,0.15)] shadow-purple-600/25 transition-all"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Save & Generate Plan</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
