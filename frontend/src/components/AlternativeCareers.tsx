import React from 'react';
import { Compass, Award, ArrowUpRight, CheckCircle } from 'lucide-react';

export interface AlternativeRole {
  roleTitle: str;
  matchScore: number; // e.g. 86
  statusTag: str;
  keyMatchingSkills: str[];
  gapSkills: str[];
}

export const AlternativeCareers: React.FC = () => {
  const roles: AlternativeRole[] = [
    {
      roleTitle: 'Data Analyst',
      matchScore: 86,
      statusTag: 'Highest Match',
      keyMatchingSkills: ['SQL (4/4)', 'Python (4/5)', 'Git (3/3)'],
      gapSkills: ['Tableau / PowerBI']
    },
    {
      roleTitle: 'Backend Developer',
      matchScore: 79,
      statusTag: 'Current Target Role',
      keyMatchingSkills: ['Python (4/5)', 'SQL (4/4)', 'REST API (3/3)', 'Git (3/3)'],
      gapSkills: ['Django (2/4)', 'Docker (0/2)']
    },
    {
      roleTitle: 'Data Engineer',
      matchScore: 74,
      statusTag: 'Adjacent Role',
      keyMatchingSkills: ['Python (4/5)', 'SQL (4/4)'],
      gapSkills: ['Apache Spark', 'Airflow', 'Docker (0/2)']
    },
    {
      roleTitle: 'Machine Learning Engineer',
      matchScore: 61,
      statusTag: 'Longer Runway',
      keyMatchingSkills: ['Python (4/5)'],
      gapSkills: ['PyTorch / TensorFlow', 'Mathematics / Linear Algebra', 'MLOps']
    }
  ];

  return (
    <div className="glass-panel rounded-2xl border border-slate-800 p-6 mb-6">
      
      <div className="flex items-center space-x-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center">
          <Compass className="w-5 h-5 text-cyan-400" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            Alternative Career Pathways & Suitability
            <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 font-normal">
              Skill Reuse Optimization
            </span>
          </h2>
          <p className="text-xs text-slate-400">
            Discovers high-match alternative roles based on candidate's existing normalized competency profile.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {roles.map((item, idx) => (
          <div key={idx} className="glass-card-interactive p-5 rounded-xl border border-slate-800 flex flex-col justify-between">
            
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-base font-bold text-white">{item.roleTitle}</h3>
                <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full ${
                  item.matchScore >= 80 
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    : item.matchScore >= 70
                    ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                    : 'bg-slate-800 text-slate-400'
                }`}>
                  {item.statusTag}
                </span>
              </div>

              <div className="flex items-baseline space-x-2 mb-3">
                <span className="text-3xl font-extrabold text-white">{item.matchScore}%</span>
                <span className="text-xs text-slate-400">Competency Match</span>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-slate-800 h-2 rounded-full mb-4 overflow-hidden">
                <div 
                  className={`h-full rounded-full transition-all duration-700 ${
                    item.matchScore >= 80 ? 'bg-emerald-500' : 'bg-gradient-nexus'
                  }`}
                  style={{ width: `${item.matchScore}%` }}
                />
              </div>

              {/* Skills matched */}
              <div className="space-y-1.5 mb-4">
                <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                  Satisfied Strengths:
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {item.keyMatchingSkills.map((sk, i) => (
                    <span key={i} className="text-xs bg-slate-800/80 text-emerald-300 px-2 py-0.5 rounded border border-slate-700 flex items-center gap-1">
                      <CheckCircle className="w-3 h-3 text-emerald-400" />
                      {sk}
                    </span>
                  ))}
                </div>
              </div>

              {/* Gaps */}
              <div className="space-y-1.5">
                <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                  Remaining Gaps:
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {item.gapSkills.map((gk, i) => (
                    <span key={i} className="text-xs bg-slate-900 text-amber-300 px-2 py-0.5 rounded border border-amber-500/20">
                      {gk}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <button className="mt-5 w-full py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-all flex items-center justify-center space-x-1">
              <span>Explore Roadmap</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>

          </div>
        ))}
      </div>

    </div>
  );
};
