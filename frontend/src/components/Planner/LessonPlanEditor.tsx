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
      case 'math_equation': return <Sigma className="w-4 h-4 text-blue-900" />;
      case 'code_snippet': return <Code2 className="w-4 h-4 text-emerald-600" />;
      case 'diagram': return <GitGraph className="w-4 h-4 text-amber-600" />;
      case 'timeline': return <History className="w-4 h-4 text-blue-800" />;
      default: return <Presentation className="w-4 h-4 text-slate-500" />;
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
      <div className="p-6 rounded-2xl bg-white border border-gray-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-xs font-bold uppercase tracking-wider text-blue-900">
              Personalized Lesson Blueprint
            </span>
            <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-yellow-100 text-yellow-800 border border-yellow-300 font-mono font-bold">
              {plan.level.toUpperCase()}
            </span>
            <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-900 border border-blue-200 font-mono font-bold">
              {plan.language.toUpperCase()}
            </span>
          </div>
          <h2 className="text-2xl font-black text-blue-950 tracking-tight">{plan.title}</h2>
          <p className="text-xs text-slate-500 mt-1">
            Total Target Duration: <span className="font-mono text-blue-900 font-bold">{formatDuration(plan.target_duration_sec)}</span> • {plan.modules.length} Pedagogical Modules
          </p>
        </div>

        {/* Top Actions */}
        <div className="flex items-center gap-3">
          <button
            onClick={onOpenProfileModal}
            className="px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 border border-gray-200 text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer"
          >
            <Sliders className="w-3.5 h-3.5 text-blue-900" />
            <span>Customize Level/Time</span>
          </button>

          <button
            onClick={onApproveAndGenerateVideo}
            disabled={isGeneratingVideo}
            className="px-5 py-2.5 rounded-xl bg-yellow-400 hover:bg-yellow-500 active:bg-yellow-600 disabled:opacity-50 text-slate-950 text-xs font-black flex items-center gap-2 shadow-md shadow-yellow-500/20 transition-all cursor-pointer"
          >
            {isGeneratingVideo ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-slate-950" />
                <span>Generating Video ({videoProgressPercent}%)...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-slate-950 text-slate-950" />
                <span>Approve &amp; Generate AI Video</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Video Generation Progress Bar */}
      {isGeneratingVideo && (
        <div className="p-4 rounded-2xl bg-white border border-gray-200 shadow-xs space-y-2">
          <div className="flex justify-between text-xs text-blue-900 font-bold">
            <span className="flex items-center gap-2">
              <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-900" />
              <span>{videoCurrentStage || 'Synthesizing Neural TTS and 2.5D Viseme Avatar...'}</span>
            </span>
            <span className="font-mono font-bold">{videoProgressPercent}%</span>
          </div>
          <div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden border border-gray-200">
            <div
              className="h-full bg-yellow-400 transition-all duration-300"
              style={{ width: `${videoProgressPercent}%` }}
            />
          </div>
        </div>
      )}

      {/* Main Two-Column Layout: Modules List & Module Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Modules Sequence List */}
        <div className="lg:col-span-6 space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-500 font-bold px-1">
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
                      ? 'border-2 border-blue-900 bg-blue-50/50 shadow-sm'
                      : 'border-gray-200 bg-white hover:border-blue-300 hover:bg-blue-50/20 shadow-xs'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3">
                      <div className="p-2 rounded-xl bg-blue-50 border border-blue-200 text-blue-900 mt-0.5">
                        {getVisualIcon(mod.visual_spec?.visual_type)}
                      </div>
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-[10px] font-mono text-blue-900 font-bold">
                            #{mod.order}
                          </span>
                          <h4 className="font-bold text-slate-900 text-xs">{mod.title}</h4>
                        </div>
                        <p className="text-[11px] text-slate-500 line-clamp-1 leading-relaxed">
                          {mod.script}
                        </p>
                        {mod.checkpoint_question && (
                          <div className="mt-2 inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded bg-yellow-100 text-yellow-800 border border-yellow-300 font-bold">
                            <HelpCircle className="w-3 h-3 text-yellow-800" />
                            <span>In-Video Checkpoint Pause</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Right Controls */}
                    <div className="flex flex-col items-end gap-2 flex-shrink-0" onClick={(e) => e.stopPropagation()}>
                      <span className="text-[11px] font-mono text-slate-500 font-medium">
                        {mod.duration_sec}s
                      </span>
                      <div className="flex items-center gap-1">
                        <button
                          disabled={idx === 0}
                          onClick={() => moveModule(idx, 'up')}
                          className="p-1 rounded text-slate-400 hover:text-slate-900 hover:bg-slate-100 disabled:opacity-30 transition-colors cursor-pointer"
                        >
                          <ArrowUp className="w-3 h-3" />
                        </button>
                        <button
                          disabled={idx === plan.modules.length - 1}
                          onClick={() => moveModule(idx, 'down')}
                          className="p-1 rounded text-slate-400 hover:text-slate-900 hover:bg-slate-100 disabled:opacity-30 transition-colors cursor-pointer"
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
            <div className="p-6 rounded-2xl bg-white border border-gray-200 shadow-sm space-y-5 sticky top-20">
              <div className="flex items-center justify-between border-b border-gray-200 pb-3">
                <div className="flex items-center gap-2">
                  <div className="p-2 rounded-xl bg-blue-50 text-blue-900 border border-blue-200">
                    {getVisualIcon(selectedSegment.visual_spec?.visual_type)}
                  </div>
                  <div>
                    <h3 className="font-bold text-blue-950 text-sm">{selectedSegment.title}</h3>
                    <p className="text-[11px] text-slate-500">
                      Module Type: <span className="text-blue-900 font-mono font-bold">{selectedSegment.segment_type}</span>
                    </p>
                  </div>
                </div>
                <span className="text-xs font-mono text-blue-950 font-bold bg-slate-100 px-2.5 py-1 rounded-xl border border-gray-200">
                  {selectedSegment.duration_sec}s
                </span>
              </div>

              {/* Narration Script Editor */}
              <div>
                <label className="block text-xs font-bold text-slate-900 mb-1.5">
                  ApniHelp Narration Script (Multilingual TTS)
                </label>
                <textarea
                  rows={4}
                  value={selectedSegment.script}
                  onChange={(e) => updateScript(selectedSegment.segment_id, e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-white border border-gray-300 text-slate-900 text-xs font-mono focus:outline-none focus:border-blue-900 focus:ring-1 focus:ring-blue-900 leading-relaxed shadow-xs"
                />
              </div>

              {/* Visual Slide Spec Preview */}
              <div>
                <label className="block text-xs font-bold text-slate-900 mb-2 flex items-center justify-between">
                  <span>Visual Slide Specification</span>
                  <span className="text-[10px] text-slate-500 uppercase font-mono font-bold">
                    {selectedSegment.visual_spec?.visual_type}
                  </span>
                </label>

                <div className="p-4 rounded-xl bg-slate-50 border border-gray-200 space-y-3 text-xs">
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-bold">Headline</span>
                    <span className="font-bold text-slate-900">{selectedSegment.visual_spec?.headline}</span>
                  </div>

                  {selectedSegment.visual_spec?.bullet_points && selectedSegment.visual_spec.bullet_points.length > 0 && (
                    <div>
                      <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-bold mb-1">Bullet Points</span>
                      <ul className="list-disc list-inside space-y-1 text-slate-700 text-[11px]">
                        {selectedSegment.visual_spec.bullet_points.map((pt, i) => (
                          <li key={i}>{pt}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Math LaTeX Equations */}
                  {selectedSegment.visual_spec?.latex_equations && selectedSegment.visual_spec.latex_equations.length > 0 && (
                    <div className="p-3 rounded-xl bg-blue-50/70 border border-blue-200">
                      <span className="text-[10px] text-blue-900 uppercase font-bold block mb-1">LaTeX Math Formula</span>
                      <code className="font-mono text-blue-950 text-xs block overflow-x-auto">
                        {selectedSegment.visual_spec.latex_equations.join(' \\quad ')}
                      </code>
                    </div>
                  )}

                  {/* Code Snippet */}
                  {selectedSegment.visual_spec?.code_content && (
                    <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-slate-100">
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
                <div className="p-4 rounded-xl bg-blue-50/70 border border-blue-200 space-y-2">
                  <div className="flex items-center gap-1.5 text-xs text-blue-900 font-bold">
                    <HelpCircle className="w-3.5 h-3.5 text-blue-900" />
                    <span>In-Video Checkpoint Question</span>
                  </div>
                  <p className="text-xs text-slate-900 font-medium">
                    {selectedSegment.checkpoint_question.prompt}
                  </p>
                  {selectedSegment.checkpoint_question.options && (
                    <div className="grid grid-cols-1 gap-1 pt-1">
                      {selectedSegment.checkpoint_question.options.map((opt, i) => (
                        <div
                          key={i}
                          className={`px-3 py-1.5 rounded-xl text-[11px] font-mono ${
                            i === selectedSegment.checkpoint_question?.correct_option_index
                              ? 'bg-emerald-50 border border-emerald-300 text-emerald-900 font-bold'
                              : 'bg-white text-slate-800 border border-gray-200'
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
            <div className="p-12 text-center border-2 border-dashed border-gray-200 bg-white rounded-2xl text-slate-500 text-xs shadow-xs">
              Select a module from the sequence list to inspect and customize its script and visual specs.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
