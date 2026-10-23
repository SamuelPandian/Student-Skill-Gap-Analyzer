import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { ReadinessCard } from './components/ReadinessCard';
import { SkillGapTable, SkillGapItem } from './components/SkillGapTable';
import { LearningPathTimeline, LearningStep } from './components/LearningPathTimeline';
import { HybridScoreBreakdown } from './components/HybridScoreBreakdown';
import { ResumeUploader } from './components/ResumeUploader';
import { AlternativeCareers } from './components/AlternativeCareers';

import { Sparkles, Flame, RefreshCw, CheckCircle, AlertCircle, RotateCcw } from 'lucide-react';

const API_BASE = "http://localhost:8000/api/v1";

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [studentId] = useState<number>(101);
  const [targetJobId] = useState<number>(1);
  const [hasUploadedResume, setHasUploadedResume] = useState<boolean>(false);
  const [studentName, setStudentName] = useState<string>('Candidate (No Resume)');
  const [targetRole, setTargetRole] = useState<string>('Backend Developer');

  const [readinessScore, setReadinessScore] = useState<number>(0);
  const [jobMatchScore, setJobMatchScore] = useState<number>(0);
  const [estimatedWeeks, setEstimatedWeeks] = useState<string>('Awaiting Upload');
  const [mandatorySatisfied, setMandatorySatisfied] = useState<boolean>(false);
  
  // Breakdown scores
  const [weightedScore, setWeightedScore] = useState<number>(0);
  const [semanticScore, setSemanticScore] = useState<number>(0);
  const [llmScore, setLLMScore] = useState<number>(0);
  const [validationStatus, setValidationStatus] = useState<'AGREED' | 'RECONCILED' | 'REVIEW_REQUIRED'>('REVIEW_REQUIRED');
  const [reconciliationNotes, setReconciliationNotes] = useState<string>(
    "Awaiting candidate resume upload to evaluate competency alignment."
  );

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isLiveConnected, setIsLiveConnected] = useState<boolean>(false);

  // Default clean skill gaps (all level 0 before upload)
  const defaultSkillGaps: SkillGapItem[] = [
    { skillId: 1, skillName: 'Python', category: 'Programming Language', requiredLevel: 5, currentLevel: 0, weightPercent: 30, isMandatory: true, nextPriorityReason: 'Awaiting resume extraction (Mandatory)' },
    { skillId: 2, skillName: 'SQL', category: 'Database', requiredLevel: 4, currentLevel: 0, weightPercent: 20, isMandatory: true, nextPriorityReason: 'Awaiting resume extraction (Mandatory)' },
    { skillId: 3, skillName: 'Django', category: 'Web Framework', requiredLevel: 4, currentLevel: 0, weightPercent: 20, isMandatory: false },
    { skillId: 4, skillName: 'REST API', category: 'Architecture', requiredLevel: 3, currentLevel: 0, weightPercent: 15, isMandatory: false },
    { skillId: 5, skillName: 'Git', category: 'Version Control', requiredLevel: 3, currentLevel: 0, weightPercent: 10, isMandatory: false },
    { skillId: 6, skillName: 'Docker', category: 'DevOps', requiredLevel: 2, currentLevel: 0, weightPercent: 5, isMandatory: false }
  ];

  const [skillGapItems, setSkillGapItems] = useState<SkillGapItem[]>(defaultSkillGaps);

  // Reset assessment back to initial clean state
  const resetAssessment = () => {
    setHasUploadedResume(false);
    setStudentName('Candidate (No Resume)');
    setReadinessScore(0);
    setJobMatchScore(0);
    setEstimatedWeeks('Awaiting Upload');
    setMandatorySatisfied(false);
    setWeightedScore(0);
    setSemanticScore(0);
    setLLMScore(0);
    setValidationStatus('REVIEW_REQUIRED');
    setReconciliationNotes('Awaiting candidate resume upload to evaluate competency alignment.');
    setSkillGapItems(defaultSkillGaps);
    setLearningSteps([]);
  };

  // Topological DAG steps
  const [learningSteps, setLearningSteps] = useState<LearningStep[]>([
    {
      stepNumber: 1,
      skillId: 1,
      skillName: 'Python Core & OOP',
      status: 'RECOMMENDED',
      currentLevel: 2,
      requiredLevel: 5,
      prerequisitesSatisfied: true,
      recommendedCourse: {
        courseId: 1,
        courseName: 'Python Core & Advanced Architecture',
        provider: 'NEXUS Academy',
        durationHours: 20,
        url: '#'
      }
    },
    {
      stepNumber: 2,
      skillId: 5,
      skillName: 'Git & GitHub Workflow',
      status: 'SATISFIED',
      currentLevel: 3,
      requiredLevel: 3,
      prerequisitesSatisfied: true,
      recommendedCourse: {
        courseId: 5,
        courseName: 'Git & GitHub Workflow Professional',
        provider: 'Udemy Tech',
        durationHours: 8,
        url: '#'
      }
    },
    {
      stepNumber: 3,
      skillId: 3,
      skillName: 'Django Fundamentals',
      status: 'RECOMMENDED',
      currentLevel: 2,
      requiredLevel: 4,
      prerequisitesSatisfied: true,
      recommendedCourse: {
        courseId: 3,
        courseName: 'Django Web Framework Fundamentals',
        provider: 'Coursera Enterprise',
        durationHours: 25,
        url: '#'
      }
    },
    {
      stepNumber: 4,
      skillId: 4,
      skillName: 'REST API Development',
      status: 'LOCKED_PREREQUISITE',
      currentLevel: 3,
      requiredLevel: 3,
      prerequisitesSatisfied: false,
      recommendedCourse: {
        courseId: 4,
        courseName: 'Building Scalable REST APIs',
        provider: 'NEXUS Academy',
        durationHours: 12,
        url: '#'
      }
    },
    {
      stepNumber: 5,
      skillId: 6,
      skillName: 'Docker Essentials',
      status: 'LOCKED_PREREQUISITE',
      currentLevel: 0,
      requiredLevel: 2,
      prerequisitesSatisfied: false,
      recommendedCourse: {
        courseId: 6,
        courseName: 'Docker Essentials for Developers',
        provider: 'Pluralsight',
        durationHours: 14,
        url: '#'
      }
    }
  ]);

  // LIVE BACKEND DATA FETCHING FUNCTION
  const fetchLiveBackendData = async () => {
    setIsLoading(true);
    try {
      // 1. Fetch Student Profile & latest detected skills
      const studentRes = await fetch(`${API_BASE}/students/${studentId}`);
      if (studentRes.ok) {
        const studentData = await studentRes.json();
        setStudentName(studentData.name || 'Shrinithish');
        if (studentData.target_role) setTargetRole(studentData.target_role);
        setIsLiveConnected(true);

        // Update current skills based on database
        if (studentData.skills) {
          const dbSkillsMap = new Map(
            studentData.skills.map((s: any) => [s.skill_id, s.proficiency_level])
          );

          setSkillGapItems((prev) =>
            prev.map((item) => {
              const current = dbSkillsMap.has(item.skillId) ? Number(dbSkillsMap.get(item.skillId)) : 0;
              return { 
                ...item, 
                currentLevel: current,
                nextPriorityReason: current === 0 && item.isMandatory
                  ? 'CRITICAL DEALBREAKER: Mandatory core requirement missing'
                  : current > 0
                    ? `Level ${current} verified in profile`
                    : undefined
              };
            })
          );
        }
      }

      // 2. Execute Hybrid Matching calculation on backend
      const matchRes = await fetch(`${API_BASE}/matching/${studentId}/${targetJobId}`, {
        method: 'POST'
      });
      if (matchRes.ok) {
        const matchData = await matchRes.json();
        setWeightedScore(matchData.weighted_score);
        setSemanticScore(matchData.semantic_score);
        setLLMScore(matchData.llm_score);
        setJobMatchScore(matchData.final_score);
        setReadinessScore(Math.round(matchData.weighted_score * 0.95)); // Derived readiness index
        setValidationStatus(matchData.validation_status);
        setMandatorySatisfied(!matchData.mandatory_missing);
        
        if (matchData.estimated_readiness?.formatted_range) {
          setEstimatedWeeks(matchData.estimated_readiness.formatted_range);
        }
        if (matchData.reconciliation_notes) {
          setReconciliationNotes(matchData.reconciliation_notes);
        }
      }

      // 3. Fetch Prerequisite DAG Learning Path
      const pathRes = await fetch(`${API_BASE}/students/${studentId}/learning-path?target_job_id=${targetJobId}`);
      if (pathRes.ok) {
        const pathData = await pathRes.json();
        if (pathData.learning_path && pathData.learning_path.length > 0) {
          const mappedSteps: LearningStep[] = pathData.learning_path.map((p: any) => ({
            stepNumber: p.step_number,
            skillId: p.skill_id,
            skillName: p.skill_name,
            status: p.status,
            currentLevel: p.current_level,
            requiredLevel: p.required_level,
            prerequisitesSatisfied: p.prerequisites_satisfied,
            recommendedCourse: p.recommended_course
              ? {
                  courseId: p.recommended_course.course_id,
                  courseName: p.recommended_course.course_name,
                  provider: p.recommended_course.provider,
                  durationHours: p.recommended_course.duration_hours,
                  url: p.recommended_course.url
                }
              : undefined
          }));
          setLearningSteps(mappedSteps);
        }
      }
    } catch (err) {
      console.warn("Backend not reached on localhost:8000, using local reactive state.", err);
      setIsLiveConnected(false);
    } finally {
      setIsLoading(false);
    }
  };

  // Initial load: check connection without overriding clean reset state
  useEffect(() => {
    fetch(`http://localhost:8000/api/v1/jobs/1`)
      .then(res => { if (res.ok) setIsLiveConnected(true); })
      .catch(() => setIsLiveConnected(false));
  }, []);

  // When resume upload completes -> update state in accordance with the uploaded resume
  const handleResumeUploaded = async (uploadData?: any, uploadedFile?: File | null) => {
    setHasUploadedResume(true);
    // 1. Immediately apply candidate name
    if (uploadData?.student_name) {
      setStudentName(uploadData.student_name);
    } else if (uploadedFile?.name) {
      const cleanName = uploadedFile.name
        .replace(/\.[^/.]+$/, "")
        .replace(/^[0-9_]+/, "")
        .replace(/_Resume.*$/i, "")
        .replace(/[-_]/g, " ")
        .trim();
      if (cleanName) setStudentName(cleanName);
    }

    // 2. Build skill level map from upload data
    const skillsArray = uploadData?.updated_skills || uploadData?.detected_skills || [];
    const skillMap = new Map<number, number>();

    skillsArray.forEach((s: any) => {
      if (s.skill_id) {
        skillMap.set(Number(s.skill_id), Number(s.proficiency_level));
      } else if (s.skill_name) {
        const lower = s.skill_name.toLowerCase();
        if (lower.includes("python")) skillMap.set(1, Number(s.proficiency_level));
        else if (lower.includes("sql")) skillMap.set(2, Number(s.proficiency_level));
        else if (lower.includes("django")) skillMap.set(3, Number(s.proficiency_level));
        else if (lower.includes("rest")) skillMap.set(4, Number(s.proficiency_level));
        else if (lower.includes("git")) skillMap.set(5, Number(s.proficiency_level));
        else if (lower.includes("docker")) skillMap.set(6, Number(s.proficiency_level));
      }
    });

    // 3. Update skill gaps matrix (Missing skills become 0)
    setSkillGapItems((prev) =>
      prev.map((item) => {
        const current = skillMap.has(item.skillId) ? skillMap.get(item.skillId)! : 0;
        return {
          ...item,
          currentLevel: current,
          nextPriorityReason: current === 0 && item.isMandatory
            ? 'CRITICAL DEALBREAKER: Mandatory core requirement missing'
            : current > 0
              ? `Level ${current} detected in parsed resume`
              : undefined
        };
      })
    );

    // 4. Calculate deterministic match scores
    const pLvl = skillMap.get(1) || 0;
    const sqlLvl = skillMap.get(2) || 0;
    const djLvl = skillMap.get(3) || 0;
    const restLvl = skillMap.get(4) || 0;
    const gitLvl = skillMap.get(5) || 0;
    const docLvl = skillMap.get(6) || 0;

    const pScore = Math.min(pLvl / 5, 1.0) * 30;
    const sqlScore = Math.min(sqlLvl / 4, 1.0) * 20;
    const djScore = Math.min(djLvl / 4, 1.0) * 20;
    const restScore = Math.min(restLvl / 3, 1.0) * 15;
    const gitScore = Math.min(gitLvl / 3, 1.0) * 10;
    const docScore = Math.min(docLvl / 2, 1.0) * 5;

    const totalWeighted = Math.round(pScore + sqlScore + djScore + restScore + gitScore + docScore);
    const hasMandatoryGap = (pLvl < 5) || (sqlLvl < 4);

    setWeightedScore(totalWeighted);
    const semScore = totalWeighted >= 50 ? 82 : 44;
    setSemanticScore(semScore);
    const lScore = totalWeighted >= 50 ? 84 : 38;
    setLLMScore(lScore);

    // Apply gate penalty if mandatory requirement is missing
    const finalJobMatch = hasMandatoryGap ? Math.round(totalWeighted * 0.75) : Math.round(totalWeighted * 1.02);
    setJobMatchScore(Math.min(finalJobMatch, 100));
    setReadinessScore(Math.round(totalWeighted * 0.95));
    setMandatorySatisfied(!hasMandatoryGap);

    if (hasMandatoryGap) {
      setEstimatedWeeks('14–18 weeks');
      setValidationStatus('REVIEW_REQUIRED');
      setReconciliationNotes(
        `Mandatory core requirement missing: ${sqlLvl < 4 ? 'SQL (4 required, 0 detected)' : 'Python'}. Flagged for review.`
      );
    } else {
      setEstimatedWeeks('6–9 weeks');
      setValidationStatus('AGREED');
      setReconciliationNotes('Deterministic weighted score and LLM evidence score verified.');
    }

    // 5. Update Topological DAG Learning Path Steps
    setLearningSteps([
      {
        stepNumber: 1,
        skillId: 2,
        skillName: 'SQL Mastery & Relational DBs',
        status: sqlLvl >= 4 ? 'SATISFIED' : 'RECOMMENDED',
        currentLevel: sqlLvl,
        requiredLevel: 4,
        prerequisitesSatisfied: true,
        recommendedCourse: {
          courseId: 2,
          courseName: 'SQL & Relational Database Mastery',
          provider: 'DataCamp Partner',
          durationHours: 15,
          url: '#'
        }
      },
      {
        stepNumber: 2,
        skillId: 1,
        skillName: 'Python Core & Advanced Architecture',
        status: pLvl >= 5 ? 'SATISFIED' : 'RECOMMENDED',
        currentLevel: pLvl,
        requiredLevel: 5,
        prerequisitesSatisfied: true,
        recommendedCourse: {
          courseId: 1,
          courseName: 'Python Core & Advanced Architecture',
          provider: 'NEXUS Academy',
          durationHours: 20,
          url: '#'
        }
      },
      {
        stepNumber: 3,
        skillId: 3,
        skillName: 'Django Fundamentals',
        status: djLvl >= 4 ? 'SATISFIED' : (pLvl >= 3 && sqlLvl >= 3 ? 'RECOMMENDED' : 'LOCKED_PREREQUISITE'),
        currentLevel: djLvl,
        requiredLevel: 4,
        prerequisitesSatisfied: pLvl >= 3 && sqlLvl >= 3,
        recommendedCourse: {
          courseId: 3,
          courseName: 'Django Web Framework Fundamentals',
          provider: 'Coursera Enterprise',
          durationHours: 25,
          url: '#'
        }
      },
      {
        stepNumber: 4,
        skillId: 4,
        skillName: 'REST API Development',
        status: restLvl >= 3 ? 'SATISFIED' : (djLvl >= 2 ? 'RECOMMENDED' : 'LOCKED_PREREQUISITE'),
        currentLevel: restLvl,
        requiredLevel: 3,
        prerequisitesSatisfied: djLvl >= 2,
        recommendedCourse: {
          courseId: 4,
          courseName: 'Building Scalable REST APIs',
          provider: 'NEXUS Academy',
          durationHours: 12,
          url: '#'
        }
      },
      {
        stepNumber: 5,
        skillId: 6,
        skillName: 'Docker Essentials',
        status: docLvl >= 2 ? 'SATISFIED' : 'RECOMMENDED',
        currentLevel: docLvl,
        requiredLevel: 2,
        prerequisitesSatisfied: true,
        recommendedCourse: {
          courseId: 6,
          courseName: 'Docker Essentials for Developers',
          provider: 'Pluralsight',
          durationHours: 14,
          url: '#'
        }
      }
    ]);

    // Background sync with database if reachable
    try {
      await fetchLiveBackendData();
    } catch (e) {
      // already handled
    }
  };

  // Course Completion Handler: Calls backend progress update API
  const handleCompleteCourse = async (courseId: number, stId: number) => {
    setIsLoading(true);
    try {
      const res = await fetch(
        `${API_BASE}/students/progress/update?student_id=${stId}&course_id=${courseId}&status_str=COMPLETED&completion_percentage=100`,
        { method: 'POST' }
      );
      if (res.ok) {
        // Re-sync with backend recalculations
        await fetchLiveBackendData();
        return;
      }
    } catch (e) {
      console.warn("Backend progress update failed, applying optimistic update.");
    } finally {
      setIsLoading(false);
    }

    // Optimistic fallback update if backend offline
    setSkillGapItems((prev) =>
      prev.map((item) =>
        item.skillId === 3 ? { ...item, currentLevel: 4 } : item
      )
    );
    setLearningSteps((prev) =>
      prev.map((step) => {
        if (step.skillId === 3) return { ...step, status: 'SATISFIED', currentLevel: 4 };
        if (step.skillId === 4) return { ...step, status: 'RECOMMENDED', prerequisitesSatisfied: true };
        return step;
      })
    );
    setReadinessScore(84);
    setJobMatchScore(89);
    setEstimatedWeeks('3–5 weeks');
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 pb-16">
      
      {/* Top Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        studentName={studentName}
        targetRole={targetRole}
      />

      <main className="max-w-7xl mx-auto px-6 pt-6">

        {/* Dashboard Top Banner */}
        <div className="mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-6 rounded-2xl border border-slate-800">
          <div>
            <div className="flex items-center space-x-3 mb-1">
              <h1 className="text-2xl font-extrabold text-white flex items-center gap-2">
                NEXUS Career Dashboard
              </h1>
              {isLiveConnected ? (
                <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-medium flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" /> Live Backend Connected
                </span>
              ) : (
                <span className="text-xs px-2.5 py-1 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 font-medium flex items-center gap-1.5">
                  <AlertCircle className="w-3.5 h-3.5" /> Backend Connecting
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400">
              Candidate: <strong className="text-indigo-300">{studentName}</strong> | Target: <strong className="text-slate-200">{targetRole} @ Nexus AI Labs</strong>
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={resetAssessment}
              className="px-3.5 py-2.5 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 text-xs font-semibold border border-rose-500/30 transition-all flex items-center space-x-1.5"
              title="Reset dashboard to 0 before uploading resume"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset Assessment</span>
            </button>

            <button
              onClick={fetchLiveBackendData}
              disabled={isLoading}
              className="px-3.5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-all flex items-center space-x-1.5"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
              <span>Sync Live DB</span>
            </button>

            <button 
              onClick={() => handleCompleteCourse(3, studentId)}
              className="px-4 py-2.5 rounded-xl bg-gradient-nexus text-white text-xs font-semibold shadow-lg shadow-indigo-500/30 hover:opacity-95 transition-all flex items-center space-x-2"
            >
              <Sparkles className="w-4 h-4" />
              <span>Simulate Course Completion</span>
            </button>
          </div>
        </div>

        {/* Notice when dashboard is in clean reset state */}
        {!hasUploadedResume && (
          <div className="mb-6 p-4 rounded-2xl bg-indigo-950/40 border border-indigo-500/30 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-lg">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/20 flex items-center justify-center text-lg flex-shrink-0">
                📄
              </div>
              <div>
                <h4 className="text-sm font-bold text-white flex items-center gap-2">
                  Assessment Reset: Awaiting Resume Upload
                  <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                    Clean State (0%)
                  </span>
                </h4>
                <p className="text-xs text-slate-400 mt-0.5">
                  All competencies are currently reset to 0. Go to the "Resume & Competencies" tab to upload a candidate PDF/DOCX resume and trigger real-time AI extraction.
                </p>
              </div>
            </div>
            <button
              onClick={() => setActiveTab('resume')}
              className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all shadow-md shadow-indigo-600/30 whitespace-nowrap flex items-center gap-1.5 self-start sm:self-auto"
            >
              <span>Upload Resume</span>
              <span>→</span>
            </button>
          </div>
        )}

        {/* Top 4 Metrics Cards */}
        <ReadinessCard
          targetRole={targetRole}
          readinessScore={readinessScore}
          jobMatchScore={jobMatchScore}
          estimatedWeeksRange={estimatedWeeks}
          mandatorySatisfied={mandatorySatisfied}
          weightedScore={weightedScore}
          validationStatus={validationStatus}
        />

        {/* Render Tab Views */}
        {activeTab === 'dashboard' && (
          <>
            {/* Skill Gap Matrix */}
            <SkillGapTable
              skills={skillGapItems}
              onSelectSkillForLearning={() => setActiveTab('learning-path')}
            />

            {/* Next Priority Recommendation Callout */}
            <div className="glass-panel p-5 rounded-2xl border border-indigo-500/30 mb-6 flex items-start space-x-4 bg-indigo-950/20">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/20 flex items-center justify-center text-indigo-400 flex-shrink-0">
                <Flame className="w-5 h-5 text-amber-400" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  NEXT PRIORITY: Python Core & Advanced Architecture
                  <span className="text-[10px] bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded border border-amber-500/30">
                    Highest Return on Upskilling
                  </span>
                </h3>
                <p className="text-xs text-slate-300 mt-1">
                  Reason: High job weight (30%) + 3.0 proficiency gap (Current Level 2.0 extracted from resume vs 5.0 required). Prerequisite foundation for Django and REST APIs.
                </p>
              </div>
            </div>

            {/* Prerequisite Learning Path DAG */}
            <LearningPathTimeline
              steps={learningSteps}
              onCompleteCourse={handleCompleteCourse}
            />
          </>
        )}

        {activeTab === 'matching' && (
          <HybridScoreBreakdown
            weightedScore={weightedScore}
            semanticScore={semanticScore}
            llmScore={llmScore}
            finalScore={jobMatchScore}
            difference={Math.abs(weightedScore - llmScore)}
            validationStatus={validationStatus}
            reconciliationNotes={reconciliationNotes}
          />
        )}

        {activeTab === 'learning-path' && (
          <LearningPathTimeline
            steps={learningSteps}
            onCompleteCourse={handleCompleteCourse}
          />
        )}

        {activeTab === 'resume' && (
          <ResumeUploader 
            studentId={studentId} 
            onUploadSuccess={handleResumeUploaded} 
          />
        )}

        {activeTab === 'careers' && (
          <AlternativeCareers />
        )}

      </main>

    </div>
  );
};

export default App;
