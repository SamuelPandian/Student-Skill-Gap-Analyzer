import React from 'react';
import { 
  Compass, LayoutDashboard, FileText, Briefcase, 
  GitMerge, BarChart2, Award, Zap 
} from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  studentName: string;
  targetRole: string;
}

export const Navbar: React.FC<NavbarProps> = ({ 
  activeTab, 
  setActiveTab, 
  studentName,
  targetRole 
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Career Dashboard', icon: LayoutDashboard },
    { id: 'matching', label: 'Hybrid Job Matcher', icon: Briefcase },
    { id: 'learning-path', label: 'Learning Path (DAG)', icon: GitMerge },
    { id: 'resume', label: 'Resume & Competencies', icon: FileText },
    { id: 'careers', label: 'Alternative Careers', icon: Compass },
  ];

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80 px-6 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        
        {/* Brand Logo & Tagline */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
          <div className="w-10 h-10 rounded-xl bg-gradient-nexus p-0.5 flex items-center justify-center shadow-lg shadow-indigo-500/30">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Zap className="w-5 h-5 text-indigo-400 fill-indigo-400" />
            </div>
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              NEXUS <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-medium">Hybrid AI</span>
            </h1>
            <p className="text-[11px] text-slate-400 font-medium">Employability, eXpertise & Upskilling System</p>
          </div>
        </div>

        {/* Nav Links */}
        <nav className="hidden md:flex items-center space-x-1 bg-slate-900/60 p-1.5 rounded-xl border border-slate-800">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-gradient-nexus text-white shadow-md shadow-indigo-500/25'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Student Profile Quick View */}
        <div className="flex items-center space-x-3">
          <div className="text-right hidden sm:block">
            <div className="text-sm font-semibold text-white">{studentName}</div>
            <div className="text-xs text-indigo-400 font-medium">{targetRole}</div>
          </div>
          <div className="w-9 h-9 rounded-full bg-slate-800 border border-indigo-500/40 flex items-center justify-center text-sm font-bold text-indigo-300 shadow-inner">
            {studentName.charAt(0)}
          </div>
        </div>

      </div>
    </header>
  );
};
