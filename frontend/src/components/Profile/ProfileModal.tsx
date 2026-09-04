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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in">
      <div className="w-full max-w-xl bg-white border border-gray-200 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-slate-50">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-blue-50 border border-blue-200 text-blue-900">
              <Sliders className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-blue-950 text-sm">Learner Profile Configuration</h3>
              <p className="text-[11px] text-slate-500">Personalize ApniHelp pedagogical style &amp; time budget</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5 overflow-y-auto flex-1 text-xs">
          {/* Name */}
          <div>
            <label className="block font-bold text-slate-900 mb-1.5 flex items-center gap-1.5">
              <User className="w-3.5 h-3.5 text-blue-900" />
              <span>Learner Name</span>
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-white border border-gray-300 text-slate-900 placeholder:text-slate-400 text-xs focus:outline-none focus:border-blue-900 focus:ring-1 focus:ring-blue-900 shadow-xs"
              placeholder="e.g. Alex"
            />
          </div>

          {/* Educational Level Selection */}
          <div>
            <label className="block font-bold text-slate-900 mb-2">Target Educational Level</label>
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
                <button
                  type="button"
                  key={lvl.id}
                  onClick={() => setLevel(lvl.id as LearnerLevel)}
                  className={`p-3.5 rounded-xl border text-left cursor-pointer transition-all ${
                    level === lvl.id
                      ? 'border-2 border-blue-900 bg-blue-50 text-blue-950 font-bold shadow-xs'
                      : 'border-gray-200 bg-slate-50 hover:border-blue-300 hover:bg-blue-50/30 text-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold text-slate-900">{lvl.label}</span>
                    {level === lvl.id && <Check className="w-3.5 h-3.5 text-blue-900" />}
                  </div>
                  <p className="text-[11px] text-slate-500 leading-tight">{lvl.desc}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Preferred Language */}
          <div>
            <label className="block font-bold text-slate-900 mb-1.5 flex items-center gap-1.5">
              <Globe className="w-3.5 h-3.5 text-blue-900" />
              <span>Teaching Language</span>
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setLanguage('en')}
                className={`py-2.5 px-3 rounded-xl border text-xs font-semibold flex items-center justify-center gap-2 transition-all cursor-pointer ${
                  language === 'en'
                    ? 'border-2 border-blue-900 bg-blue-50 text-blue-950 font-bold shadow-xs'
                    : 'border-gray-200 bg-slate-50 text-slate-700 hover:border-blue-300 hover:bg-blue-50/30'
                }`}
              >
                <span>English (Neural Voice)</span>
              </button>
              <button
                type="button"
                onClick={() => setLanguage('hi')}
                className={`py-2.5 px-3 rounded-xl border text-xs font-semibold flex items-center justify-center gap-2 transition-all cursor-pointer ${
                  language === 'hi'
                    ? 'border-2 border-blue-900 bg-blue-50 text-blue-950 font-bold shadow-xs'
                    : 'border-gray-200 bg-slate-50 text-slate-700 hover:border-blue-300 hover:bg-blue-50/30'
                }`}
              >
                <span>हिन्दी (Hindi Devanagari)</span>
              </button>
            </div>
          </div>

          {/* Time Budget Slider */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="font-bold text-slate-900 flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-blue-900" />
                <span>Time Budget</span>
              </label>
              <span className="font-mono text-blue-900 font-bold">{timeBudgetMin} Minutes</span>
            </div>
            <input
              type="range"
              min={5}
              max={60}
              step={5}
              value={timeBudgetMin}
              onChange={(e) => setTimeBudgetMin(Number(e.target.value))}
              className="w-full accent-blue-900 cursor-pointer bg-slate-200 rounded-lg h-2"
            />
            <div className="flex justify-between text-[10px] text-slate-500 mt-1 font-mono">
              <span>5 min (Bite-sized)</span>
              <span>15 min (Standard)</span>
              <span>30 min (Comprehensive)</span>
              <span>60 min (Deep Dive)</span>
            </div>
          </div>

          {/* Learning Goal */}
          <div>
            <label className="block font-bold text-slate-900 mb-1.5 flex items-center gap-1.5">
              <Target className="w-3.5 h-3.5 text-blue-900" />
              <span>Specific Learning Goal or Exam Target</span>
            </label>
            <input
              type="text"
              value={learningGoal}
              onChange={(e) => setLearningGoal(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-white border border-gray-300 text-slate-900 placeholder:text-slate-400 text-xs focus:outline-none focus:border-blue-900 focus:ring-1 focus:ring-blue-900 shadow-xs"
              placeholder="e.g., Master limit evaluation for calculus exam, or interview prep on tree traversal"
            />
          </div>

          {/* Modal Footer */}
          <div className="pt-3 border-t border-gray-200 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 text-xs font-semibold transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2.5 rounded-xl bg-yellow-400 hover:bg-yellow-500 active:bg-yellow-600 text-slate-950 text-xs font-black flex items-center gap-2 shadow-md shadow-yellow-500/20 transition-all cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5 text-slate-950" />
              <span>Save Preferences</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
