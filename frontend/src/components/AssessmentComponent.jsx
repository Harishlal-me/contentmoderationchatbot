import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, XCircle, BookOpen } from 'lucide-react';

export default function AssessmentComponent({ data }) {
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);

  // Validate the new scenario-based structure
  if (!data || !data.paragraph || !data.questions) return null;

  const handleSelect = (qId, optionText) => {
    if (submitted) return;
    setAnswers(prev => ({ ...prev, [qId]: optionText }));
  };

  const calculateScore = () => {
    let score = 0;
    data.questions.forEach(q => {
      if (answers[q.id] === q.answer || (answers[q.id] && q.answer.startsWith(answers[q.id].substring(0, 2)))) {
        score++;
      }
    });
    return score;
  };

  return (
    <div className="w-full mt-4 space-y-6">
      <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-4">
        <h3 className="text-lg font-semibold text-blue-400 mb-1">Scenario Assessment</h3>
        <p className="text-sm text-textMuted">Read the paragraph below and evaluate the moderation scenarios.</p>
      </div>

      {/* The Context Paragraph Block */}
      <motion.div 
        initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
        className="bg-[#11111a] border border-white/5 shadow-md rounded-2xl p-6 relative overflow-hidden"
      >
        <div className="absolute top-0 left-0 w-1 h-full bg-blue-500/50"></div>
        <div className="flex items-center gap-3 mb-4">
          <BookOpen className="w-5 h-5 text-blue-400" />
          <h4 className="font-semibold text-textMain tracking-wide">Context Paragraph</h4>
        </div>
        <p className="text-[15px] font-medium text-textMain/90 leading-relaxed italic border-l-2 border-white/10 pl-4 py-1">
          "{data.paragraph}"
        </p>
      </motion.div>

      {/* The Questions Mapping */}
      <div className="space-y-6 pt-4">
        {data.questions.map((q, idx) => {
          const isCorrect = answers[q.id] === q.answer || (answers[q.id] && q.answer.startsWith(answers[q.id].substring(0, 2)));
          
          return (
            <motion.div 
              initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.1 }}
              key={q.id || idx} className="bg-surface/50 border border-white/5 rounded-2xl p-5 shadow-sm"
            >
              <h4 className="text-[14px] font-medium text-textMain mb-4 leading-snug">
                <span className="text-blue-400 font-bold mr-2">Q{idx + 1}.</span> {q.question}
              </h4>
              
              <div className="space-y-2">
                {q.options.map((opt, i) => {
                  const isSelected = answers[q.id] === opt;
                  let optStyle = "bg-white/5 border-white/10 hover:bg-white/10 text-textMain/90";
                  
                  if (submitted) {
                    const isWinningOpt = opt === q.answer || q.answer.startsWith(opt.substring(0, 2));
                    if (isWinningOpt) optStyle = "bg-green-500/20 border-green-500/50 text-green-400";
                    else if (isSelected) optStyle = "bg-red-500/20 border-red-500/50 text-red-400";
                    else optStyle = "bg-white/5 border-transparent opacity-50";
                  } else if (isSelected) {
                    optStyle = "bg-blue-500/20 border-blue-500/50 text-blue-400";
                  }

                  return (
                    <button
                      key={i}
                      onClick={() => handleSelect(q.id, opt)}
                      disabled={submitted}
                      className={`w-full text-left px-4 py-3 rounded-xl border transition-all text-[13px] font-medium flex items-center justify-between ${optStyle}`}
                    >
                      <span className="leading-snug pr-4">{opt}</span>
                      {submitted && (opt === q.answer || q.answer.startsWith(opt.substring(0, 2))) && <CheckCircle2 className="w-5 h-5 flex-shrink-0" />}
                      {submitted && isSelected && !(opt === q.answer || q.answer.startsWith(opt.substring(0, 2))) && <XCircle className="w-5 h-5 flex-shrink-0" />}
                    </button>
                  );
                })}
              </div>

              {submitted && (
                <div className={`mt-4 p-3 rounded-lg text-sm border ${isCorrect ? 'bg-green-500/10 border-green-500/20 text-green-400' : 'bg-red-500/10 border-red-500/20 text-red-400'}`}>
                  <strong>{isCorrect ? 'Correct!' : 'Incorrect.'}</strong> <span className="opacity-90">{q.explanation}</span>
                </div>
              )}
            </motion.div>
          );
        })}
      </div>

      {!submitted ? (
        <button
          onClick={() => setSubmitted(true)}
          disabled={Object.keys(answers).length !== data.questions.length}
          className="w-full mt-6 py-3.5 bg-blue-500 text-white rounded-xl font-semibold hover:bg-blue-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_20px_rgba(59,130,246,0.3)] tracking-wide"
        >
          Submit Assessment
        </button>
      ) : (
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="mt-8 p-6 bg-gradient-to-r from-blue-500/20 to-purple-500/20 border border-white/10 rounded-2xl text-center shadow-lg">
          <h3 className="text-2xl font-bold text-white mb-2">Assessment Graded!</h3>
          <p className="text-lg text-textMuted mb-2">You scored <span className="text-blue-400 font-bold">{calculateScore()}</span> out of {data.questions.length}</p>
          <button onClick={() => window.location.reload()} className="text-xs text-textMuted/70 hover:text-white transition-colors underline underline-offset-4 mt-2">Run another scenario</button>
        </motion.div>
      )}
    </div>
  );
}
