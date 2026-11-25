import React from 'react';
import { 
  ShieldCheck, LayoutDashboard, FileText, Sparkles, 
  History, Eye, Activity, Zap, Compass, LogOut 
} from 'lucide-react';

export default function AdminNavbar({ 
  adminTab, 
  setAdminTab, 
  isAutopilotRunning, 
  publishedCount = 0,
  dailyTarget = 200,
  totalArticlesCount = 0,
  onExitToUserPortal,
  onLogout 
}) {
  return (
    <header className="sticky top-0 z-40 bg-slate-950 border-b border-slate-800 text-white shadow-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        
        {/* Admin Brand */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 via-orange-500 to-rose-500 flex items-center justify-center shadow-lg shadow-amber-500/20">
            <ShieldCheck className="w-6 h-6 text-slate-950 stroke-[2.2]" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg tracking-tight text-white">
                GlobeTrotter <span className="text-amber-400">Admin</span>
              </span>
              <span className="text-[10px] uppercase font-mono font-bold px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                Command Center
              </span>
            </div>
            <div className="flex flex-wrap items-center gap-x-2 gap-y-0.5 text-[11px] text-slate-400">
              <span className="flex items-center space-x-1">
                <span className={`w-2 h-2 rounded-full ${isAutopilotRunning ? 'bg-emerald-400 animate-pulse' : 'bg-slate-600'}`} />
                <span>{isAutopilotRunning ? 'Autopilot Active' : 'Autopilot Idle'}</span>
              </span>
              <span>•</span>
              <span className="text-teal-400 font-semibold" title="Articles published in the current 24-hour cycle (resets daily at 00:00 UTC)">
                {publishedCount}/{dailyTarget} Today
              </span>
              <span>•</span>
              <span className="text-amber-300 font-semibold" title="Total travel articles generated across all statuses">
                {totalArticlesCount} Total Articles
              </span>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="hidden md:flex items-center space-x-1">
          <button
            onClick={() => setAdminTab('overview')}
            className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-xs font-semibold transition-all ${
              adminTab === 'overview'
                ? 'bg-amber-500/15 text-amber-300 border border-amber-500/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <LayoutDashboard className="w-4 h-4" />
            <span>Autopilot & Telemetry</span>
          </button>

          <button
            onClick={() => setAdminTab('articles')}
            className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-xs font-semibold transition-all ${
              adminTab === 'articles'
                ? 'bg-amber-500/15 text-amber-300 border border-amber-500/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Articles Manager</span>
          </button>

          <button
            onClick={() => setAdminTab('trigger')}
            className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-xs font-semibold transition-all ${
              adminTab === 'trigger'
                ? 'bg-amber-500/15 text-amber-300 border border-amber-500/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <Sparkles className="w-4 h-4 text-amber-400" />
            <span>Custom Generator</span>
          </button>

          <button
            onClick={() => setAdminTab('jobs')}
            className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-xs font-semibold transition-all ${
              adminTab === 'jobs'
                ? 'bg-amber-500/15 text-amber-300 border border-amber-500/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <History className="w-4 h-4" />
            <span>Publishing Jobs</span>
          </button>
        </nav>

        {/* Actions */}
        <div className="flex items-center space-x-2">
          <button
            onClick={onExitToUserPortal}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-xl bg-teal-500/20 hover:bg-teal-500 text-teal-300 hover:text-slate-950 border border-teal-500/40 text-xs font-bold transition-all shadow-sm"
          >
            <Compass className="w-4 h-4" />
            <span className="hidden sm:inline">View Public Blog</span>
          </button>

          {onLogout && (
            <button
              onClick={onLogout}
              className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-rose-400 hover:border-rose-500/40 transition-colors"
              title="Log Out of Admin"
            >
              <LogOut className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Mobile Sub-Navigation Bar for Admin */}
      <div className="md:hidden flex items-center justify-around border-t border-slate-900 bg-slate-950 px-2 py-2 text-[11px] font-medium">
        <button
          onClick={() => setAdminTab('overview')}
          className={`p-1.5 ${adminTab === 'overview' ? 'text-amber-400 font-bold' : 'text-slate-400'}`}
        >
          Autopilot
        </button>
        <button
          onClick={() => setAdminTab('articles')}
          className={`p-1.5 ${adminTab === 'articles' ? 'text-amber-400 font-bold' : 'text-slate-400'}`}
        >
          Articles
        </button>
        <button
          onClick={() => setAdminTab('trigger')}
          className={`p-1.5 ${adminTab === 'trigger' ? 'text-amber-400 font-bold' : 'text-slate-400'}`}
        >
          Generator
        </button>
        <button
          onClick={() => setAdminTab('jobs')}
          className={`p-1.5 ${adminTab === 'jobs' ? 'text-amber-400 font-bold' : 'text-slate-400'}`}
        >
          Jobs
        </button>
      </div>
    </header>
  );
}
