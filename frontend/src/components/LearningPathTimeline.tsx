import React from 'react';
import { GitMerge, CheckCircle, PlayCircle, Lock, BookOpen, Clock, ExternalLink, Sparkles } from 'lucide-react';

export interface LearningStep {
  stepNumber: number;
  skillId: number;
  skillName: str;
  status: 'SATISFIED' | 'RECOMMENDED' | 'LOCKED_PREREQUISITE';
  currentLevel: number;
  requiredLevel: number;
  prerequisitesSatisfied: boolean;
  recommendedCourse?: {
    courseId: number;
    courseName: str;
    provider: str;
    durationHours: number;
    url?: str;
  };
}

interface LearningPathTimelineProps {
  steps: LearningStep[];
  onCompleteCourse?: (courseId: number, studentId: number) => void;
}

export const LearningPathTimeline: React.FC<LearningPathTimelineProps> = ({
  steps,
  onCompleteCourse
}) => {
  return (
    <div className="glass-panel rounded-2xl border border-slate-800 p-6 mb-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <GitMerge className="w-5 h-5 text-indigo-400" />
            Prerequisite-Aware Learning Path (DAG Sequence)
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Topologically sorted roadmap. Skills are unlocked only when prerequisite dependencies are satisfied.
          </p>
        </div>
        <span className="text-xs font-semibold px-3 py-1 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-500/30 flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" /> Continuous Recalculation Loop
        </span>
      </div>

      <div className="relative border-l-2 border-slate-800 ml-4 pl-6 space-y-6">
        {steps.map((step) => {
          const isSatisfied = step.status === 'SATISFIED';
          const isRecommended = step.status === 'RECOMMENDED';
          const isLocked = step.status === 'LOCKED_PREREQUISITE';

          return (
            <div key={step.stepNumber} className="relative group">
              
              {/* Timeline Icon Node */}
              <div className={`absolute -left-[35px] top-0 w-8 h-8 rounded-full border-2 flex items-center justify-center text-xs font-bold transition-all ${
                isSatisfied
                  ? 'bg-emerald-950 border-emerald-500 text-emerald-300 shadow-md shadow-emerald-500/20'
                  : isRecommended
                  ? 'bg-indigo-950 border-indigo-500 text-indigo-300 shadow-md shadow-indigo-500/30 ring-4 ring-indigo-500/10'
                  : 'bg-slate-900 border-slate-700 text-slate-500'
              }`}>
                {isSatisfied ? (
                  <CheckCircle className="w-4 h-4 text-emerald-400" />
                ) : isRecommended ? (
                  <PlayCircle className="w-4 h-4 text-indigo-400" />
                ) : (
                  <Lock className="w-3.5 h-3.5 text-slate-500" />
                )}
              </div>

              {/* Step Card */}
              <div className={`p-4 rounded-xl border transition-all ${
                isRecommended
                  ? 'bg-indigo-950/30 border-indigo-500/40 shadow-lg shadow-indigo-500/10'
                  : isSatisfied
                  ? 'bg-slate-900/40 border-slate-800/80 opacity-80'
                  : 'bg-slate-900/20 border-slate-800/40'
              }`}>
                
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                      Step {step.stepNumber}
                    </span>
                    <h3 className="text-base font-bold text-white">{step.skillName}</h3>
                  </div>

                  <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${
                    isSatisfied
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                      : isRecommended
                      ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 animate-pulse'
                      : 'bg-slate-800 text-slate-400'
                  }`}>
                    {isSatisfied ? 'Satisfied' : isRecommended ? '▶ Active Priority' : 'Locked Prerequisite'}
                  </span>
                </div>

                <div className="text-xs text-slate-400 mb-3">
                  Target Level: {step.requiredLevel}/5 | Current: {step.currentLevel}/5
                </div>

                {/* Recommended Course Box */}
                {step.recommendedCourse && (
                  <div className="mt-3 p-3 rounded-lg bg-slate-900/90 border border-slate-800 flex items-center justify-between">
                    <div className="flex items-start space-x-3">
                      <BookOpen className="w-5 h-5 text-indigo-400 mt-0.5" />
                      <div>
                        <div className="text-xs font-bold text-slate-200">
                          {step.recommendedCourse.courseName}
                        </div>
                        <div className="text-[11px] text-slate-400 flex items-center space-x-2 mt-0.5">
                          <span>Provider: {step.recommendedCourse.provider}</span>
                          <span>•</span>
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3 text-slate-400" />
                            {step.recommendedCourse.durationHours} hrs
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      {step.recommendedCourse.url && (
                        <a
                          href={step.recommendedCourse.url}
                          target="_blank"
                          rel="noreferrer"
                          className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white"
                          title="Open Course"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                        </a>
                      )}

                      {isRecommended && onCompleteCourse && (
                        <button
                          onClick={() => onCompleteCourse(step.recommendedCourse!.courseId, 101)}
                          className="text-xs bg-emerald-600 hover:bg-emerald-500 text-white font-medium px-3 py-1.5 rounded-lg shadow-md shadow-emerald-600/30 transition-all"
                        >
                          Mark Completed
                        </button>
                      )}
                    </div>
                  </div>
                )}

              </div>

            </div>
          );
        })}
      </div>
    </div>
  );
};
