import React from 'react';
import { Cpu, Scale, Sparkles, CheckCircle2, AlertTriangle, RefreshCw } from 'lucide-react';

interface HybridScoreBreakdownProps {
  weightedScore: number;
  semanticScore: number;
  llmScore: number;
  finalScore: number;
  difference: number;
  validationStatus: 'AGREED' | 'RECONCILED' | 'REVIEW_REQUIRED';
  reconciliationNotes?: string;
}

export const HybridScoreBreakdown: React.FC<HybridScoreBreakdownProps> = ({
  weightedScore,
  semanticScore,
  llmScore,
  finalScore,
  difference,
  validationStatus,
  reconciliationNotes
}) => {
  const isAgreed = validationStatus === 'AGREED';
  const isReconciled = validationStatus === 'RECONCILED';

  return (
    <div className="glass-panel rounded-2xl border border-slate-800 p-6 mb-6">
      
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between pb-6 border-b border-slate-800 mb-6 gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-white flex items-center gap-2">
            <Cpu className="w-6 h-6 text-indigo-400" />
            Hybrid AI Score Breakdown & Reconciliation
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Combines Deterministic Weighted Matching (Baseline), Embedding Vector Similarity, and LLM Evidence Analysis.
          </p>
        </div>

        {/* Validation Status Badge */}
        <div className="flex items-center space-x-2">
          <span className={`px-3 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 border ${
            isAgreed
              ? 'bg-emerald-950/80 text-emerald-300 border-emerald-500/40 shadow-lg shadow-emerald-500/20'
              : isReconciled
              ? 'bg-purple-950/80 text-purple-300 border-purple-500/40 shadow-lg shadow-purple-500/20'
              : 'bg-amber-950/80 text-amber-300 border-amber-500/40 shadow-lg shadow-amber-500/20'
          }`}>
            {isAgreed ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            ) : isReconciled ? (
              <RefreshCw className="w-4 h-4 text-purple-400" />
            ) : (
              <AlertTriangle className="w-4 h-4 text-amber-400" />
            )}
            <span>STATUS: {validationStatus}</span>
          </span>
        </div>
      </div>

      {/* 3 Signal Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        
        {/* Signal A: Weighted Baseline */}
        <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
          <div className="text-xs font-semibold text-indigo-400 uppercase tracking-wider mb-1">
            Signal A: Weighted Baseline
          </div>
          <div className="text-2xl font-extrabold text-white">{weightedScore}%</div>
          <p className="text-[11px] text-slate-400 mt-1">Deterministic DB calculation</p>
        </div>

        {/* Signal B: Semantic Similarity */}
        <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
          <div className="text-xs font-semibold text-cyan-400 uppercase tracking-wider mb-1">
            Signal B: Semantic Similarity
          </div>
          <div className="text-2xl font-extrabold text-white">{semanticScore}%</div>
          <p className="text-[11px] text-slate-400 mt-1">Cosine vector similarity</p>
        </div>

        {/* Signal C: LLM Evidence Evaluation */}
        <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
          <div className="text-xs font-semibold text-purple-400 uppercase tracking-wider mb-1">
            Signal C: LLM Evidence
          </div>
          <div className="text-2xl font-extrabold text-white">{llmScore}%</div>
          <p className="text-[11px] text-slate-400 mt-1">Structured evidence extraction</p>
        </div>

        {/* Final Fused Score */}
        <div className="bg-gradient-nexus p-4 rounded-xl text-white shadow-lg shadow-indigo-500/25">
          <div className="text-xs font-semibold text-indigo-200 uppercase tracking-wider mb-1">
            Final Fused Hybrid Match
          </div>
          <div className="text-3xl font-black">{finalScore}%</div>
          <p className="text-[11px] text-indigo-100 mt-1">Diff: {difference.toFixed(1)}%</p>
        </div>

      </div>

      {/* Reconciliation Notes */}
      {reconciliationNotes && (
        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs text-slate-300 flex items-start space-x-2">
          <Scale className="w-4 h-4 text-indigo-400 mt-0.5 flex-shrink-0" />
          <div>
            <span className="font-bold text-white">Reconciliation Audit Trail: </span>
            {reconciliationNotes}
          </div>
        </div>
      )}

    </div>
  );
};
