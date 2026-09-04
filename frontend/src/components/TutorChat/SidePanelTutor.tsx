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
      text: 'Hello! I am your ApniHelp tutor. Ask me any unscripted questions, request deeper derivations, or ask me to switch to Hindi anytime.',
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
    <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-white border-l border-gray-200 shadow-2xl flex flex-col animate-in slide-in-from-right">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-slate-50 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-blue-50 border border-blue-200 text-blue-900">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-bold text-blue-950 text-xs">ApniHelp Side-Panel Tutor</h3>
            <p className="text-[10px] text-slate-500">RAG-Grounded Contextual Assistance</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onLanguageSwitch(currentLanguage === 'en' ? 'hi' : 'en')}
            className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white hover:bg-slate-100 border border-gray-200 text-[10px] font-bold text-slate-700 transition-colors shadow-xs cursor-pointer"
          >
            <Globe className="w-3 h-3 text-blue-900" />
            <span>{currentLanguage === 'en' ? 'EN' : 'हिन्दी'}</span>
          </button>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition-colors cursor-pointer"
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
              <div className="w-7 h-7 rounded-lg bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-900 flex-shrink-0 mt-0.5">
                <Bot className="w-3.5 h-3.5" />
              </div>
            )}
            <div
              className={`max-w-[85%] p-3.5 rounded-2xl leading-relaxed ${
                m.sender === 'user'
                  ? 'bg-blue-900 text-white rounded-br-none shadow-sm font-medium'
                  : 'bg-slate-100 border border-gray-200 text-slate-900 rounded-bl-none shadow-xs'
              }`}
            >
              <p className="whitespace-pre-line">{m.text}</p>

              {/* Grounded Citations */}
              {m.sources && m.sources.length > 0 && (
                <div className="mt-2.5 pt-2 border-t border-gray-200 text-[10px] text-blue-900 flex items-center gap-1.5 font-semibold">
                  <BookOpen className="w-3 h-3 text-blue-900" />
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
                      className="px-2.5 py-1 rounded-full bg-white border border-gray-200 hover:border-blue-400 hover:bg-blue-50/40 text-[10px] text-slate-700 hover:text-blue-950 transition-all shadow-xs cursor-pointer"
                    >
                      {act}
                    </button>
                  ))}
                </div>
              )}
            </div>
            {m.sender === 'user' && (
              <div className="w-7 h-7 rounded-lg bg-blue-900 flex items-center justify-center text-yellow-400 flex-shrink-0 mt-0.5 text-[10px] font-black">
                U
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex items-center gap-2 text-slate-500 text-xs py-2">
            <Loader2 className="w-4 h-4 animate-spin text-blue-900" />
            <span>ApniHelp Tutor is thinking &amp; grounding answer...</span>
          </div>
        )}
      </div>

      {/* Input Field */}
      <div className="p-3 border-t border-gray-200 bg-slate-50">
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
            className="flex-1 px-3.5 py-2.5 rounded-xl bg-white border border-gray-300 text-slate-900 placeholder-slate-400 text-xs focus:outline-none focus:border-blue-900 focus:ring-1 focus:ring-blue-900 shadow-xs"
          />
          <button
            type="submit"
            disabled={isLoading || !inputText.trim()}
            className="p-2.5 rounded-xl bg-yellow-400 hover:bg-yellow-500 active:bg-yellow-600 disabled:opacity-40 text-slate-950 font-bold transition-all shadow-sm cursor-pointer"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>
    </div>
  );
};
