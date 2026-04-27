import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldAlert, ShieldCheck, Sparkles, User, Bot } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import QuizComponent from './QuizComponent';
import AssessmentComponent from './AssessmentComponent';

export default function MessageBubble({ msg, onRewrite, isExplicitRequest, isShortUserMsg, isProcessing }) {
  const isUser = msg.role === 'user';
  
  const extractJSON = (text) => {
    if (!text) return null;
    const match = text.match(/```json\s*([\s\S]*?)\s*```/);
    if (match) {
      try {
        return JSON.parse(match[1]);
      } catch (e) {
        console.error("Failed to parse JSON module:", e);
      }
    }
    if (text.trim().startsWith('{') && text.trim().endsWith('}')) {
       try { return JSON.parse(text.trim()); } catch(e) {}
    }
    return null;
  };

  // 1. Module Loading Interceptor
  if ((msg._cmd === 'QUIZ' || msg._cmd === 'ASSESS') && isProcessing) {
      return (
         <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="flex w-full justify-start py-4 group">
           <div className="flex gap-4 w-full max-w-4xl flex-row">
             <div className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center shadow-sm bg-surface border border-border text-textMain">
               <Bot className="w-6 h-6" />
             </div>
             <div className="items-start flex flex-col justify-center">
                 <div className="p-4 rounded-2xl bg-surface/50 border border-white/5 flex items-center gap-4 shadow-sm backdrop-blur-sm">
                     <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-accent"></div>
                     <span className="text-sm font-medium text-textMain/80 tracking-wide">
                         {msg._cmd === 'QUIZ' ? 'Generating adaptive quiz structure...' : 'Preparing mixed assessment paragraph...'}
                     </span>
                 </div>
             </div>
           </div>
         </motion.div>
      );
  }

  // 2. Strict Module Extractor (No raw JSON allowed. Fallback if model failed)
  if ((msg._cmd === 'QUIZ' || msg._cmd === 'ASSESS') && !isProcessing) {
      let interactiveData = extractJSON(msg.content);
      
      // Fallback Engine guarantees no blank screen or broken JSON dumps
      if (!interactiveData || !interactiveData.type) {
          if (msg._cmd === 'QUIZ') {
              interactiveData = {
                  type: 'quiz',
                  questions: [
                      { id: 1, question: "What is cyberbullying?", options: ["A) Normal gameplay", "B) Repeated online harassment", "C) Eating", "D) Sleeping"], answer: "B) Repeated online harassment", explanation: "Repeated harassment defines cyberbullying." },
                      { id: 2, question: "How should you respond to trolling?", options: ["A) Feed them", "B) Ignore and Block", "C) Yell back", "D) Delete system32"], answer: "B) Ignore and Block", explanation: "Do not respond to provocations." },
                      { id: 3, question: "What is doxxing?", options: ["A) Boxing tournament", "B) Revealing private information", "C) A type of firewall", "D) Email spam"], answer: "B) Revealing private information", explanation: "Doxxing is malicious public disclosure." },
                      { id: 4, question: "What is the best way to report abuse?", options: ["A) Use platform reporting tools", "B) Email police", "C) Call a friend", "D) Do nothing"], answer: "A) Use platform reporting tools", explanation: "Report directly on the platform where it occurred." },
                      { id: 5, question: "Is purposeful social exclusion a form of abuse?", options: ["A) Yes", "B) No", "C) Maybe", "D) Only in games"], answer: "A) Yes", explanation: "Social exclusion is a toxic behavioral pattern." }
                  ]
              };
          } else {
              interactiveData = {
                  type: 'assessment',
                  paragraph: "The team meeting went exceptionally well today. Afterwards though, John pulled me aside and said he thinks the new intern is completely worthless and shouldn't be allowed to speak. I told him he should just calm down. 'I'll make sure he regrets ever applying here,' John replied.",
                  questions: [
                      { id: 1, question: "Which phrase indicates a direct insult aiming to dehumanize?", options: ["A) The meeting went well", "B) Completely worthless and shouldn't be allowed to speak", "C) I told him to calm down", "D) He pulled me aside"], answer: "B) Completely worthless and shouldn't be allowed to speak", explanation: "Dehumanizing language and shutting down voices is a form of verbal abuse." },
                      { id: 2, question: "Identify the sentence that contains a direct implicit threat.", options: ["A) The meeting went exceptionally well", "B) John pulled me aside", "C) I'll make sure he regrets ever applying here", "D) I told him he should just calm down"], answer: "C) I'll make sure he regrets ever applying here", explanation: "This implies targeted retaliation or future malicious action against the intern." },
                      { id: 3, question: "What severity level best describes John's behavior in the paragraph?", options: ["A) Safe", "B) Low", "C) Medium", "D) High"], answer: "D) High", explanation: "Combining direct dehumanization with a vow for retaliation warrants a High severity flag." },
                      { id: 4, question: "How should the narrator act following John's statements?", options: ["A) Ignore him completely", "B) Report the threat to HR or a manager", "C) Tell the intern to leave", "D) Join in on the insults"], answer: "B) Report the threat to HR or a manager", explanation: "Actionable threats in a professional environment must be escalated." },
                      { id: 5, question: "Is the first sentence of the paragraph safe?", options: ["A) Yes", "B) No, it's sarcastic", "C) Maybe", "D) Only if John said it"], answer: "A) Yes", explanation: "It is a purely neutral recounting of a positive event." }
                  ]
              };
          }
      }
      
      return (
         <div className="flex w-full justify-start py-4">
             {msg._cmd === 'QUIZ' ? <QuizComponent data={interactiveData} /> : <AssessmentComponent data={interactiveData} />}
         </div>
      );
  }

  const interactiveData = extractJSON(msg.content);

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} py-4 group`}
    >
      <div className={`flex gap-4 w-full max-w-4xl ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        
        {/* Avatar */}
        <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center shadow-sm ${isUser ? 'bg-accent/20 text-accent' : 'bg-surface border border-border text-textMain'}`}>
          {isUser ? <User className="w-5 h-5" /> : <Bot className="w-6 h-6" />}
        </div>
        
        {/* Message Content */}
        <div className={`max-w-[85%] md:max-w-[80%] ${isUser ? 'items-end flex flex-col' : 'items-start flex flex-col'}`}>
          <div className={`relative rounded-2xl p-4 shadow-sm ${
            isUser 
              ? 'bg-white/10 border border-white/5 text-textMain backdrop-blur-md' 
              : 'bg-transparent text-textMain/90'
          }`}>
             {msg.bert_info && !isUser && !isExplicitRequest && !isShortUserMsg && (
               <div 
                 title={`Risk Score: ${msg.bert_info.risk_score}%`}
                 className={`absolute -right-[6px] -top-[6px] w-[14px] h-[14px] rounded-full border-2 border-[#0a0a0a] z-10 ${
                   msg.bert_info.risk_score >= 70
                     ? 'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.6)]' 
                     : msg.bert_info.risk_score >= 40
                     ? 'bg-yellow-500 shadow-[0_0_10px_rgba(234,179,8,0.5)]'
                     : 'bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.4)]'
                 }`} 
               />
             )}
            <div className={`
              prose prose-invert max-w-none text-[15px] leading-relaxed
              prose-p:leading-relaxed prose-p:my-1
              prose-headings:text-textMain prose-headings:font-semibold
              prose-h2:text-[15px] prose-h2:mt-4 prose-h2:mb-2 prose-h2:border-b prose-h2:border-white/10 prose-h2:pb-1
              prose-h3:text-[15px] prose-h3:mt-4 prose-h3:mb-2
              prose-strong:text-textMain prose-strong:font-semibold
              prose-ul:my-2 prose-ul:space-y-1
              prose-ol:my-2 prose-ol:space-y-1
              prose-li:my-0.5 prose-li:text-textMain/90
              prose-code:text-blue-300 prose-code:bg-[#1a1a2e] prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-[13px]
              prose-pre:bg-[#0d0d1a] prose-pre:border prose-pre:border-border prose-pre:rounded-xl prose-pre:text-[13px]
              prose-blockquote:border-l-2 prose-blockquote:border-accent/50 prose-blockquote:pl-4 prose-blockquote:italic
              prose-hr:border-[#2a2a2a]
            `}>
              {interactiveData ? (
                interactiveData.type === 'quiz' ? <QuizComponent data={interactiveData} /> :
                interactiveData.type === 'assessment' ? <AssessmentComponent data={interactiveData} /> :
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
              ) : (
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {msg.content}
                </ReactMarkdown>
              )}
            </div>
          </div>

          {/* Diagnostic Metadata Block - Only for explicit AI responses */}
          {msg.bert_info && !isUser && isExplicitRequest && (
            <AnimatePresence>
              <motion.div 
                initial={{ opacity: 0, height: 0, marginTop: 0 }}
                animate={{ opacity: 1, height: 'auto', marginTop: 16 }}
                className="w-full max-w-sm border border-border bg-surface rounded-xl overflow-hidden shadow-lg"
              >
                <div className={`p-3 flex items-center gap-3 border-b border-white/5 backdrop-blur-md ${
                    msg.bert_info.is_threat ? 'bg-red-500/10' : 'bg-green-500/10'
                }`}>
                  {msg.bert_info.is_threat ? <ShieldAlert className="text-red-400 w-5 h-5" /> : <ShieldCheck className="text-green-400 w-5 h-5" />}
                  <div>
                    <div className={`text-sm font-semibold tracking-wide ${msg.bert_info.is_threat ? 'text-red-400' : 'text-green-400'}`}>
                      {msg.bert_info.is_threat ? 'Cyberbullying Detected' : 'Content Verified Safe'}
                    </div>
                    <div className="text-xs text-textMuted mt-0.5 font-medium">
                      Confidence Score: {(msg.bert_info.confidence * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>
                


              </motion.div>
            </AnimatePresence>
          )}
        </div>
      </div>
    </motion.div>
  );
}
