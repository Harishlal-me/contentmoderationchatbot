import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, XCircle, ChevronRight } from 'lucide-react';

export default function QuizComponent({ data }) {
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);

  if (!data || !data.questions) return null;

  const handleSelect = (qId, optionBoxText) => {
    if (submitted) return;
    setAnswers(prev => ({ ...prev, [qId]: optionBoxText }));
  };

  const calculateScore = () => {
    let score = 0;
    data.questions.forEach(q => {
      // We check if the selected option string starts with the answer or matches
      if (answers[q.id] === q.answer || (answers[q.id] && q.answer.startsWith(answers[q.id].substring(0, 2)))) {
        score++;
      }
    });
    return score;
  };

  return (
    <div className="w-full mt-4 space-y-6">
      <div className="bg-accent/10 border border-accent/20 rounded-xl p-4">
        <h3 className="text-lg font-semibold text-accent mb-1">Cyberbullying Detection Quiz</h3>
        <p className="text-sm text-textMuted">Select the best answer for each scenario.</p>
      </div>

      <div className="space-y-8">
        {data.questions.map((q, idx) => {
          const isCorrect = answers[q.id] === q.answer || (answers[q.id] && q.answer.startsWith(answers[q.id].substring(0, 2)));
          
          return (
            <motion.div 
              initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.1 }}
              key={q.id || idx} className="bg-surface/50 border border-white/5 rounded-2xl p-5 shadow-sm"
            >
              <h4 className="text-[15px] font-medium text-textMain mb-4">
                <span className="text-accent mr-2">{idx + 1}.</span> {q.question}
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
                    optStyle = "bg-accent/20 border-accent/50 text-accent";
                  }

                  return (
                    <button
                      key={i}
                      onClick={() => handleSelect(q.id, opt)}
                      disabled={submitted}
                      className={`w-full text-left px-4 py-3 rounded-xl border transition-all text-sm flex items-center justify-between ${optStyle}`}
                    >
                      <span>{opt}</span>
                      {submitted && (opt === q.answer || q.answer.startsWith(opt.substring(0, 2))) && <CheckCircle2 className="w-5 h-5" />}
                      {submitted && isSelected && !(opt === q.answer || q.answer.startsWith(opt.substring(0, 2))) && <XCircle className="w-5 h-5" />}
                    </button>
                  );
                })}
              </div>

              {submitted && (
                <div className={`mt-4 p-3 rounded-lg text-sm border ${isCorrect ? 'bg-green-500/10 border-green-500/20 text-green-400' : 'bg-red-500/10 border-red-500/20 text-red-400'}`}>
                  <strong>{isCorrect ? 'Correct!' : 'Incorrect.'}</strong> {q.explanation}
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
          className="w-full mt-4 py-3 bg-accent text-white rounded-xl font-semibold hover:bg-accent/90 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_20px_rgba(139,92,246,0.3)]"
        >
          Submit Answers
        </button>
      ) : (
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="mt-8 p-6 bg-gradient-to-r from-accent/20 to-blue-500/20 border border-white/10 rounded-2xl text-center shadow-lg">
          <h3 className="text-2xl font-bold text-white mb-2">Quiz Complete!</h3>
          <p className="text-lg text-textMuted mb-4">You scored <span className="text-accent font-bold">{calculateScore()}</span> out of {data.questions.length}</p>
        </motion.div>
      )}
    </div>
  );
}
