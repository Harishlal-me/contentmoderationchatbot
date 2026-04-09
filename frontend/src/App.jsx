import React, { useState, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Shield, MessageSquare, Trash2, PlusCircle, Search } from 'lucide-react';
import ChatView from './components/ChatView';

export default function App() {
  const [activeModule, setActiveModule] = useState('CHAT');
  const [messages, setMessages] = useState([]);
  const [refreshKey, setRefreshKey] = useState(0);

  // Chat History Management
  const [currentChatId, setCurrentChatId] = useState(Date.now().toString());
  const [chatHistory, setChatHistory] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');

  // Sync active messages to the chat history
  useEffect(() => {
    if (messages.length > 0) {
      setChatHistory(prev => {
        const exists = prev.find(c => c.id === currentChatId);
        
        let title = 'New Conversation';
        const firstUserMsg = messages.find(m => m.role === 'user')?.content || '';
        const isQuiz = messages.some(m => m._cmd === 'QUIZ');
        const isAssess = messages.some(m => m._cmd === 'ASSESS');
        
        if (isQuiz) {
             title = '🧠 Quiz Attempt: Cyberbullying Basics';
        } else if (isAssess) {
             title = '🧪 Assessment: Severity classification';
        } else if (firstUserMsg.includes('Analyze this text:')) {
             title = '💬 Analysis: ' + firstUserMsg.replace('Analyze this text:', '').replace(/"/g, '').trim().substring(0, 20) + '...';
        } else if (firstUserMsg) {
             title = '💬 ' + firstUserMsg.substring(0, 25) + (firstUserMsg.length > 25 ? '...' : '');
        }

        if (exists) {
            return prev.map(c => c.id === currentChatId ? { ...c, title, messages } : c);
        } else {
            return [{ id: currentChatId, title, messages }, ...prev];
        }
      });
    }
  }, [messages, currentChatId]);

  const startNewChat = () => {
    setCurrentChatId(Date.now().toString());
    setMessages([]);
    setActiveModule('CHAT');
    setRefreshKey(prev => prev + 1);
  };

  const clearHistory = () => {
    setChatHistory([]);
    startNewChat();
  };

  const filteredHistory = chatHistory.filter((chat) =>
    chat.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="flex h-screen bg-[#0a0a0a] bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-[#13131a] via-[#0a0a0a] to-[#050505] text-textMain overflow-hidden font-inter selection:bg-accent/30 tracking-wide">
      {/* Sidebar - Premium Dark Mode Glassmorphism */}
      <motion.div 
        initial={{ x: -100 }}
        animate={{ x: 0 }}
        className="w-[260px] border-r border-white/5 bg-black/40 backdrop-blur-2xl flex-col p-3 transition-all duration-300 z-10 hidden md:flex shadow-2xl"
      >
        <button className="flex items-center gap-3 p-3 mb-4 mt-2 rounded-xl text-textMain hover:bg-white/5 transition-all w-full select-none" onClick={startNewChat}>
          <div className="bg-accent/20 p-2 rounded-lg text-accent shadow-sm">
            <Shield className="w-5 h-5" />
          </div>
          <span className="font-semibold text-[15px] tracking-tight">CyberGuard AI</span>
        </button>

        <button onClick={startNewChat} className="flex items-center justify-between p-2.5 mb-4 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 text-textMain transition-all w-full shadow-lg backdrop-blur-md text-sm font-medium group">
          <span className="flex items-center gap-2">
             <PlusCircle className="w-4 h-4 ml-1 text-textMuted group-hover:text-accent transition-colors" />
             New Chat
          </span>
        </button>

        {/* Search Chats Input */}
        <div className="relative mb-4 group">
           <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-textMuted group-focus-within:text-accent transition-colors" />
           <input 
             type="text" 
             placeholder="Search chats..."
             value={searchQuery}
             onChange={(e) => setSearchQuery(e.target.value)}
             className="w-full bg-white/5 border border-white/5 focus:border-accent/50 rounded-xl py-2 pl-9 pr-3 text-sm text-textMain placeholder-textMuted/70 outline-none transition-all focus:ring-2 focus:ring-accent/20"
           />
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto pr-1 custom-scrollbar">
          <div className="text-xs font-semibold text-textMuted px-3 py-2 mb-1 tracking-wider uppercase">History</div>
          {filteredHistory.length === 0 ? (
             <div className="text-center text-textMuted text-xs mt-4">No chats found.</div>
          ) : (
            <AnimatePresence>
              {filteredHistory.map(chat => {
                const isActive = currentChatId === chat.id && activeModule === 'CHAT';
                return (
                  <motion.button
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    key={chat.id}
                    onClick={() => {
                      setCurrentChatId(chat.id);
                      setMessages(chat.messages);
                      setActiveModule('CHAT');
                    }}
                    className={`w-full flex items-center gap-3 p-2.5 px-3 rounded-xl transition-all duration-200 text-left text-[14px] truncate ${
                      isActive ? 'bg-white/10 text-white font-medium shadow-md backdrop-blur-md border border-white/5' : 'text-textMuted hover:bg-white/5 font-medium border border-transparent hover:text-textMain'
                    }`}
                  >
                    <MessageSquare className={`w-[16px] h-[16px] flex-shrink-0 ${isActive ? 'text-accent' : 'opacity-60'}`} />
                    <span className="truncate">{chat.title}</span>
                  </motion.button>
                )
              })}
            </AnimatePresence>
          )}
        </nav>

        <div className="mt-auto border-t border-white/5 pt-3">
          <button
            onClick={clearHistory}
            className="w-full flex items-center gap-3 p-2.5 px-3 rounded-xl text-red-400/80 hover:bg-red-500/10 hover:text-red-400 transition-all text-[14px] font-medium"
          >
            <Trash2 className="w-[18px] h-[18px] flex-shrink-0" />
            <span>Clear Operations</span>
          </button>
        </div>
      </motion.div>

      {/* Main Content Area */}
      <div className="flex-1 relative bg-transparent flex flex-col min-w-0">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeModule}
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.02 }}
            transition={{ duration: 0.4, ease: [0.23, 1, 0.32, 1] }}
            className="absolute inset-0 flex flex-col"
          >
            <ChatView 
               activeModule={activeModule} 
               messages={messages} 
               setMessages={setMessages} 
               refreshKey={refreshKey}
               onChangeModule={setActiveModule}
            />
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}
