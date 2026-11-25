import React from 'react';
import { Compass, Sparkles, LayoutDashboard, Globe, BookOpen, Layers } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, publishedCount, dailyTarget = 200 }) {
  const percent = Math.min(100, Math.round(((publishedCount || 0) / dailyTarget) * 100));

  return (
    <header className="sticky top-0 z-40 bg-slate-900/90 backdrop-blur-md border-b border-slate-800 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div 
          className="flex items-center space-x-3 cursor-pointer group"
          onClick={() => setActiveTab('feed')}
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 via-teal-400 to-indigo-500 flex items-center justify-center shadow-lg shadow-teal-500/20 group-hover:scale-105 transition-transform">
            <Compass className="w-6 h-6 text-slate-950 stroke-[2.2]" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-300 bg-clip-text text-transparent">
                GlobeTrotter<span className="text-teal-400">.AI</span>
              </span>
              <span className="text-[10px] uppercase font-semibold px-1.5 py-0.5 rounded bg-teal-500/20 text-teal-300 border border-teal-500/30">
                NIM 3.5
              </span>
            </div>
            <p className="text-[11px] text-slate-400 hidden sm:block">Automated Global Tourism Publisher</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1 sm:space-x-2">
          <button
            onClick={() => setActiveTab('feed')}
            className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'feed'
                ? 'bg-teal-500/15 text-teal-300 border border-teal-500/30 shadow-sm'
                : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <BookOpen className="w-4 h-4" />
            <span>Travel Stories</span>
          </button>

          <button
            onClick={() => setActiveTab('dashboard')}
            className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'dashboard'
                ? 'bg-teal-500/15 text-teal-300 border border-teal-500/30 shadow-sm'
                : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <LayoutDashboard className="w-4 h-4" />
            <span>24/7 Autopilot Engine</span>
          </button>

          <button
            onClick={() => setActiveTab('trigger')}
            className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'trigger'
                ? 'bg-teal-500/15 text-teal-300 border border-teal-500/30 shadow-sm'
                : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <Sparkles className="w-4 h-4 text-amber-400" />
            <span className="hidden md:inline">Custom Creator</span>
          </button>
        </nav>

        {/* Daily Target Progress Pill */}
        <div className="hidden lg:flex items-center space-x-3 bg-slate-800/70 border border-slate-700/60 px-3.5 py-1.5 rounded-full">
          <Globe className="w-4 h-4 text-teal-400 animate-spin-slow" />
          <div className="text-xs">
            <span className="text-slate-400">Daily Target: </span>
            <span className="font-semibold text-emerald-300">{publishedCount || 0}</span>
            <span className="text-slate-500"> / {dailyTarget}</span>
          </div>
          <div className="w-16 bg-slate-700 h-1.5 rounded-full overflow-hidden">
            <div 
              className="bg-gradient-to-r from-teal-400 to-emerald-400 h-full rounded-full transition-all duration-500" 
              style={{ width: `${percent}%` }}
            />
          </div>
        </div>
      </div>
    </header>
  );
}
