import React from 'react';
import { X, Loader2 } from 'lucide-react';

interface LoadingPopupProps {
  isOpen: boolean;
  message?: string;
  progressPercent?: number;
  stage?: string;
  startedAtMs?: number;
  maxDurationMs?: number;
  onCancel?: () => void;
  onDismiss?: () => void;
  cancelLabel?: string;
}

const formatElapsed = (ms: number): string => {
  const total = Math.max(0, Math.floor(ms / 1000));
  const m = Math.floor(total / 60);
  const s = total % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
};

const STAGE_LABELS: Record<string, string> = {
  tts_audio_synthesis: 'Synthesizing neural narration (TTS)...',
  avatar_lip_sync: 'Animating AI teacher avatar...',
  rendering_visual_slides: 'Rendering subject-aware visual slides...',
  stitching_ffmpeg: 'Stitching & encoding final MP4...',
  ready: 'Almost done...',
  pending: 'Preparing pipeline...',
  failed: 'Pipeline failed.',
};

const humanizeStage = (stage: string | undefined): string => {
  if (!stage) return 'Generating video...';
  return STAGE_LABELS[stage] || stage.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
};

const LoadingPopup: React.FC<LoadingPopupProps> = ({
  isOpen,
  message,
  progressPercent = 0,
  stage,
  startedAtMs,
  maxDurationMs = 300000,
  onCancel,
  onDismiss,
  cancelLabel = 'Cancel',
}) => {
  const [now, setNow] = React.useState<number>(() => Date.now());

  React.useEffect(() => {
    if (!isOpen) return;
    const id = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(id);
  }, [isOpen]);

  if (!isOpen) return null;

  const elapsedMs = startedAtMs ? now - startedAtMs : 0;
  const elapsed = formatElapsed(elapsedMs);
  const maxSec = Math.floor(maxDurationMs / 1000);
  const remaining = formatElapsed(Math.max(0, maxDurationMs - elapsedMs));
  const pct = Math.max(0, Math.min(100, progressPercent));
  const stageText = humanizeStage(stage);
  const isIndeterminate = pct === 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="relative flex flex-col items-center p-6 bg-white rounded-lg shadow-xl w-[30rem] max-w-[92vw]">
        {onDismiss && (
          <button
            type="button"
            onClick={onDismiss}
            aria-label="Close"
            className="absolute top-2 right-2 p-1 rounded-full text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}

        <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
        <p className="mt-3 text-gray-800 font-semibold text-center">
          {message || 'Generating your video lesson...'}
        </p>
        <p className="mt-1 text-xs text-slate-500 text-center max-w-md">
          Please keep this tab open. Larger lessons with more visual segments can take up to ~{Math.floor(maxSec / 60)} minutes.
        </p>

        <div className="mt-4 w-full">
          <div className="flex justify-between text-xs font-semibold text-slate-500 mb-1">
            <span>
              {isIndeterminate ? 'Working…' : `${pct.toFixed(0)}% complete`}
            </span>
            <span>
              {elapsed} elapsed
              {remaining !== '0:00' && ` · ${remaining} left`}
            </span>
          </div>
          <div className="w-full bg-slate-200 rounded-full h-2.5 overflow-hidden">
            <div
              className="bg-gradient-to-r from-blue-500 to-indigo-500 h-2.5 rounded-full transition-all duration-300"
              style={{ width: `${isIndeterminate ? 8 : pct}%` }}
            />
          </div>
          <p className="mt-3 text-xs text-slate-600 text-center font-medium">
            {stageText}
          </p>
        </div>

        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="mt-5 px-4 py-2 text-sm font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-md transition-colors"
          >
            {cancelLabel}
          </button>
        )}
      </div>
    </div>
  );
};

export default LoadingPopup;