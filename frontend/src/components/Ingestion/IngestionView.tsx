import React, { useState, useRef, useEffect } from 'react';
import { UploadCloud, FileText, Sparkles, CheckCircle2, AlertCircle, Play, Loader2, BookOpen } from 'lucide-react';
import { api } from '../../services/api';
import { DocumentMetadata } from '../../types';

export interface GenerateVideoPayload {
  file?: File;
  documentMetadata?: DocumentMetadata;
  topic?: string;
  subjectCategory?: string;
  title?: string;
  summary?: string;
}

interface IngestionViewProps {
  onGenerateVideo: (data: GenerateVideoPayload) => void;
  isGenerating?: boolean;
  progressStage?: string;
  progressPercent?: number;
  initialTopic?: string;
}

export const IngestionView: React.FC<IngestionViewProps> = ({
  onGenerateVideo,
  isGenerating = false,
  progressStage = '',
  progressPercent = 0,
  initialTopic = '',
}) => {
  const [activeTab, setActiveTab] = useState<'upload' | 'topic'>('upload');
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Document state
  const [uploadedDoc, setUploadedDoc] = useState<DocumentMetadata | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Topic state
  const [topicText, setTopicText] = useState(initialTopic);
  const [subjectCategory, setSubjectCategory] = useState('Mathematics');

  useEffect(() => {
    if (initialTopic) {
      setTopicText(initialTopic);
      setActiveTab('topic');
    }
  }, [initialTopic]);

  const sampleTopics = [
    { title: 'Limits, Continuity & Epsilon-Delta Definition', cat: 'Mathematics' },
    { title: 'Binary Search Trees & Time Complexity', cat: 'Computer Science' },
    { title: 'Cell Biology, Membrane Transport & ATP Pumps', cat: 'Biology' },
    { title: 'The Industrial Revolution & Steam Power in Britain', cat: 'World History' },
  ];

  const handleFileUpload = async (file: File) => {
    setError(null);
    setIsUploading(true);
    try {
      const doc = await api.uploadDocument(file);
      setUploadedDoc(doc);
    } catch (err: any) {
      setError(err.message || 'Failed to upload document.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleTopicSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!topicText.trim() || isGenerating) return;
    setError(null);
    onGenerateVideo({
      topic: topicText.trim(),
      subjectCategory,
      title: topicText.trim(),
    });
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      {/* Intro Heading */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-black text-blue-950 tracking-tight sm:text-4xl mb-2">
          Create Your Video Lesson
        </h1>
        <p className="text-slate-600 text-sm max-w-2xl mx-auto">
          Upload any lecture document or enter an academic topic to automatically generate an interactive ApniHelp video lesson in seconds.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 mb-8 max-w-md mx-auto">
        <button
          onClick={() => setActiveTab('upload')}
          className={`flex-1 pb-3 text-sm font-semibold flex items-center justify-center gap-2 border-b-2 transition-colors ${
            activeTab === 'upload'
              ? 'border-blue-900 text-blue-950 font-bold'
              : 'border-transparent text-slate-500 hover:text-blue-900'
          }`}
        >
          <UploadCloud className="w-4 h-4" />
          <span>Upload Document</span>
        </button>
        <button
          onClick={() => setActiveTab('topic')}
          className={`flex-1 pb-3 text-sm font-semibold flex items-center justify-center gap-2 border-b-2 transition-colors ${
            activeTab === 'topic'
              ? 'border-blue-900 text-blue-950 font-bold'
              : 'border-transparent text-slate-500 hover:text-blue-900'
          }`}
        >
          <Sparkles className="w-4 h-4" />
          <span>Topic Parametric Mode</span>
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-3 shadow-sm">
          <AlertCircle className="w-4 h-4 flex-shrink-0 text-red-500" />
          <span>{error}</span>
        </div>
      )}

      {/* Tab 1: Upload Document */}
      {activeTab === 'upload' && (
        <div className="space-y-6">
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all shadow-sm ${
              isDragging
                ? 'border-blue-900 bg-blue-50/50'
                : 'border-gray-300 hover:border-blue-900 hover:bg-blue-50/20 bg-white'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.pptx,.txt,.md"
              className="hidden"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  handleFileUpload(e.target.files[0]);
                }
              }}
            />

            <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-900">
              {isUploading ? (
                <Loader2 className="w-8 h-8 animate-spin text-blue-900" />
              ) : (
                <UploadCloud className="w-8 h-8 text-blue-900" />
              )}
            </div>

            <h3 className="text-base font-bold text-slate-900 mb-1">
              {isUploading ? 'Extracting & Indexing Material...' : 'Drop your file here, or click to browse'}
            </h3>
            <p className="text-xs text-slate-500 mb-3">
              Supports PDF, DOCX, PowerPoint (.pptx), and Plain Text (.txt, .md)
            </p>
            <span className="inline-block text-[11px] px-3 py-1 rounded-full bg-slate-100 text-slate-600 border border-gray-200">
              Max file size: 50MB
            </span>
          </div>

          {/* Uploaded Document Card with Single 'Generate Video' Button */}
          {uploadedDoc && (
            <div className="p-6 rounded-2xl bg-white border border-gray-200 shadow-md space-y-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-xl bg-blue-50 border border-blue-200 text-blue-900">
                    <FileText className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="font-bold text-slate-900 text-sm">{uploadedDoc.filename}</h4>
                    <p className="text-xs text-slate-500">
                      {uploadedDoc.total_pages} Pages • {uploadedDoc.chunk_count} Grounded Knowledge Chunks
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-emerald-700 bg-emerald-50 border border-emerald-300 px-3 py-1 rounded-full font-semibold">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Ready for Video</span>
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-50 border border-gray-200 text-xs text-slate-700 leading-relaxed">
                <span className="font-bold text-blue-950 block mb-1">Extracted Knowledge Summary:</span>
                {uploadedDoc.extracted_summary}
              </div>

              {/* Single 'Generate Video' Primary Action Button */}
              <button
                onClick={() =>
                  onGenerateVideo({
                    documentMetadata: uploadedDoc,
                    title: uploadedDoc.filename.split('.')[0].replace(/_/g, ' '),
                    summary: uploadedDoc.extracted_summary,
                  })
                }
                disabled={isGenerating}
                className="w-full py-4 px-6 rounded-xl bg-yellow-400 hover:bg-yellow-500 active:bg-yellow-600 disabled:opacity-50 disabled:cursor-not-allowed text-slate-950 font-black text-base flex items-center justify-center gap-2.5 shadow-md shadow-yellow-500/20 transition-all transform hover:-translate-y-0.5 cursor-pointer"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin text-slate-950" />
                    <span>
                      Generating Video ({progressStage || 'Synthesizing Pipeline'}{' '}
                      {progressPercent > 0 ? `${progressPercent}%` : ''})...
                    </span>
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5 fill-slate-950 text-slate-950" />
                    <span>Generate Video</span>
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Topic Parametric Mode */}
      {activeTab === 'topic' && (
        <div className="space-y-6">
          <form onSubmit={handleTopicSubmit} className="p-6 rounded-2xl bg-white border border-gray-200 shadow-md space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-900 mb-2">Subject Category</label>
              <div className="flex flex-wrap gap-2">
                {['Mathematics', 'Computer Science', 'Biology', 'World History', 'Physics'].map((cat) => (
                  <button
                    key={cat}
                    type="button"
                    onClick={() => setSubjectCategory(cat)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                      subjectCategory === cat
                        ? 'bg-blue-900 text-white shadow-sm'
                        : 'bg-slate-100 text-slate-700 border border-gray-200 hover:bg-slate-200 hover:text-blue-950'
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-900 mb-2">Topic or Concept Prompt</label>
              <textarea
                value={topicText}
                onChange={(e) => setTopicText(e.target.value)}
                placeholder="e.g., Explain Limits and Epsilon-Delta definition in Calculus, or Binary Search Tree Worst Case Degeneracy..."
                rows={3}
                className="w-full px-4 py-3 rounded-xl bg-white border border-gray-300 text-slate-900 placeholder-slate-400 text-sm focus:outline-none focus:border-blue-900 focus:ring-1 focus:ring-blue-900 shadow-sm"
              />
            </div>

            {/* Quick Pick Samples */}
            <div>
              <span className="text-[11px] font-semibold text-slate-500 block mb-2">
                Or select a pre-grounded curriculum topic:
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {sampleTopics.map((item, idx) => (
                  <button
                    type="button"
                    key={idx}
                    onClick={() => {
                      setTopicText(item.title);
                      setSubjectCategory(item.cat);
                    }}
                    className="p-3 rounded-xl bg-slate-50 border border-gray-200 hover:border-blue-300 hover:bg-blue-50/40 text-xs text-slate-800 cursor-pointer flex items-center justify-between transition-all group text-left w-full"
                  >
                    <span className="truncate group-hover:text-blue-950 font-medium transition-colors">
                      {item.title}
                    </span>
                    <span className="text-[10px] px-2 py-0.5 rounded-md bg-white text-slate-600 font-mono flex-shrink-0 border border-gray-200 shadow-2xs">
                      {item.cat}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* Single 'Generate Video' Primary Action Button */}
            <button
              type="submit"
              disabled={isGenerating || !topicText.trim()}
              className="w-full py-4 px-6 rounded-xl bg-yellow-400 hover:bg-yellow-500 active:bg-yellow-600 disabled:opacity-50 disabled:cursor-not-allowed text-slate-950 font-black text-base flex items-center justify-center gap-2.5 shadow-md shadow-yellow-500/20 transition-all transform hover:-translate-y-0.5 cursor-pointer"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin text-slate-950" />
                  <span>
                    Generating Video ({progressStage || 'Synthesizing Pipeline'}{' '}
                    {progressPercent > 0 ? `${progressPercent}%` : ''})...
                  </span>
                </>
              ) : (
                <>
                  <Play className="w-5 h-5 fill-slate-950 text-slate-950" />
                  <span>Generate Video</span>
                </>
              )}
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

