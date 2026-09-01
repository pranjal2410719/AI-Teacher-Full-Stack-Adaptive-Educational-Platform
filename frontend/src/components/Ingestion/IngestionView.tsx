import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, Sparkles, CheckCircle2, AlertCircle, ArrowRight, Loader2, BookOpen } from 'lucide-react';
import { api } from '../../services/api';
import { DocumentMetadata, TopicIngestionResponse } from '../../types';

interface IngestionViewProps {
  onMaterialReady: (data: { documentId?: string; topicId?: string; title: string; summary: string }) => void;
}

export const IngestionView: React.FC<IngestionViewProps> = ({ onMaterialReady }) => {
  const [activeTab, setActiveTab] = useState<'upload' | 'topic'>('upload');
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Document state
  const [uploadedDoc, setUploadedDoc] = useState<DocumentMetadata | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Topic state
  const [topicText, setTopicText] = useState('');
  const [subjectCategory, setSubjectCategory] = useState('Mathematics');
  const [isGeneratingTopic, setIsGeneratingTopic] = useState(false);
  const [topicResult, setTopicResult] = useState<TopicIngestionResponse | null>(null);

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

  const handleTopicSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topicText.trim()) return;
    setError(null);
    setIsGeneratingTopic(true);
    try {
      const res = await api.ingestTopic(topicText.trim(), subjectCategory);
      setTopicResult(res);
    } catch (err: any) {
      setError(err.message || 'Failed to process topic.');
    } finally {
      setIsGeneratingTopic(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      {/* Intro Heading */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-extrabold text-white tracking-tight sm:text-4xl mb-3">
          What would you like to teach or learn today?
        </h1>
        <p className="text-slate-400/60 text-sm max-w-2xl mx-auto">
          Upload any lecture slides, textbook PDF, or Word document — or type any academic topic for instant RAG grounding and lesson synthesis.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-800 mb-8 max-w-md mx-auto">
        <button
          onClick={() => setActiveTab('upload')}
          className={`flex-1 pb-3 text-sm font-semibold flex items-center justify-center gap-2 border-b-2 transition-colors ${
            activeTab === 'upload'
              ? 'border-purple-600 text-[#ff6f1e]'
              : 'border-transparent text-slate-400/60 hover:text-slate-400'
          }`}
        >
          <UploadCloud className="w-4 h-4" />
          <span>Upload Document</span>
        </button>
        <button
          onClick={() => setActiveTab('topic')}
          className={`flex-1 pb-3 text-sm font-semibold flex items-center justify-center gap-2 border-b-2 transition-colors ${
            activeTab === 'topic'
              ? 'border-purple-600 text-[#ff6f1e]'
              : 'border-transparent text-slate-400/60 hover:text-slate-400'
          }`}
        >
          <Sparkles className="w-4 h-4" />
          <span>Topic Parametric Mode</span>
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-xl bg-red-950/40 border border-red-800/60 text-red-300 text-xs flex items-center gap-3">
          <AlertCircle className="w-4 h-4 flex-shrink-0 text-red-400" />
          <span>{error}</span>
        </div>
      )}

      {/* Tab 1: Upload Document */}
      {activeTab === 'upload' && (
        <div className="space-y-6">
          <div
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all ${
              isDragging
                ? 'border-purple-600 bg-slate-900/20'
                : 'border-slate-800 hover:border-slate-800 bg-slate-900/40'
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

            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-slate-900/60 border border-slate-800/60 flex items-center justify-center text-[#ff6f1e]">
              {isUploading ? (
                <Loader2 className="w-8 h-8 animate-spin" />
              ) : (
                <UploadCloud className="w-8 h-8" />
              )}
            </div>

            <h3 className="text-base font-bold text-slate-400 mb-1">
              {isUploading ? 'Extracting & Indexing Material...' : 'Drop your files here, or click to browse'}
            </h3>
            <p className="text-xs text-slate-400/60 mb-3">
              Supports PDF, DOCX, PowerPoint (.pptx), and Plain Text (.txt, .md)
            </p>
            <span className="inline-block text-[11px] px-3 py-1 rounded-full bg-slate-900 text-slate-400/70 border border-slate-800">
              Max file size: 50MB
            </span>
          </div>

          {/* Uploaded Document Card */}
          {uploadedDoc && (
            <div className="p-6 rounded-2xl bg-slate-900 border-[1.5px] border-slate-800/90 border border-slate-800/60 shadow-[rgba(0,0,0,0.06)_0px_2px_20px_0px] space-y-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800/60 text-[#ff6f1e]">
                    <FileText className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="font-bold text-slate-400 text-sm">{uploadedDoc.filename}</h4>
                    <p className="text-xs text-slate-400/60">
                      {uploadedDoc.total_pages} Pages • {uploadedDoc.chunk_count} Grounded Semantic Chunks Indexed
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-[#22c55e] bg-slate-900 border border-[#22c55e]/40 px-3 py-1 rounded-full">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Ready</span>
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/80 text-xs text-slate-400/70 leading-relaxed">
                <span className="font-semibold text-[#ff6f1e] block mb-1">Extracted Syllabus Summary:</span>
                {uploadedDoc.extracted_summary}
              </div>

              <button
                onClick={() => onMaterialReady({
                  documentId: uploadedDoc.document_id,
                  title: uploadedDoc.filename.split('.')[0].replace(/_/g, ' '),
                  summary: uploadedDoc.extracted_summary
                })}
                className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-sm font-semibold flex items-center justify-center gap-2 shadow-lg shadow-xl transition-all"
              >
                <span>Proceed to Configure Learner Profile & Plan</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Topic Parametric Mode */}
      {activeTab === 'topic' && (
        <div className="space-y-6">
          <form onSubmit={handleTopicSubmit} className="p-6 rounded-2xl bg-slate-900 border-[1.5px] border-slate-800/60 border border-slate-800 space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400/70 mb-2">Subject Category</label>
              <div className="flex flex-wrap gap-2">
                {['Mathematics', 'Computer Science', 'Biology', 'World History', 'Physics'].map((cat) => (
                  <button
                    key={cat}
                    type="button"
                    onClick={() => setSubjectCategory(cat)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
                      subjectCategory === cat
                        ? 'bg-[#ff6f1e] text-white shadow-sm'
                        : 'bg-slate-900 text-slate-400/60 hover:bg-slate-900 hover:text-slate-400'
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400/70 mb-2">Topic or Concept Prompt</label>
              <textarea
                value={topicText}
                onChange={(e) => setTopicText(e.target.value)}
                placeholder="e.g., Explain Limits and Epsilon-Delta definition in Calculus, or Binary Search Tree Worst Case Degeneracy..."
                rows={3}
                className="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 placeholder-slate-500 text-sm focus:outline-none focus:border-purple-600 focus:ring-1 focus:ring-purple-500"
              />
            </div>

            {/* Quick Pick Samples */}
            <div>
              <span className="text-[11px] font-medium text-slate-400/60 block mb-2">Or select a pre-grounded curriculum topic:</span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {sampleTopics.map((item, idx) => (
                  <div
                    key={idx}
                    onClick={() => {
                      setTopicText(item.title);
                      setSubjectCategory(item.cat);
                    }}
                    className="p-2.5 rounded-xl bg-slate-900/70 border border-slate-800/80 hover:border-[#ce500a]/60 text-xs text-slate-400/70 cursor-pointer flex items-center justify-between transition-colors"
                  >
                    <span className="truncate">{item.title}</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-900 text-slate-400/60 font-mono flex-shrink-0">
                      {item.cat}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <button
              type="submit"
              disabled={isGeneratingTopic || !topicText.trim()}
              className="w-full py-3 px-4 rounded-xl bg-[#ff6f1e] hover:bg-[#ff6f1e] disabled:opacity-50 text-white text-sm font-semibold flex items-center justify-center gap-2 transition-all shadow-md shadow-xl"
            >
              {isGeneratingTopic ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Synthesizing Parametric Grounding...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Generate Grounded Syllabus</span>
                </>
              )}
            </button>
          </form>

          {/* Topic Result Card */}
          {topicResult && (
            <div className="p-6 rounded-2xl bg-slate-900 border-[1.5px] border-slate-800/90 border border-slate-800/60 shadow-[rgba(0,0,0,0.06)_0px_2px_20px_0px] space-y-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800/60 text-[#ff6f1e]">
                    <BookOpen className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="font-bold text-slate-400 text-sm">{topicResult.topic}</h4>
                    <p className="text-xs text-slate-400/60">
                      Category: {topicResult.subject_category} • {topicResult.generated_chunks_count} Seed Knowledge Chunks
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-[#22c55e] bg-slate-900 border border-[#22c55e]/40 px-3 py-1 rounded-full">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Synthesized</span>
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/80 text-xs text-slate-400/70 leading-relaxed">
                <span className="font-semibold text-[#ff6f1e] block mb-1">Generated Syllabus Scope:</span>
                {topicResult.seed_summary}
              </div>

              <button
                onClick={() => onMaterialReady({
                  topicId: topicResult.topic_id,
                  title: topicResult.topic,
                  summary: topicResult.seed_summary
                })}
                className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-sm font-semibold flex items-center justify-center gap-2 shadow-lg shadow-xl transition-all"
              >
                <span>Proceed to Configure Learner Profile & Plan</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
