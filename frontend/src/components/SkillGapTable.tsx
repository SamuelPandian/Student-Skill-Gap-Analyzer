import React from 'react';
import { AlertCircle, CheckCircle2, Flame, ArrowUpRight } from 'lucide-react';

export interface SkillGapItem {
  skillId: number;
  skillName: str;
  category: str;
  requiredLevel: number; // e.g. 5
  currentLevel: number;  // e.g. 4
  weightPercent: number; // e.g. 30
  isMandatory: boolean;
  nextPriorityReason?: str;
}

interface SkillGapTableProps {
  skills: SkillGapItem[];
  onSelectSkillForLearning?: (skillId: number) => void;
}

export const SkillGapTable: React.FC<SkillGapTableProps> = ({ skills, onSelectSkillForLearning }) => {
  return (
    <div className="glass-panel rounded-2xl border border-slate-800 p-6 mb-6">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            Skill Gap & Proficiency Matrix
            <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 font-normal">
              Target Job Requirement Weights = 100%
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Quantified distance between candidate competency state and target role expectations.
          </p>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-800 text-xs font-semibold text-slate-400 uppercase tracking-wider">
              <th className="pb-3 px-3">Skill Competency</th>
              <th className="pb-3 px-3 text-center">Required Level</th>
              <th className="pb-3 px-3 text-center">Current Level</th>
              <th className="pb-3 px-3 text-center">Proficiency Gap</th>
              <th className="pb-3 px-3 text-center">Weight</th>
              <th className="pb-3 px-3">Proficiency Progress</th>
              <th className="pb-3 px-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-sm">
            {skills.map((item) => {
              const gap = Math.max(item.requiredLevel - item.currentLevel, 0);
              const percent = Math.min((item.currentLevel / item.requiredLevel) * 100, 100);
              const isSatisfied = gap === 0;

              return (
                <tr key={item.skillId} className="hover:bg-slate-900/40 transition-colors">
                  
                  {/* Skill Name & Mandatory Badge */}
                  <td className="py-4 px-3">
                    <div className="font-semibold text-white flex items-center space-x-2">
                      <span>{item.skillName}</span>
                      {item.isMandatory && (
                        <span className="text-[10px] bg-rose-500/20 text-rose-300 border border-rose-500/30 px-1.5 py-0.5 rounded font-medium">
                          Core Mandatory
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-slate-400">{item.category}</div>
                  </td>

                  {/* Required Level */}
                  <td className="py-4 px-3 text-center font-semibold text-slate-300">
                    {item.requiredLevel} / 5
                  </td>

                  {/* Current Level */}
                  <td className="py-4 px-3 text-center">
                    <span className={`font-bold ${isSatisfied ? 'text-emerald-400' : item.currentLevel > 0 ? 'text-indigo-300' : 'text-amber-400'}`}>
                      {item.currentLevel} / 5
                    </span>
                  </td>

                  {/* Gap */}
                  <td className="py-4 px-3 text-center">
                    {isSatisfied ? (
                      <span className="inline-flex items-center text-xs font-semibold text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-500/30">
                        <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Satisfied
                      </span>
                    ) : (
                      <span className="inline-flex items-center text-xs font-semibold text-amber-400 bg-amber-950/60 px-2 py-0.5 rounded border border-amber-500/30">
                        <AlertCircle className="w-3.5 h-3.5 mr-1" /> -{gap.toFixed(1)} Gap
                      </span>
                    )}
                  </td>

                  {/* Importance Weight */}
                  <td className="py-4 px-3 text-center font-medium text-slate-300">
                    {item.weightPercent}%
                  </td>

                  {/* Progress Bar */}
                  <td className="py-4 px-3 w-44">
                    <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          isSatisfied 
                            ? 'bg-emerald-500' 
                            : percent > 40 
                            ? 'bg-gradient-nexus' 
                            : 'bg-amber-500'
                        }`}
                        style={{ width: `${percent}%` }}
                      />
                    </div>
                    <div className="text-[11px] text-slate-400 mt-1 flex justify-between">
                      <span>{percent.toFixed(0)}% fulfilled</span>
                      {item.nextPriorityReason && (
                        <span className="text-indigo-400 font-medium flex items-center gap-0.5">
                          <Flame className="w-3 h-3 text-amber-400" /> High Priority
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Action */}
                  <td className="py-4 px-3 text-right">
                    {!isSatisfied && (
                      <button
                        onClick={() => onSelectSkillForLearning && onSelectSkillForLearning(item.skillId)}
                        className="text-xs bg-indigo-600/30 hover:bg-indigo-600 text-indigo-200 hover:text-white px-3 py-1.5 rounded-lg border border-indigo-500/30 transition-all flex items-center space-x-1 ml-auto"
                      >
                        <span>Upskill</span>
                        <ArrowUpRight className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </td>

                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
