import React, { useState, useEffect } from 'react';
import {
  Award,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  ArrowRight,
  Sparkles,
  BookOpen,
  TrendingUp,
  Loader2,
  Check,
  ChevronRight,
} from 'lucide-react';
import { Quiz, LearningReport } from '../../types';
import { api } from '../../services/api';

interface QuizViewProps {
  lessonId: string;
  studentId: string;
  onViewAnalytics: () => void;
  onSelectNextTopic: (topic: string) => void;
}

export const QuizView: React.FC<QuizViewProps> = ({
  lessonId,
  studentId,
  onViewAnalytics,
  onSelectNextTopic,
}) => {
  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [report, setReport] = useState<LearningReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadQuiz();
  }, [lessonId]);

  const loadQuiz = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const q = await api.generateQuiz(lessonId, studentId, 3);
      setQuiz(q);
      // Pre-initialize answers
      const initialAnswers: Record<string, any> = {};
      q.questions.forEach((qu) => {
        if (qu.type === 'mcq') initialAnswers[qu.question_id] = 0;
        else initialAnswers[qu.question_id] = '';
      });
      setAnswers(initialAnswers);
    } catch (err: any) {
      setError(err.message || 'Failed to generate quiz.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOptionSelect = (qId: string, optIndex: number) => {
    setAnswers((prev) => ({ ...prev, [qId]: optIndex }));
  };

  const handleTextChange = (qId: string, text: string) => {
    setAnswers((prev) => ({ ...prev, [qId]: text }));
  };

  const handleSubmit = async () => {
    if (!quiz) return;
    setIsSubmitting(true);
    setError(null);

    const formattedAnswers = Object.entries(answers).map(([qId, val]) => ({
      question_id: qId,
      student_answer: val,
    }));

    try {
      const rep = await api.submitQuiz({
        quiz_id: quiz.quiz_id,
        student_id: studentId,
        lesson_id: lessonId,
        answers: formattedAnswers,
      });
      setReport(rep);
    } catch (err: any) {
      setError(err.message || 'Failed to grade quiz.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-3xl mx-auto py-20 text-center space-y-3">
        <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-900" />
        <h3 className="text-base font-bold text-blue-950">Synthesizing Post-Lesson Assessment...</h3>
        <p className="text-xs text-slate-500">Constructing diagnostic questions and rubric checks</p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto py-8 px-4 space-y-6">
      {error && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center justify-between gap-3 shadow-sm">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-red-500 flex-shrink-0" />
            <span>{error}</span>
          </div>
          <button
            type="button"
            onClick={loadQuiz}
            className="px-3 py-1.5 rounded-lg bg-red-100 hover:bg-red-200 text-red-800 text-xs font-semibold flex items-center gap-1.5 transition-colors flex-shrink-0 border border-red-300 cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Retry</span>
          </button>
        </div>
      )}

      {/* State A: Taking Quiz */}
      {!report && quiz && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-white border border-gray-200 shadow-sm space-y-2">
            <div className="flex items-center gap-2 text-xs font-bold text-blue-900 uppercase tracking-wider">
              <Award className="w-4 h-4" />
              <span>Diagnostic Mastery Assessment</span>
            </div>
            <h2 className="text-xl font-black text-blue-950">{quiz.title}</h2>
            <p className="text-xs text-slate-600">
              Answer the following {quiz.questions.length} questions to assess your conceptual understanding and generate your diagnostic learning report.
            </p>
          </div>

          {/* Question List */}
          <div className="space-y-5">
            {quiz.questions.map((q, idx) => (
              <div key={q.question_id} className="p-5 rounded-2xl bg-white border border-gray-200 shadow-sm space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono font-bold text-blue-900 px-2 py-0.5 rounded bg-blue-50 border border-blue-200">
                    Question #{idx + 1} • {q.concept}
                  </span>
                  <span className="text-[10px] text-slate-500 font-mono">{q.points} pt</span>
                </div>

                <p className="text-sm font-bold text-slate-900 leading-snug">{q.prompt}</p>

                {q.type === 'mcq' && q.options ? (
                  <div className="space-y-2 pt-1">
                    {q.options.map((opt, optIdx) => (
                      <button
                        type="button"
                        key={optIdx}
                        onClick={() => handleOptionSelect(q.question_id, optIdx)}
                        className={`w-full p-3.5 rounded-xl border text-xs text-left cursor-pointer transition-all flex items-center justify-between ${
                          answers[q.question_id] === optIdx
                            ? 'border-2 border-blue-900 bg-blue-50 text-blue-950 font-bold shadow-sm'
                            : 'border-gray-200 bg-slate-50 text-slate-800 hover:border-blue-400 hover:bg-blue-50/40'
                        }`}
                      >
                        <span className="leading-snug">{opt}</span>
                        <div
                          className={`w-4 h-4 rounded-full border flex items-center justify-center text-[10px] flex-shrink-0 ml-2 ${
                            answers[q.question_id] === optIdx
                              ? 'border-blue-900 bg-blue-900 text-white'
                              : 'border-gray-300'
                          }`}
                        >
                          {answers[q.question_id] === optIdx && '✓'}
                        </div>
                      </button>
                    ))}
                  </div>
                ) : (
                  <textarea
                    rows={2}
                    value={answers[q.question_id] || ''}
                    onChange={(e) => handleTextChange(q.question_id, e.target.value)}
                    placeholder="Type your conceptual explanation..."
                    className="w-full px-3.5 py-2.5 rounded-xl bg-white border border-gray-300 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-900 focus:ring-1 focus:ring-blue-900 font-sans shadow-xs"
                  />
                )}
              </div>
            ))}
          </div>

          <button
            onClick={handleSubmit}
            disabled={isSubmitting}
            className="w-full py-3.5 rounded-xl bg-yellow-400 hover:bg-yellow-500 active:bg-yellow-600 disabled:opacity-50 text-slate-950 text-sm font-black flex items-center justify-center gap-2 shadow-md shadow-yellow-500/20 transition-all cursor-pointer"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-slate-950" />
                <span>Grading Responses Against Rubrics...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-slate-950" />
                <span>Submit & Generate Diagnostic Report</span>
              </>
            )}
          </button>
        </div>
      )}

      {/* State B: Diagnostic Learning Report */}
      {report && (
        <div className="space-y-6 animate-in fade-in">
          {/* Header Card with Score */}
          <div className="p-6 rounded-2xl bg-white border border-gray-200 shadow-md flex flex-col sm:flex-row items-center justify-between gap-6">
            <div className="space-y-1.5 text-center sm:text-left">
              <span className="text-xs font-bold text-blue-900 uppercase tracking-wider flex items-center justify-center sm:justify-start gap-1.5">
                <Award className="w-4 h-4" />
                <span>Diagnostic Learning Report</span>
              </span>
              <h2 className="text-2xl font-black text-blue-950">Mastery Assessment Summary</h2>
              <p className="text-xs text-slate-600 max-w-md">{report.learning_report_summary}</p>
            </div>

            {/* Score Circle */}
            <div className="flex-shrink-0 flex flex-col items-center justify-center w-24 h-24 rounded-full bg-emerald-50 border-4 border-emerald-500 text-emerald-800 shadow-sm">
              <span className="text-2xl font-black text-emerald-800 font-mono">
                {report.score_percent.toFixed(0)}%
              </span>
              <span className="text-[10px] text-emerald-700 uppercase font-bold">Mastery</span>
            </div>
          </div>

          {/* Concepts Grid: Strengths & Weaknesses */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Strong Concepts */}
            <div className="p-5 rounded-2xl bg-emerald-50/70 border border-emerald-200 space-y-3">
              <div className="flex items-center gap-2 text-xs font-bold text-emerald-900">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Demonstrated Strong Concepts</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {report.strong_concepts.map((c, i) => (
                  <span
                    key={i}
                    className="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-white text-emerald-800 border border-emerald-300 shadow-xs"
                  >
                    ✓ {c}
                  </span>
                ))}
              </div>
            </div>

            {/* Weak Concepts */}
            <div className="p-5 rounded-2xl bg-amber-50/70 border border-amber-200 space-y-3">
              <div className="flex items-center gap-2 text-xs font-bold text-amber-900">
                <AlertTriangle className="w-4 h-4 text-amber-600" />
                <span>Areas for Targeted Revision</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {report.weak_concepts.map((c, i) => (
                  <span
                    key={i}
                    className="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-white text-amber-800 border border-amber-300 shadow-xs"
                  >
                    ! {c}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Resolved Misconceptions */}
          {report.misconceptions_resolved && report.misconceptions_resolved.length > 0 && (
            <div className="p-4 rounded-xl bg-slate-50 border border-gray-200 space-y-2">
              <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wider">
                Misconceptions Resolved During In-Video Scaffolding:
              </span>
              <ul className="text-xs text-slate-800 space-y-1">
                {report.misconceptions_resolved.map((m, i) => (
                  <li key={i} className="flex items-center gap-2 text-emerald-800 font-medium">
                    <Check className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />
                    <span>{m}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommended Next Topics */}
          {report.recommended_next_topics && report.recommended_next_topics.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                <TrendingUp className="w-4 h-4 text-blue-900" />
                <span>Personalized Recommended Next Lessons</span>
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {report.recommended_next_topics.map((t, idx) => (
                  <button
                    type="button"
                    key={idx}
                    onClick={() => onSelectNextTopic(t.topic)}
                    className="p-4 rounded-xl bg-white border border-gray-200 hover:border-blue-400 hover:bg-blue-50/30 cursor-pointer transition-all space-y-1.5 group text-left w-full shadow-sm"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-100 text-blue-900 border border-blue-200 font-bold">
                        {t.level.toUpperCase()}
                      </span>
                      <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-blue-900 transition-colors" />
                    </div>
                    <h4 className="font-bold text-slate-900 text-xs group-hover:text-blue-950 transition-colors">
                      {t.topic}
                    </h4>
                    {t.rationale && (
                      <p className="text-[11px] text-slate-500 leading-tight">{t.rationale}</p>
                    )}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Bottom Actions */}
          <div className="pt-4 flex flex-col sm:flex-row gap-3">
            <button
              onClick={() => {
                setReport(null);
                loadQuiz();
              }}
              className="flex-1 py-3 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold flex items-center justify-center gap-2 transition-colors border border-gray-200 cursor-pointer"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Retake Assessment</span>
            </button>
            <button
              onClick={onViewAnalytics}
              className="flex-1 py-3 rounded-xl bg-blue-900 hover:bg-blue-800 text-white text-xs font-bold flex items-center justify-center gap-2 shadow-md transition-all cursor-pointer"
            >
              <TrendingUp className="w-4 h-4 text-yellow-400" />
              <span>View Full Learning Analytics & Profile</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
