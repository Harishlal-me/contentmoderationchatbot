import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X, Brain, TrendingUp, MessageSquare, RefreshCw,
  ShieldAlert, ShieldCheck, Minus, Lightbulb, Target, Clock,
  ArrowUp, ArrowDown, ArrowRight, BarChart2,
} from 'lucide-react';
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement,
  LineElement, Tooltip, Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler);

// ── Helpers ──────────────────────────────────────────────────
const STATUS_META = {
  '🔴 UNSAFE':  { color: 'text-red-400',    bg: 'bg-red-500/10',    border: 'border-red-500/20',    icon: ShieldAlert },
  '🟡 WARNING': { color: 'text-yellow-400', bg: 'bg-yellow-500/10', border: 'border-yellow-500/20', icon: Minus       },
  '🟢 SAFE':    { color: 'text-green-400',  bg: 'bg-green-500/10',  border: 'border-green-500/20',  icon: ShieldCheck },
};
const getMeta = (s) => STATUS_META[s] || STATUS_META['🟢 SAFE'];

function getBarColor(score) {
  return score >= 70 ? '#ef4444' : score >= 40 ? '#eab308' : '#22c55e';
}

function RiskBar({ score }) {
  return (
    <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden mt-1">
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${score}%` }}
        transition={{ duration: 0.7, ease: 'easeOut' }}
        className="h-full rounded-full"
        style={{ backgroundColor: getBarColor(score) }}
      />
    </div>
  );
}

function TrendArrow({ prev, curr }) {
  if (prev === undefined) return null;
  const diff = curr - prev;
  if (diff > 5)  return <ArrowUp   className="w-3 h-3 text-red-400 inline ml-1" />;
  if (diff < -5) return <ArrowDown className="w-3 h-3 text-green-400 inline ml-1" />;
  return <ArrowRight className="w-3 h-3 text-textMuted inline ml-1" />;
}

// ── Main Component ────────────────────────────────────────────
export default function SessionPanel({ open, onClose, session, onRefresh }) {
  const {
    stats      = { total: 0, toxic: 0, avg: 0 },
    history    = [],
    insight    = 'Not enough data yet — send more messages to see trends.',
    suggestion = '',
  } = session || {};

  const safeCount = stats.total - stats.toxic;
  const memActive = history.length > 0;
  const ctxActive = history.length > 2;
  const scores    = history.map(m => m.risk_score);

  // ── Chart.js data ──
  const chartData = {
    labels: history.map((m, i) => `Msg ${i + 1}\n${m.time || ''}`),
    datasets: [{
      label: 'Risk Score',
      data: scores,
      fill: true,
      tension: 0.45,
      borderColor: '#6366f1',
      backgroundColor: 'rgba(99,102,241,0.10)',
      pointBackgroundColor: scores.map(s => getBarColor(s)),
      pointBorderColor: '#0a0a0a',
      pointRadius: 5,
      pointHoverRadius: 7,
    }],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false }, tooltip: {
      backgroundColor: '#111113',
      titleColor: '#fff',
      bodyColor: '#888',
      borderColor: '#2a2a2a',
      borderWidth: 1,
      callbacks: {
        label: ctx => ` Risk: ${ctx.parsed.y}%`,
      },
    }},
    scales: {
      x: { ticks: { color: '#555', font: { size: 10 } }, grid: { color: '#1a1a1a' } },
      y: { min: 0, max: 100, ticks: { color: '#555', font: { size: 10 }, callback: v => `${v}%` }, grid: { color: '#1a1a1a' } },
    },
  };

  // ── Insight icon mapping ──
  const insightIcon = insight.includes('worsening') ? '📉' : insight.includes('improving') ? '📈' : '📊';

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
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
            onClick={onClose}
          />

          {/* Panel */}
          <motion.div
            key="panel"
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 28, stiffness: 260 }}
            className="fixed right-0 top-0 h-full w-[410px] bg-[#0c0c0e] border-l border-white/8 shadow-2xl z-50 flex flex-col"
          >

            {/* ── Header ── */}
            <div className="flex items-center justify-between px-5 py-4 border-b border-white/8 flex-shrink-0">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-accent/15 flex items-center justify-center">
                  <BarChart2 className="w-4 h-4 text-accent" />
                </div>
                <div>
                  <h2 className="font-semibold text-[14px] text-textMain tracking-tight">Analysis Dashboard</h2>
                  <p className="text-[11px] text-textMuted mt-0.5">Live · updates after every message</p>
                </div>
              </div>
              <div className="flex items-center gap-1.5">
                <button onClick={onRefresh} title="Refresh"
                  className="p-1.5 rounded-lg text-textMuted hover:text-textMain hover:bg-white/5 transition-all">
                  <RefreshCw className="w-3.5 h-3.5" />
                </button>
                <button onClick={onClose}
                  className="p-1.5 rounded-lg text-textMuted hover:text-textMain hover:bg-white/5 transition-all">
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* ── Scrollable Body ── */}
            <div className="flex-1 overflow-y-auto custom-scrollbar">

              {/* ━━━━━━━━━━━━━━━━━━━━━━━━
                  SECTION 1 — Performance Tracker
              ━━━━━━━━━━━━━━━━━━━━━━━━ */}
              <div className="px-5 py-4 border-b border-white/5">
                <div className="flex items-center gap-2 mb-3">
                  <TrendingUp className="w-4 h-4 text-accent" />
                  <span className="text-[12px] font-semibold text-textMuted tracking-wider uppercase">Behavior Performance Tracker</span>
                </div>

                {/* Graph */}
                <div className="h-[160px] w-full mb-4">
                  {scores.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-textMuted">
                      <TrendingUp className="w-8 h-8 mb-2 opacity-15" />
                      <p className="text-[12px]">No data yet — analyze a message first.</p>
                    </div>
                  ) : (
                    <Line data={chartData} options={chartOptions} />
                  )}
                </div>

                {/* Insight */}
                <div className="rounded-xl bg-white/3 border border-white/8 p-3 mb-3">
                  <div className="flex items-center gap-1.5 mb-1">
                    <Target className="w-3.5 h-3.5 text-purple-400" />
                    <span className="text-[11px] font-semibold text-textMuted uppercase tracking-wider">Insight</span>
                  </div>
                  <p className="text-[13px] text-textMain">
                    <span className="mr-1">{insightIcon}</span>{insight}
                  </p>
                </div>

                {/* Suggestion */}
                {suggestion && (
                  <div className="rounded-xl bg-accent/5 border border-accent/15 p-3">
                    <div className="flex items-center gap-1.5 mb-1">
                      <Lightbulb className="w-3.5 h-3.5 text-accent" />
                      <span className="text-[11px] font-semibold text-accent/80 uppercase tracking-wider">Suggestion</span>
                    </div>
                    <p className="text-[13px] text-textMain/90">{suggestion}</p>
                  </div>
                )}
              </div>

              {/* ━━━━━━━━━━━━━━━━━━━━━━━━
                  SECTION 2 — Session Analysis
              ━━━━━━━━━━━━━━━━━━━━━━━━ */}
              <div className="px-5 py-4 border-b border-white/5">
                <div className="flex items-center gap-2 mb-3">
                  <Brain className="w-4 h-4 text-purple-400" />
                  <span className="text-[12px] font-semibold text-textMuted tracking-wider uppercase">Session Analysis</span>
                </div>

                {/* Stats row */}
                <div className="grid grid-cols-3 gap-2 mb-3">
                  {[
                    { label: 'Total',  value: stats.total,  color: 'text-textMain'  },
                    { label: 'Toxic',  value: stats.toxic,  color: 'text-red-400'   },
                    { label: 'Safe',   value: safeCount,    color: 'text-green-400' },
                  ].map(({ label, value, color }) => (
                    <div key={label} className="bg-white/4 rounded-xl p-3 text-center border border-white/5">
                      <div className={`text-[20px] font-bold ${color}`}>{value}</div>
                      <div className="text-[10px] text-textMuted mt-0.5">{label}</div>
                    </div>
                  ))}
                </div>

                {/* Avg bar */}
                <div className="bg-white/4 rounded-xl p-3 border border-white/5 mb-3">
                  <div className="flex justify-between text-[12px]">
                    <span className="text-textMuted">Avg Risk Score</span>
                    <span className={`font-bold ${stats.avg >= 70 ? 'text-red-400' : stats.avg >= 40 ? 'text-yellow-400' : 'text-green-400'}`}>
                      {stats.avg}%
                    </span>
                  </div>
                  <RiskBar score={stats.avg} />
                </div>

                {/* System status */}
                <div className="space-y-1.5">
                  {[
                    { label: 'Memory',            active: memActive, info: memActive ? 'Tracking session'     : 'No data yet'      },
                    { label: 'Context Awareness', active: ctxActive, info: ctxActive ? 'Escalation tracking'  : 'Need 3+ messages' },
                    { label: 'BERT Classifier',   active: true,      info: 'Active'                                                },
                    { label: 'LLM Reasoning',     active: true,      info: 'llama3.2 · Ollama'                                     },
                  ].map(({ label, active, info }) => (
                    <div key={label} className="flex items-center justify-between px-3 py-1.5 rounded-lg bg-white/3 border border-white/5">
                      <span className="text-[12px] text-textMain">{label}</span>
                      <div className="flex items-center gap-1.5">
                        <div className={`w-1.5 h-1.5 rounded-full ${active ? 'bg-green-400' : 'bg-white/20'}`} />
                        <span className={`text-[11px] ${active ? 'text-green-400' : 'text-textMuted'}`}>{info}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* ━━━━━━━━━━━━━━━━━━━━━━━━
                  SECTION 3 — Conversation Breakdown
              ━━━━━━━━━━━━━━━━━━━━━━━━ */}
              <div className="px-5 py-4 border-b border-white/5">
                <div className="flex items-center gap-2 mb-3">
                  <MessageSquare className="w-4 h-4 text-accent" />
                  <span className="text-[12px] font-semibold text-textMuted tracking-wider uppercase">Conversation Breakdown</span>
                </div>

                {history.length === 0 ? (
                  <div className="text-center py-8 text-textMuted">
                    <MessageSquare className="w-7 h-7 mx-auto mb-2 opacity-15" />
                    <p className="text-[12px]">No analyzed messages yet.</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {[...history].reverse().map((msg, i, arr) => {
                      const meta = getMeta(msg.status);
                      const Icon = meta.icon;
                      const realIdx = arr.length - 1 - i;
                      const prevScore = realIdx > 0 ? history[realIdx - 1].risk_score : undefined;
                      return (
                        <motion.div
                          key={i}
                          initial={{ opacity: 0, y: 6 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: i * 0.03 }}
                          className={`rounded-xl p-3 border ${meta.bg} ${meta.border} hover:brightness-110 transition-all`}
                        >
                          <p className="text-[13px] text-textMain font-medium leading-snug line-clamp-2 mb-2">
                            "{msg.text}"
                          </p>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-1.5">
                              <Icon className={`w-3.5 h-3.5 ${meta.color}`} />
                              <span className={`text-[12px] font-semibold ${meta.color}`}>{msg.status}</span>
                            </div>
                            <span className="text-[11px] text-textMuted">
                              {msg.risk_score}%
                              <TrendArrow prev={prevScore} curr={msg.risk_score} />
                            </span>
                          </div>
                          <RiskBar score={msg.risk_score} />
                          <p className="text-[11px] text-textMuted mt-1.5">→ {msg.summary}</p>
                        </motion.div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* ━━━━━━━━━━━━━━━━━━━━━━━━
                  SECTION 4 — Timeline
              ━━━━━━━━━━━━━━━━━━━━━━━━ */}
              <div className="px-5 py-4">
                <div className="flex items-center gap-2 mb-3">
                  <Clock className="w-4 h-4 text-blue-400" />
                  <span className="text-[12px] font-semibold text-textMuted tracking-wider uppercase">Timeline</span>
                </div>

                {history.length === 0 ? (
                  <p className="text-[12px] text-textMuted text-center py-4">No timeline data yet.</p>
                ) : (
                  <div className="space-y-1.5">
                    {history.map((msg, i) => {
                      const meta   = getMeta(msg.status);
                      const prev   = i > 0 ? history[i - 1].risk_score : undefined;
                      return (
                        <div key={i} className="flex items-center gap-2 text-[12px]">
                          <span className="text-textMuted w-10 flex-shrink-0 font-mono">Msg {i + 1}</span>
                          <span className="text-textMuted/60 font-mono w-16 flex-shrink-0">{msg.time || '--:--:--'}</span>
                          <span className={`font-semibold ${meta.color} flex items-center gap-1`}>
                            {msg.status.split(' ')[0]} {msg.risk_score}%
                            <TrendArrow prev={prev} curr={msg.risk_score} />
                          </span>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>

            {/* Footer */}
            <div className="px-5 py-2.5 border-t border-white/5 flex items-center gap-2 flex-shrink-0">
              <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
              <span className="text-[11px] text-textMuted">Updated till latest message</span>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
