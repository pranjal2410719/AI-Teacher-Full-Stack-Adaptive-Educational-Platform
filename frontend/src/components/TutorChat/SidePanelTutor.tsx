import React, { useState } from 'react';
import { X, Send, Bot, User, Sparkles, Globe, BookOpen, Loader2 } from 'lucide-react';
import { api } from '../../services/api';
import { TutorChatResponse } from '../../types';

interface SidePanelTutorProps {
  isOpen: boolean;
  onClose: () => void;
  currentLanguage: string;
  onLanguageSwitch: (lang: string) => void;
  documentId?: string;
  topicId?: string;
}

interface ChatMessage {
  id: string;
  sender: 'user' | 'tutor';
  text: string;
  sources?: string[];
  suggestedActions?: string[];
}

export const SidePanelTutor: React.FC<SidePanelTutorProps> = ({
  isOpen,
  onClose,
  currentLanguage,
  onLanguageSwitch,
  documentId,
  topicId,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      sender: 'tutor',
      text: 'Hello! I am your AI Teacher tutor. Ask me any unscripted questions, request deeper derivations, or ask me to switch to Hindi anytime.',
      suggestedActions: ['Explain in Hindi (हिंदी में समझाएं)', 'What is the physical intuition?', 'Give a code example'],
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  if (!isOpen) return null;

  const handleSend = async (messageText?: string) => {
    const textToSend = (messageText || inputText).trim();
    if (!textToSend || isLoading) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      text: textToSend,
    };
    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setIsLoading(true);

    try {
      const res = await api.tutorChat({
        message: textToSend,
        document_id: documentId,
        topic_id: topicId,
      });

      if (res.language && res.language !== currentLanguage) {
        onLanguageSwitch(res.language);
      }

      const tutorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'tutor',
        text: res.reply,
        sources: res.grounded_sources,
        suggestedActions: res.suggested_actions,
      };
      setMessages((prev) => [...prev, tutorMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'tutor',
          text: 'I apologize, but I encountered a momentary connection error. Please try asking again.',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-slate-900 border-l border-slate-800 shadow-2xl flex flex-col animate-in slide-in-from-right">
      {/* Header */}
      <div className="p-4 border-b border-slate-800 bg-slate-900 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-slate-800 border border-slate-800 text-[#ff6f1e]">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-bold text-slate-400 text-xs">AI Teacher Side-Panel Tutor</h3>
            <p className="text-[10px] text-slate-400/60">RAG-Grounded Contextual Assistance</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onLanguageSwitch(currentLanguage === 'en' ? 'hi' : 'en')}
            className="flex items-center gap-1 px-2 py-1 rounded bg-slate-800 text-[10px] font-semibold text-slate-400/70 hover:bg-slate-800"
          >
            <Globe className="w-3 h-3 text-[#22c55e]" />
            <span>{currentLanguage === 'en' ? 'EN' : 'हिन्दी'}</span>
          </button>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400/60 hover:text-slate-400 hover:bg-slate-800"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Message History */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4 text-xs">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex gap-2.5 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {m.sender === 'tutor' && (
              <div className="w-7 h-7 rounded-lg bg-slate-800 border border-purple-800/50 flex items-center justify-center text-[#ff6f1e] flex-shrink-0 mt-0.5">
                <Bot className="w-3.5 h-3.5" />
              </div>
            )}
            <div
              className={`max-w-[85%] p-3.5 rounded-2xl leading-relaxed ${
                m.sender === 'user'
                  ? 'bg-[#ff6f1e] text-white rounded-br-none shadow-md shadow-slate-900/50'
                  : 'bg-slate-900 border border-slate-800/80 text-slate-400 rounded-bl-none shadow-sm'
              }`}
            >
              <p className="whitespace-pre-line">{m.text}</p>

              {/* Grounded Citations */}
              {m.sources && m.sources.length > 0 && (
                <div className="mt-2.5 pt-2 border-t border-slate-800/80 text-[10px] text-[#ff6f1e] flex items-center gap-1.5">
                  <BookOpen className="w-3 h-3 text-[#ff6f1e]" />
                  <span>Grounded in: {m.sources.join(', ')}</span>
                </div>
              )}

              {/* Action chips */}
              {m.suggestedActions && m.suggestedActions.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {m.suggestedActions.map((act, i) => (
                    <button
                      key={i}
                      onClick={() => handleSend(act)}
                      className="px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800/80 hover:border-purple-500 text-[10px] text-slate-400/70 transition-colors"
                    >
                      {act}
                    </button>
                  ))}
                </div>
              )}
            </div>
            {m.sender === 'user' && (
              <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center text-white flex-shrink-0 mt-0.5 text-[10px] font-bold">
                U
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex items-center gap-2 text-slate-400/60 text-xs py-2">
            <Loader2 className="w-4 h-4 animate-spin text-[#ff6f1e]" />
            <span>AI Tutor is thinking & grounding answer...</span>
          </div>
        )}
      </div>

      {/* Input Field */}
      <div className="p-3 border-t border-slate-800 bg-slate-900">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder={currentLanguage === 'hi' ? 'कोई भी प्रश्न पूछें...' : 'Ask unscripted question...'}
            className="flex-1 px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 placeholder-slate-500 text-xs focus:outline-none focus:border-purple-500"
          />
          <button
            type="submit"
            disabled={isLoading || !inputText.trim()}
            className="p-2.5 rounded-xl bg-[#ff6f1e] hover:bg-[#ff6f1e] disabled:opacity-40 text-white transition-all shadow-md shadow-slate-900/50"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>
    </div>
  );
};
