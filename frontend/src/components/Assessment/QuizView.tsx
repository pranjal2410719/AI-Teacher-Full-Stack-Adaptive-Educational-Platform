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
        <Loader2 className="w-8 h-8 animate-spin mx-auto text-purple-400" />
        <h3 className="text-base font-bold text-slate-100">Synthesizing Post-Lesson Assessment...</h3>
        <p className="text-xs text-slate-400">Constructing diagnostic questions and rubric checks</p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto py-8 px-4 space-y-6">
      {error && (
        <div className="p-4 rounded-xl bg-red-950/40 border border-red-800 text-red-300 text-xs">
          {error}
        </div>
      )}

      {/* State A: Taking Quiz */}
      {!report && quiz && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl space-y-2">
            <div className="flex items-center gap-2 text-xs font-bold text-purple-400 uppercase tracking-wider">
              <Award className="w-4 h-4" />
              <span>Diagnostic Mastery Assessment</span>
            </div>
            <h2 className="text-xl font-bold text-slate-100">{quiz.title}</h2>
            <p className="text-xs text-slate-400">
              Answer the following {quiz.questions.length} questions to assess your conceptual understanding and generate your diagnostic learning report.
            </p>
          </div>

          {/* Question List */}
          <div className="space-y-5">
            {quiz.questions.map((q, idx) => (
              <div key={q.question_id} className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono font-bold text-purple-400 px-2 py-0.5 rounded bg-purple-950/80 border border-purple-800/40">
                    Question #{idx + 1} • {q.concept}
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono">{q.points} pt</span>
                </div>

                <p className="text-sm font-semibold text-slate-100 leading-snug">{q.prompt}</p>

                {q.type === 'mcq' && q.options ? (
                  <div className="space-y-2 pt-1">
                    {q.options.map((opt, optIdx) => (
                      <div
                        key={optIdx}
                        onClick={() => handleOptionSelect(q.question_id, optIdx)}
                        className={`p-3 rounded-xl border text-xs cursor-pointer transition-all flex items-center justify-between ${
                          answers[q.question_id] === optIdx
                            ? 'border-purple-500 bg-purple-950/40 text-purple-200'
                            : 'border-slate-800 bg-slate-950/60 text-slate-300 hover:border-slate-700'
                        }`}
                      >
                        <span>{opt}</span>
                        <div
                          className={`w-4 h-4 rounded-full border flex items-center justify-center text-[10px] ${
                            answers[q.question_id] === optIdx
                              ? 'border-purple-500 bg-purple-600 text-white'
                              : 'border-slate-700'
                          }`}
                        >
                          {answers[q.question_id] === optIdx && '✓'}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <textarea
                    rows={2}
                    value={answers[q.question_id] || ''}
                    onChange={(e) => handleTextChange(q.question_id, e.target.value)}
                    placeholder="Type your conceptual explanation..."
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-purple-500 font-sans"
                  />
                )}
              </div>
            ))}
          </div>

          <button
            onClick={handleSubmit}
            disabled={isSubmitting}
            className="w-full py-3.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 disabled:opacity-50 text-white text-sm font-bold flex items-center justify-center gap-2 shadow-lg shadow-purple-600/30 transition-all"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Grading Responses Against Rubrics...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
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
          <div className="p-6 rounded-2xl bg-slate-900 border border-purple-900/50 shadow-2xl flex flex-col sm:flex-row items-center justify-between gap-6">
            <div className="space-y-1.5 text-center sm:text-left">
              <span className="text-xs font-bold text-purple-400 uppercase tracking-wider flex items-center justify-center sm:justify-start gap-1.5">
                <Award className="w-4 h-4" />
                <span>Diagnostic Learning Report</span>
              </span>
              <h2 className="text-2xl font-extrabold text-slate-100">Mastery Assessment Summary</h2>
              <p className="text-xs text-slate-400 max-w-md">{report.learning_report_summary}</p>
            </div>

            {/* Score Circle */}
            <div className="flex-shrink-0 flex flex-col items-center justify-center w-24 h-24 rounded-full bg-gradient-to-tr from-purple-950 via-slate-900 to-emerald-950 border-2 border-emerald-500/80 shadow-lg shadow-emerald-500/10">
              <span className="text-2xl font-black text-emerald-300 font-mono">
                {report.score_percent.toFixed(0)}%
              </span>
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Mastery</span>
            </div>
          </div>

          {/* Concepts Grid: Strengths & Weaknesses */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Strong Concepts */}
            <div className="p-5 rounded-2xl bg-slate-900/80 border border-emerald-900/40 space-y-3">
              <div className="flex items-center gap-2 text-xs font-bold text-emerald-400">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>Demonstrated Strong Concepts</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {report.strong_concepts.map((c, i) => (
                  <span
                    key={i}
                    className="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-emerald-950/70 text-emerald-300 border border-emerald-800/60"
                  >
                    ✓ {c}
                  </span>
                ))}
              </div>
            </div>

            {/* Weak Concepts */}
            <div className="p-5 rounded-2xl bg-slate-900/80 border border-amber-900/40 space-y-3">
              <div className="flex items-center gap-2 text-xs font-bold text-amber-400">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <span>Areas for Targeted Revision</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {report.weak_concepts.map((c, i) => (
                  <span
                    key={i}
                    className="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-amber-950/70 text-amber-300 border border-amber-800/60"
                  >
                    ! {c}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Resolved Misconceptions */}
          {report.misconceptions_resolved && report.misconceptions_resolved.length > 0 && (
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                Misconceptions Resolved During In-Video Scaffolding:
              </span>
              <ul className="text-xs text-slate-300 space-y-1">
                {report.misconceptions_resolved.map((m, i) => (
                  <li key={i} className="flex items-center gap-2 text-emerald-300">
                    <Check className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                    <span>{m}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommended Next Topics */}
          {report.recommended_next_topics && report.recommended_next_topics.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <TrendingUp className="w-4 h-4 text-purple-400" />
                <span>Personalized Recommended Next Lessons</span>
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {report.recommended_next_topics.map((t, idx) => (
                  <div
                    key={idx}
                    onClick={() => onSelectNextTopic(t.topic)}
                    className="p-4 rounded-xl bg-slate-900 border border-slate-800 hover:border-purple-600/70 cursor-pointer transition-all space-y-1.5 group"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800/40">
                        {t.level.toUpperCase()}
                      </span>
                      <ChevronRight className="w-4 h-4 text-slate-500 group-hover:text-purple-400 transition-colors" />
                    </div>
                    <h4 className="font-bold text-slate-100 text-xs group-hover:text-purple-300 transition-colors">
                      {t.topic}
                    </h4>
                    {t.rationale && (
                      <p className="text-[11px] text-slate-400 leading-tight">{t.rationale}</p>
                    )}
                  </div>
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
              className="flex-1 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center justify-center gap-2 transition-colors"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Retake Assessment</span>
            </button>
            <button
              onClick={onViewAnalytics}
              className="flex-1 py-3 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold flex items-center justify-center gap-2 shadow-lg shadow-purple-600/25 transition-all"
            >
              <TrendingUp className="w-4 h-4" />
              <span>View Full Learning Analytics & Profile</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
