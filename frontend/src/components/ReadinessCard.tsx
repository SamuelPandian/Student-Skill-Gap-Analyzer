import React from 'react';
import { Target, Clock, Award, ShieldCheck, ArrowUpRight, TrendingUp } from 'lucide-react';

interface ReadinessCardProps {
  targetRole: string;
  readinessScore: number;  // 72%
  jobMatchScore: number;   // 81%
  estimatedWeeksRange: string; // "6–9 weeks"
  mandatorySatisfied: boolean;
  weightedScore?: number;
  validationStatus?: string;
}

export const ReadinessCard: React.FC<ReadinessCardProps> = ({
  targetRole,
  readinessScore,
  jobMatchScore,
  estimatedWeeksRange,
  mandatorySatisfied,
  weightedScore = 79,
  validationStatus = 'Reconciled'
}) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      
      {/* 1. Target Role & Overall Readiness */}
      <div className="glass-card-interactive p-5 rounded-2xl border border-indigo-500/20 relative overflow-hidden group">
        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
          <Target className="w-24 h-24 text-indigo-400" />
        </div>
        <div className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-indigo-400 mb-2">
          <Target className="w-4 h-4" />
          <span>Target Role</span>
        </div>
        <div className="text-xl font-bold text-white mb-3 truncate">{targetRole}</div>
        <div className="flex items-baseline space-x-2">
          <span className="text-3xl font-extrabold text-white">{readinessScore}%</span>
          <span className={`text-xs font-medium flex items-center ${readinessScore >= 60 ? 'text-emerald-400' : 'text-rose-400'}`}>
            <TrendingUp className="w-3.5 h-3.5 mr-0.5" /> {readinessScore >= 60 ? '+4% this week' : 'Gap detected'}
          </span>
        </div>
        <div className="w-full bg-slate-800 h-2 rounded-full mt-3 overflow-hidden">
          <div 
            className="bg-gradient-nexus h-full rounded-full transition-all duration-1000 ease-out" 
            style={{ width: `${Math.max(readinessScore, 5)}%` }}
          />
        </div>
        <p className="text-[11px] text-slate-400 mt-2">Overall Career Readiness Index</p>
      </div>

      {/* 2. Job Match Score */}
      <div className="glass-card-interactive p-5 rounded-2xl border border-purple-500/20 relative overflow-hidden group">
        <div className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-purple-400 mb-2">
          <Award className="w-4 h-4" />
          <span>Hybrid Job Match</span>
        </div>
        <div className="text-3xl font-extrabold text-purple-200 mb-1">{jobMatchScore}%</div>
        <div className="text-xs font-medium text-slate-300 mb-3">Backend Developer @ Nexus AI Labs</div>
        <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
          <div 
            className="bg-gradient-to-r from-indigo-500 to-purple-500 h-full rounded-full transition-all duration-1000 ease-out" 
            style={{ width: `${Math.max(jobMatchScore, 5)}%` }}
          />
        </div>
        <div className="mt-3 flex items-center justify-between text-[11px] text-slate-400">
          <span>Weighted baseline: {weightedScore}%</span>
          <span className="text-purple-300 font-medium">{validationStatus}</span>
        </div>
      </div>

      {/* 3. Estimated Time-to-Readiness Range */}
      <div className="glass-card-interactive p-5 rounded-2xl border border-cyan-500/20 relative overflow-hidden group">
        <div className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-cyan-400 mb-2">
          <Clock className="w-4 h-4" />
          <span>Estimated Readiness</span>
        </div>
        <div className="text-2xl font-extrabold text-cyan-100 mb-1">{estimatedWeeksRange}</div>
        <p className="text-xs text-slate-300 mb-3">Based on 10 study hrs/week & prerequisite depth</p>
        <div className="inline-flex items-center text-[11px] font-medium text-cyan-300 bg-cyan-950/60 px-2.5 py-1 rounded-md border border-cyan-500/30">
          Adaptive ML Range Forecast
        </div>
      </div>

      {/* 4. Mandatory Skills Status */}
      <div className={`glass-card-interactive p-5 rounded-2xl border relative overflow-hidden group ${
        mandatorySatisfied ? 'border-emerald-500/20' : 'border-rose-500/30 bg-rose-950/10'
      }`}>
        <div className={`flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider mb-2 ${
          mandatorySatisfied ? 'text-emerald-400' : 'text-rose-400'
        }`}>
          <ShieldCheck className="w-4 h-4" />
          <span>Mandatory Requirements</span>
        </div>
        <div className="flex items-center space-x-2 mb-2">
          <div className={`w-3 h-3 rounded-full ${
            mandatorySatisfied 
              ? 'bg-emerald-400 shadow-lg shadow-emerald-500/50 animate-pulse' 
              : 'bg-rose-500 shadow-lg shadow-rose-500/50 animate-pulse'
          }`} />
          <span className={`text-lg font-bold ${mandatorySatisfied ? 'text-white' : 'text-rose-200'}`}>
            {mandatorySatisfied ? 'All Satisfied' : 'Dealbreaker Missing'}
          </span>
        </div>
        <p className="text-xs text-slate-400 mb-3">
          {mandatorySatisfied 
            ? 'Python (5/5) & SQL (4/4) core requirements verified.' 
            : 'SQL (4/4) core requirement missing from parsed resume.'}
        </p>
        <div className={`text-[11px] px-2.5 py-1 rounded-md border inline-block ${
          mandatorySatisfied 
            ? 'text-emerald-300 bg-emerald-950/50 border-emerald-500/30' 
            : 'text-rose-300 bg-rose-950/50 border-rose-500/30'
        }`}>
          {mandatorySatisfied ? 'Zero Dealbreaker Penalty' : '50% Gate Penalty Applied'}
        </div>
      </div>

    </div>
  );
};
