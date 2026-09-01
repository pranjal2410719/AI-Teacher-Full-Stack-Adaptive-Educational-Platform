import React, { useState } from 'react';
import {
  Sparkles,
  ArrowUp,
  ArrowDown,
  Trash2,
  Plus,
  Play,
  CheckCircle2,
  HelpCircle,
  Code2,
  Sigma,
  GitGraph,
  History,
  Presentation,
  Loader2,
  Eye,
  Sliders
} from 'lucide-react';
import { LessonPlan, LessonSegmentPlan } from '../../types';

interface LessonPlanEditorProps {
  plan: LessonPlan;
  onUpdatePlan: (updatedPlan: LessonPlan) => void;
  onApproveAndGenerateVideo: () => void;
  isGeneratingVideo: boolean;
  videoProgressPercent?: number;
  videoCurrentStage?: string;
  onOpenProfileModal: () => void;
}

export const LessonPlanEditor: React.FC<LessonPlanEditorProps> = ({
  plan,
  onUpdatePlan,
  onApproveAndGenerateVideo,
  isGeneratingVideo,
  videoProgressPercent = 0,
  videoCurrentStage = '',
  onOpenProfileModal,
}) => {
  const [selectedSegment, setSelectedSegment] = useState<LessonSegmentPlan | null>(
    plan.modules[0] || null
  );

  const moveModule = (index: number, direction: 'up' | 'down') => {
    const newModules = [...plan.modules];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    if (targetIndex < 0 || targetIndex >= newModules.length) return;
    
    const temp = newModules[index];
    newModules[index] = newModules[targetIndex];
    newModules[targetIndex] = temp;

    // Recalculate orders
    newModules.forEach((m, idx) => { m.order = idx + 1; });
    onUpdatePlan({ ...plan, modules: newModules });
  };

  const updateScript = (segmentId: string, newScript: string) => {
    const newModules = plan.modules.map((m) =>
      m.segment_id === segmentId ? { ...m, script: newScript } : m
    );
    onUpdatePlan({ ...plan, modules: newModules });
    if (selectedSegment && selectedSegment.segment_id === segmentId) {
      setSelectedSegment({ ...selectedSegment, script: newScript });
    }
  };

  const getVisualIcon = (type: string) => {
    switch (type) {
      case 'math_equation': return <Sigma className="w-4 h-4 text-purple-400" />;
      case 'code_snippet': return <Code2 className="w-4 h-4 text-emerald-400" />;
      case 'diagram': return <GitGraph className="w-4 h-4 text-amber-400" />;
      case 'timeline': return <History className="w-4 h-4 text-purple-400" />;
      default: return <Presentation className="w-4 h-4 text-slate-400/60" />;
    }
  };

  const formatDuration = (totalSec: number) => {
    const min = Math.floor(totalSec / 60);
    const sec = totalSec % 60;
    return `${min}m ${sec > 0 ? `${sec}s` : ''}`;
  };

  return (
    <div className="max-w-6xl mx-auto py-6 px-4 space-y-6">
      {/* Header Bar */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-xs font-semibold uppercase tracking-wider text-purple-400">
              Personalized Lesson Blueprint
            </span>
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-800 text-purple-400 border border-slate-800/60 font-mono">
              {plan.level.toUpperCase()}
            </span>
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-600/40 font-mono">
              {plan.language.toUpperCase()}
            </span>
          </div>
          <h2 className="text-2xl font-bold text-slate-400">{plan.title}</h2>
          <p className="text-xs text-slate-400/60 mt-1">
            Total Target Duration: <span className="font-mono text-purple-400 font-semibold">{formatDuration(plan.target_duration_sec)}</span> • {plan.modules.length} Pedagogical Modules
          </p>
        </div>

        {/* Top Actions */}
        <div className="flex items-center gap-3">
          <button
            onClick={onOpenProfileModal}
            className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400/70 text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            <Sliders className="w-3.5 h-3.5" />
            <span>Customize Level/Time</span>
          </button>

          <button
            onClick={onApproveAndGenerateVideo}
            disabled={isGeneratingVideo}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 disabled:opacity-50 text-white text-xs font-bold flex items-center gap-2 shadow-lg shadow-purple-600/30 transition-all"
          >
            {isGeneratingVideo ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Generating Video ({videoProgressPercent}%)...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-white" />
                <span>Approve & Generate AI Video</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Video Generation Progress Bar */}
      {isGeneratingVideo && (
        <div className="p-4 rounded-2xl bg-slate-800/40 border border-slate-800/60 space-y-2">
          <div className="flex justify-between text-xs text-purple-400 font-medium">
            <span className="flex items-center gap-2">
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              <span>{videoCurrentStage || 'Synthesizing Neural TTS and 2.5D Viseme Avatar...'}</span>
            </span>
            <span className="font-mono font-bold">{videoProgressPercent}%</span>
          </div>
          <div className="w-full h-2 rounded-full bg-slate-900 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-purple-500 to-emerald-400 transition-all duration-300"
              style={{ width: `${videoProgressPercent}%` }}
            />
          </div>
        </div>
      )}

      {/* Main Two-Column Layout: Modules List & Module Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Modules Sequence List */}
        <div className="lg:col-span-6 space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-400/60 font-semibold px-1">
            <span>Pedagogical Sequence ({plan.modules.length})</span>
            <span>Duration</span>
          </div>

          <div className="space-y-2.5">
            {plan.modules.map((mod, idx) => {
              const isSelected = selectedSegment?.segment_id === mod.segment_id;
              return (
                <div
                  key={mod.segment_id}
                  onClick={() => setSelectedSegment(mod)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'border-purple-600 bg-slate-900/90 shadow-md shadow-purple-950/50'
                      : 'border-slate-800/80 bg-slate-900/60 hover:border-slate-800'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3">
                      <div className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400/70 mt-0.5">
                        {getVisualIcon(mod.visual_spec?.visual_type)}
                      </div>
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-[10px] font-mono text-purple-400 font-bold">
                            #{mod.order}
                          </span>
                          <h4 className="font-semibold text-slate-400 text-xs">{mod.title}</h4>
                        </div>
                        <p className="text-[11px] text-slate-400/60 line-clamp-1 leading-relaxed">
                          {mod.script}
                        </p>
                        {mod.checkpoint_question && (
                          <div className="mt-2 inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800/40">
                            <HelpCircle className="w-3 h-3 text-purple-400" />
                            <span>In-Video Checkpoint Pause</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Right Controls */}
                    <div className="flex flex-col items-end gap-2 flex-shrink-0" onClick={(e) => e.stopPropagation()}>
                      <span className="text-[11px] font-mono text-slate-400/60 font-medium">
                        {mod.duration_sec}s
                      </span>
                      <div className="flex items-center gap-1">
                        <button
                          disabled={idx === 0}
                          onClick={() => moveModule(idx, 'up')}
                          className="p-1 rounded text-slate-400/60 hover:text-slate-400 hover:bg-slate-800 disabled:opacity-30"
                        >
                          <ArrowUp className="w-3 h-3" />
                        </button>
                        <button
                          disabled={idx === plan.modules.length - 1}
                          onClick={() => moveModule(idx, 'down')}
                          className="p-1 rounded text-slate-400/60 hover:text-slate-400 hover:bg-slate-800 disabled:opacity-30"
                        >
                          <ArrowDown className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Detailed Module & Visual Spec Inspector */}
        <div className="lg:col-span-6">
          {selectedSegment ? (
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-5 sticky top-20">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <div className="p-2 rounded-xl bg-slate-800 text-purple-400 border border-slate-800/60">
                    {getVisualIcon(selectedSegment.visual_spec?.visual_type)}
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-400 text-sm">{selectedSegment.title}</h3>
                    <p className="text-[11px] text-slate-400/60">
                      Module Type: <span className="text-purple-400 font-mono">{selectedSegment.segment_type}</span>
                    </p>
                  </div>
                </div>
                <span className="text-xs font-mono text-purple-400 font-bold bg-slate-800/60 px-2.5 py-1 rounded-xl border border-slate-800/40">
                  {selectedSegment.duration_sec}s
                </span>
              </div>

              {/* Narration Script Editor */}
              <div>
                <label className="block text-xs font-semibold text-slate-400/70 mb-1.5">
                  AI Teacher Narration Script (Multilingual TTS)
                </label>
                <textarea
                  rows={4}
                  value={selectedSegment.script}
                  onChange={(e) => updateScript(selectedSegment.segment_id, e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 text-xs font-mono focus:outline-none focus:border-purple-600 leading-relaxed"
                />
              </div>

              {/* Visual Slide Spec Preview */}
              <div>
                <label className="block text-xs font-semibold text-slate-400/70 mb-2 flex items-center justify-between">
                  <span>Visual Slide Specification</span>
                  <span className="text-[10px] text-slate-400/50 uppercase font-mono">
                    {selectedSegment.visual_spec?.visual_type}
                  </span>
                </label>

                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800/80 space-y-3 text-xs">
                  <div>
                    <span className="text-[10px] text-slate-400/60 uppercase tracking-wider block font-semibold">Headline</span>
                    <span className="font-bold text-slate-400">{selectedSegment.visual_spec?.headline}</span>
                  </div>

                  {selectedSegment.visual_spec?.bullet_points?.length > 0 && (
                    <div>
                      <span className="text-[10px] text-slate-400/60 uppercase tracking-wider block font-semibold mb-1">Bullet Points</span>
                      <ul className="list-disc list-inside space-y-1 text-slate-400/70 text-[11px]">
                        {selectedSegment.visual_spec.bullet_points.map((pt, i) => (
                          <li key={i}>{pt}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Math LaTeX Equations */}
                  {selectedSegment.visual_spec?.latex_equations && selectedSegment.visual_spec.latex_equations.length > 0 && (
                    <div className="p-3 rounded-xl bg-cyan-950/30 border border-cyan-800/40">
                      <span className="text-[10px] text-purple-400 uppercase font-semibold block mb-1">LaTeX Math Formula</span>
                      <code className="font-mono text-cyan-200 text-xs block overflow-x-auto">
                        {selectedSegment.visual_spec.latex_equations.join(' \\quad ')}
                      </code>
                    </div>
                  )}

                  {/* Code Snippet */}
                  {selectedSegment.visual_spec?.code_content && (
                    <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                      <div className="flex justify-between text-[10px] text-emerald-400 uppercase font-semibold mb-1">
                        <span>Code Snippet</span>
                        <span className="font-mono">{selectedSegment.visual_spec.code_language || 'python'}</span>
                      </div>
                      <pre className="font-mono text-emerald-400 text-[11px] overflow-x-auto whitespace-pre leading-relaxed">
                        {selectedSegment.visual_spec.code_content}
                      </pre>
                    </div>
                  )}
                </div>
              </div>

              {/* Checkpoint Question Details */}
              {selectedSegment.checkpoint_question && (
                <div className="p-4 rounded-xl bg-indigo-950/30 border border-indigo-800/40 space-y-2">
                  <div className="flex items-center gap-1.5 text-xs text-indigo-300 font-semibold">
                    <HelpCircle className="w-3.5 h-3.5 text-purple-400" />
                    <span>In-Video Checkpoint Question</span>
                  </div>
                  <p className="text-xs text-slate-400 font-medium">
                    {selectedSegment.checkpoint_question.prompt}
                  </p>
                  {selectedSegment.checkpoint_question.options && (
                    <div className="grid grid-cols-1 gap-1 pt-1">
                      {selectedSegment.checkpoint_question.options.map((opt, i) => (
                        <div
                          key={i}
                          className={`px-3 py-1.5 rounded-xl text-[11px] font-mono ${
                            i === selectedSegment.checkpoint_question?.correct_option_index
                              ? 'bg-emerald-950/70 border border-emerald-600/40 text-emerald-400'
                              : 'bg-slate-900 text-slate-400/60'
                          }`}
                        >
                          {opt}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="p-12 text-center border border-dashed border-slate-800 rounded-2xl text-slate-400/50 text-xs">
              Select a module from the sequence list to inspect and customize its script and visual specs.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
