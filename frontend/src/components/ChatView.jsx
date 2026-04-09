import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Shield, Sparkles, HelpCircle, Activity, RotateCcw } from 'lucide-react';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';

export default function ChatView({ activeModule, messages, setMessages, refreshKey, onChangeModule }) {
  const [inputMsg, setInputMsg] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const scrollContainerRef = useRef(null);
  const initiatedModuleRef = useRef(null);

  // ── Auto-scroll to bottom whenever messages change ──
  const scrollToBottom = useCallback(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
    }
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isProcessing, scrollToBottom]);

  // ── Handle module switching (Quiz / Assessment) ──
  useEffect(() => {
    let timeoutId;
    if (activeModule === 'QUIZ') {
      initiatedModuleRef.current = 'QUIZ';
      setMessages([]);
      timeoutId = setTimeout(() => {
        sendSystemTrigger('QUIZ');
      }, 50);
    } else if (activeModule === 'ASSESS') {
      initiatedModuleRef.current = 'ASSESS';
      setMessages([]);
      timeoutId = setTimeout(() => {
        sendSystemTrigger('ASSESS');
      }, 50);
    } else if (activeModule === 'CHAT') {
      initiatedModuleRef.current = null;
    }
    
    return () => {
      if (timeoutId) clearTimeout(timeoutId);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeModule, refreshKey]);

  // ── Stream helper ──
  const processStream = async (response) => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let accContent = '';
    let foundBoundary = false;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      accContent += decoder.decode(value, { stream: true });

      if (!foundBoundary && accContent.includes('\n|||\n')) {
        const parts = accContent.split('\n|||\n');
        const bertStr = parts[0];
        let bertObj = null;
        try { bertObj = JSON.parse(bertStr); } catch (e) {}

        foundBoundary = true;
        accContent = parts[1] || '';

        setMessages(prev => {
          const arr = [...prev];
          const lastIdx = arr.length - 1;
          const current = arr[lastIdx];
          const next = { ...current, content: accContent };
          if (bertObj && Object.keys(bertObj).length > 0) {
            next.bert_info = bertObj;
          }
          arr[lastIdx] = next;
          return arr;
        });
      } else if (foundBoundary) {
        setMessages(prev => {
          const arr = [...prev];
          const lastIdx = arr.length - 1;
          arr[lastIdx] = { ...arr[lastIdx], content: accContent };
          return arr;
        });
      }
    }
  };

  // ── Used when module tab is clicked (Quiz / Assess) ──
  const sendSystemTrigger = async (cmd) => {
    if (isProcessing) return;
    setIsProcessing(true);

    // Add an AI placeholder
    setMessages(prev => [...prev, { role: 'assistant', content: '', _cmd: cmd }]);

    try {
      const entropySeed = Math.random().toString(36).substring(7);
      const response = await fetch('http://localhost:8000/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cmd, metadata: entropySeed, history: [] })
      });
      await processStream(response);
    } catch {
      setMessages(prev => {
        const arr = [...prev];
        arr[arr.length - 1].content =
          `**${cmd === 'QUIZ' ? '🎯 Quiz Generator' : '📊 Assessment Module'} — Offline Mode**\n\nI'm running in simulation mode (Ollama is unreachable). Please ensure Ollama is running:\n\`\`\`\nollama serve\n\`\`\``;
        return arr;
      });
    } finally {
      setIsProcessing(false);
    }
  };

  // ── Normal user message ──
  const sendMessage = async (prompt) => {
    if (!prompt.trim() || isProcessing) return;
    setIsProcessing(true);

    const userMsg = { role: 'user', content: prompt };
    setMessages(prev => [...prev, userMsg, { role: 'assistant', content: '', bert_info: null }]);

    try {
      const currentHistory = [...messages, userMsg];
      const endpoint = activeModule === 'CHAT' ? '/api/chat' : '/api/command';
      const body = activeModule === 'CHAT' 
          ? { prompt, history: currentHistory.slice(-10) }
          : { cmd: activeModule, metadata: prompt, history: currentHistory.slice(-10) };

      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      await processStream(response);
    } catch {
      setMessages(prev => {
        const arr = [...prev];
        arr[arr.length - 1].content =
          "**Connection Error:** Unable to reach the CyberGuard API. Please ensure the backend server is running (`uvicorn api:app --reload --port 8000`).";
        return arr;
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputMsg.trim() || isProcessing) return;
    const prompt = inputMsg;
    setInputMsg('');
    if (inputRef.current) inputRef.current.style.height = 'auto';
    await sendMessage(prompt);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend(e);
    }
  };

  const SuggestionCard = ({ icon: Icon, title, description, onClick, color = 'text-textMain' }) => (
    <button
      onClick={onClick}
      className="p-4 bg-[#1a1a1a] border border-[#2a2a2a] rounded-xl text-left hover:bg-[#222222] hover:border-[#383838] transition-all flex flex-col gap-2 group w-full"
    >
      <div className="flex items-center gap-2">
        <Icon className={`w-4 h-4 ${color}`} />
        <h3 className="font-semibold text-[13px] text-textMain">{title}</h3>
      </div>
      <p className="text-[12px] text-textMuted leading-snug">{description}</p>
    </button>
  );

  const moduleLabel = activeModule === 'QUIZ'
    ? '🎯 Quiz Generator'
    : activeModule === 'ASSESS'
    ? '📊 Assessment Module'
    : null;

  return (
    <div className="flex flex-col h-full bg-[#0a0a0a] text-textMain font-inter overflow-hidden">

      {/* Module Banner (for Quiz / Assess) */}
      {moduleLabel && (
        <div className="flex items-center justify-between px-5 py-2.5 border-b border-[#1f1f1f] bg-[#111111]">
          <span className="text-[13px] font-semibold text-textMuted tracking-wide">{moduleLabel}</span>
          <button
            onClick={() => { setMessages([]); initiatedModuleRef.current = null; setTimeout(() => sendSystemTrigger(activeModule), 100); }}
            className="flex items-center gap-1.5 text-[12px] text-textMuted hover:text-textMain transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Restart
          </button>
        </div>
      )}

      {/* ── Scrollable Messages Area ── */}
      <div
        ref={scrollContainerRef}
        className="flex-1 overflow-y-auto px-4 py-6"
        style={{ scrollBehavior: 'smooth' }}
      >
        <div className="max-w-3xl mx-auto space-y-2 min-h-full flex flex-col pb-6">

          {messages.length === 0 && !isProcessing ? (
            /* Welcome / Empty State */
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="flex-1 flex flex-col items-center justify-center text-center py-16"
            >
              <div className="w-16 h-16 bg-[#1a1a1a] rounded-2xl flex items-center justify-center mb-5 shadow-sm border border-[#262626]">
                <Shield className="w-8 h-8 text-textMain" />
              </div>
              <h1 className="text-[26px] font-semibold mb-2 tracking-tight">How can I help you today?</h1>
              <p className="text-[14px] text-textMuted mb-10 max-w-xs leading-relaxed">
                I'm CyberGuard AI — your assistant for cyberbullying awareness, moderation training, and content analysis.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 w-full max-w-2xl">
                <SuggestionCard
                  icon={HelpCircle}
                  title="Generate a Quiz"
                  description="Test your cyberbullying detection knowledge interactively."
                  color="text-yellow-400"
                  onClick={() => onChangeModule && onChangeModule('QUIZ')}
                />
                <SuggestionCard
                  icon={Sparkles}
                  title="Analyze Text"
                  description="Paste any message to get a full severity breakdown."
                  color="text-blue-400"
                  onClick={() => {
                    const text = 'Analyze text: "your text here"';
                    setInputMsg(text);
                    if (inputRef.current) {
                      inputRef.current.focus();
                      setTimeout(() => {
                        if (inputRef.current) {
                          inputRef.current.setSelectionRange(text.indexOf('"') + 1, text.lastIndexOf('"'));
                        }
                      }, 10);
                    }
                  }}
                />
                <SuggestionCard
                  icon={Activity}
                  title="Start Assessment"
                  description="Practice identifying harmful content in a mixed paragraph."
                  color="text-green-400"
                  onClick={() => onChangeModule && onChangeModule('ASSESS')}
                />
              </div>
            </motion.div>
          ) : (
            /* Messages List */
            <AnimatePresence initial={false}>
              {messages.map((msg, i) => {
                let isExplicitRequest = false;
                let isShortUserMsg = false;
                
                if (msg.role === 'assistant' && i > 0 && messages[i-1].role === 'user') {
                   const txt = messages[i-1].content.toLowerCase();
                   if (txt.length < 5) {
                       isShortUserMsg = true;
                   }
                   if (txt.includes('analyze') || txt.includes('evaluate') || txt.includes('is this') || txt.includes('good or bad') || txt.includes('check')) {
                       isExplicitRequest = true;
                   }
                }
                
                // Do not render empty assistant bubbles (e.g. while waiting for first stream token)
                if (msg.role === 'assistant' && !msg.content.trim()) {
                    return null;
                }

                return (
                <MessageBubble
                  key={i}
                  msg={msg}
                  isExplicitRequest={isExplicitRequest || activeModule === 'ASSESS'}
                  isShortUserMsg={isShortUserMsg}
                  isProcessing={isProcessing && i === messages.length - 1}
                  onRewrite={(text) => {
                    setMessages(prev => [...prev, { role: 'assistant', content: '', _cmd: 'REWRITE' }]);
                    setIsProcessing(true);
                    fetch('http://localhost:8000/api/command', {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({ cmd: 'REWRITE', metadata: text, history: messages.slice(-5) })
                    }).then(r => processStream(r)).finally(() => setIsProcessing(false));
                  }}
                />
              )})}
              {isProcessing && (!messages.length || !messages[messages.length - 1]._cmd) && <TypingIndicator />}
            </AnimatePresence>
          )}

      {/* Bottom spacer for floating input */}
          <div className="h-32 flex-shrink-0" />
        </div>
      </div>

      {/* ── Fixed Input Area ── */}
      <div className="absolute bottom-6 left-0 right-0 px-4">
        <div className="max-w-3xl mx-auto">
          <form
            onSubmit={handleSend}
            className="bg-[#111113]/80 backdrop-blur-2xl border border-white/10 rounded-[2rem] p-1.5 pl-5 flex items-end shadow-[0_8px_40px_rgba(0,0,0,0.5)] transition-all focus-within:border-white/25 focus-within:bg-[#1a1a1c]/90 focus-within:shadow-[0_8px_40px_rgba(0,0,0,0.7)]"
          >
            <textarea
              ref={inputRef}
              disabled={isProcessing}
              value={inputMsg}
              onChange={(e) => {
                setInputMsg(e.target.value);
                e.target.style.height = 'auto';
                e.target.style.height = Math.min(e.target.scrollHeight, 200) + 'px';
              }}
              onKeyDown={handleKeyDown}
              placeholder="Message CyberGuard AI..."
              rows={1}
              className="flex-1 bg-transparent border-none outline-none py-3 text-[15px] text-textMain placeholder:text-textMuted disabled:opacity-50 resize-none max-h-[200px] overflow-y-auto"
            />
            <motion.button
              whileTap={{ scale: 0.95 }}
              type="submit"
              disabled={!inputMsg.trim() || isProcessing}
              className={`p-3 rounded-full ml-2 mb-0.5 transition-colors flex items-center justify-center shadow-sm ${
                inputMsg.trim() && !isProcessing
                  ? 'bg-white text-black hover:bg-gray-200'
                  : 'bg-white/5 text-textMuted cursor-not-allowed'
              }`}
            >
              <Send className="w-[18px] h-[18px] translate-x-[1px]" />
            </motion.button>
          </form>
          <div className="text-center mt-2 text-[11px] text-textMuted">
            CyberGuard AI · Press Enter to send, Shift+Enter for new line
          </div>
        </div>
      </div>
    </div>
  );
}
