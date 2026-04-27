import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Brain, TrendingUp, MessageSquare, RefreshCw, ShieldAlert, ShieldCheck, Minus } from 'lucide-react';

const STATUS_META = {
  '🔴 UNSAFE':  { color: 'text-red-400',    bg: 'bg-red-500/10',    border: 'border-red-500/20',    icon: ShieldAlert },
  '🟡 WARNING': { color: 'text-yellow-400', bg: 'bg-yellow-500/10', border: 'border-yellow-500/20', icon: Minus       },
  '🟢 SAFE':    { color: 'text-green-400',  bg: 'bg-green-500/10',  border: 'border-green-500/20',  icon: ShieldCheck },
};

function getMeta(status) {
  return STATUS_META[status] || STATUS_META['🟢 SAFE'];
}

function RiskBar({ score }) {
  const color = score >= 70 ? '#ef4444' : score >= 40 ? '#eab308' : '#22c55e';
  return (
    <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden mt-1">
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${score}%` }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        className="h-full rounded-full"
        style={{ backgroundColor: color }}
      />
    </div>
  );
}

export default function SessionPanel({ open, onClose, session, onRefresh }) {
  const { stats = { total: 0, toxic: 0, avg: 0 }, history = [] } = session || {};
  const prevLen = useRef(0);

  // Pulse effect on new entries
  useEffect(() => {
    prevLen.current = history.length;
  }, [history.length]);

  const safeCount  = stats.total - stats.toxic;
  const toxicPct   = stats.total ? Math.round((stats.toxic / stats.total) * 100) : 0;
  const memActive  = history.length > 0;
  const ctxActive  = history.length > 2;

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            key="backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
            onClick={onClose}
          />

          {/* Slide-in Panel */}
          <motion.div
            key="panel"
            initial={{ x: '100%', opacity: 0.5 }}
            animate={{ x: 0,     opacity: 1   }}
            exit={{    x: '100%', opacity: 0   }}
            transition={{ type: 'spring', damping: 28, stiffness: 280 }}
            className="fixed right-0 top-0 h-full w-[380px] bg-[#0e0e10] border-l border-white/8 shadow-2xl z-50 flex flex-col"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-5 py-4 border-b border-white/8">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-accent/15 flex items-center justify-center">
                  <TrendingUp className="w-4 h-4 text-accent" />
                </div>
                <div>
                  <h2 className="font-semibold text-[14px] text-textMain tracking-tight">Live Session Analysis</h2>
                  <p className="text-[11px] text-textMuted mt-0.5">Updates after every message</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={onRefresh}
                  className="p-1.5 rounded-lg text-textMuted hover:text-textMain hover:bg-white/5 transition-all"
                  title="Refresh"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={onClose}
                  className="p-1.5 rounded-lg text-textMuted hover:text-textMain hover:bg-white/5 transition-all"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto custom-scrollbar">

              {/* ── User Behavior Stats ── */}
              <div className="px-5 py-4 border-b border-white/5">
                <div className="flex items-center gap-2 mb-3">
                  <Brain className="w-4 h-4 text-purple-400" />
                  <span className="text-[12px] font-semibold text-textMuted tracking-wider uppercase">User Behavior</span>
                </div>

                <div className="grid grid-cols-3 gap-3 mb-4">
                  {[
                    { label: 'Total', value: stats.total,   color: 'text-textMain' },
                    { label: 'Toxic', value: stats.toxic,   color: 'text-red-400'  },
                    { label: 'Safe',  value: safeCount,     color: 'text-green-400'},
                  ].map(({ label, value, color }) => (
                    <div key={label} className="bg-white/4 rounded-xl p-3 text-center border border-white/5">
                      <div className={`text-[22px] font-bold ${color}`}>{value}</div>
                      <div className="text-[11px] text-textMuted mt-0.5">{label}</div>
                    </div>
                  ))}
                </div>

                {/* Avg Risk bar */}
                <div className="bg-white/4 rounded-xl p-3 border border-white/5">
                  <div className="flex justify-between items-center text-[12px]">
                    <span className="text-textMuted font-medium">Avg Risk Score</span>
                    <span className={`font-bold ${stats.avg >= 70 ? 'text-red-400' : stats.avg >= 40 ? 'text-yellow-400' : 'text-green-400'}`}>
                      {stats.avg}%
                    </span>
                  </div>
                  <RiskBar score={stats.avg} />
                  {stats.total > 0 && (
                    <div className="text-[11px] text-textMuted mt-2">
                      {toxicPct}% of analyzed messages flagged harmful
                    </div>
                  )}
                </div>
              </div>

              {/* ── System Status ── */}
              <div className="px-5 py-4 border-b border-white/5">
                <div className="flex items-center gap-2 mb-3">
                  <TrendingUp className="w-4 h-4 text-blue-400" />
                  <span className="text-[12px] font-semibold text-textMuted tracking-wider uppercase">System Status</span>
                </div>
                <div className="space-y-2">
                  {[
                    { label: 'Memory',            active: memActive, desc: memActive ? 'Tracking session'       : 'No data yet'        },
                    { label: 'Context Awareness', active: ctxActive, desc: ctxActive ? 'Analysing escalation'   : 'Need 3+ messages'   },
                    { label: 'BERT Classifier',   active: true,      desc: 'Active'                                                    },
                    { label: 'LLM Reasoning',     active: true,      desc: 'Ollama · llama3.2'                                         },
                  ].map(({ label, active, desc }) => (
                    <div key={label} className="flex items-center justify-between py-1.5 px-3 rounded-lg bg-white/3 border border-white/5">
                      <span className="text-[12px] text-textMain">{label}</span>
                      <div className="flex items-center gap-1.5">
                        <div className={`w-1.5 h-1.5 rounded-full ${active ? 'bg-green-400' : 'bg-white/20'}`} />
                        <span className={`text-[11px] ${active ? 'text-green-400' : 'text-textMuted'}`}>{desc}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* ── Conversation Breakdown ── */}
              <div className="px-5 py-4">
                <div className="flex items-center gap-2 mb-3">
                  <MessageSquare className="w-4 h-4 text-accent" />
                  <span className="text-[12px] font-semibold text-textMuted tracking-wider uppercase">Conversation Breakdown</span>
                </div>

                {history.length === 0 ? (
                  <div className="text-center py-10 text-textMuted">
                    <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-20" />
                    <p className="text-[12px]">No analyzed messages yet.</p>
                    <p className="text-[11px] mt-1 opacity-60">Ask me to analyze some text to get started.</p>
                  </div>
                ) : (
                  <div className="space-y-2.5">
                    {[...history].reverse().map((msg, i) => {
                      const meta = getMeta(msg.status);
                      const Icon = meta.icon;
                      return (
                        <motion.div
                          key={i}
                          initial={{ opacity: 0, y: 8 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: i * 0.04 }}
                          className={`rounded-xl p-3 border ${meta.bg} ${meta.border} group hover:brightness-110 transition-all cursor-default`}
                        >
                          {/* Text preview */}
                          <p className="text-[13px] text-textMain font-medium leading-snug line-clamp-2 mb-2">
                            "{msg.text}"
                          </p>

                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-1.5">
                              <Icon className={`w-3.5 h-3.5 ${meta.color}`} />
                              <span className={`text-[12px] font-semibold ${meta.color}`}>{msg.status}</span>
                            </div>
                            <span className="text-[11px] text-textMuted">{msg.risk_score}% risk</span>
                          </div>

                          {/* Risk bar */}
                          <RiskBar score={msg.risk_score} />

                          <p className="text-[11px] text-textMuted mt-2">→ {msg.summary}</p>
                        </motion.div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>

            {/* Footer */}
            <div className="px-5 py-3 border-t border-white/5 flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
              <span className="text-[11px] text-textMuted">Updated till latest message</span>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
