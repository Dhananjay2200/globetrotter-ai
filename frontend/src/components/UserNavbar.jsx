import React, { useState } from 'react';
import { Compass, Search, Bookmark, SlidersHorizontal, Shield, X } from 'lucide-react';

export default function UserNavbar({ 
  searchQuery, 
  setSearchQuery, 
  savedCount = 0, 
  onOpenBookmarks, 
  onOpenFilter,
  onSwitchToAdmin 
}) {
  const [mobileSearchOpen, setMobileSearchOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 bg-slate-950/90 backdrop-blur-md border-b border-slate-800/80 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        
        {/* Brand */}
        <div className="flex items-center space-x-3 cursor-pointer group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-500 via-emerald-400 to-cyan-500 flex items-center justify-center shadow-lg shadow-teal-500/20 group-hover:scale-105 transition-transform">
            <Compass className="w-6 h-6 text-slate-950 stroke-[2.2]" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-teal-200 bg-clip-text text-transparent">
                GlobeTrotter<span className="text-teal-400">.</span>
              </span>
              <span className="text-[10px] tracking-wide uppercase font-bold px-2 py-0.5 rounded-full bg-slate-800 text-teal-300 border border-slate-700">
                Stories
              </span>
            </div>
            <p className="text-[11px] text-slate-400 hidden sm:block">Worldwide Travel & Destination Guides</p>
          </div>
        </div>

        {/* Desktop Search Bar */}
        <div className="hidden md:flex flex-1 max-w-md mx-4">
          <div className="relative w-full">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search destinations, countries, or guides..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-900/90 border border-slate-700/80 rounded-xl pl-10 pr-9 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500 transition-all"
            />
            {searchQuery && (
              <button 
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          {/* Mobile Search Toggle */}
          <button
            onClick={() => setMobileSearchOpen(!mobileSearchOpen)}
            className="md:hidden p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white"
            aria-label="Toggle Search"
          >
            <Search className="w-4 h-4" />
          </button>

          {/* Mobile Filter Button */}
          <button
            onClick={onOpenFilter}
            className="md:hidden p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-teal-300"
            aria-label="Open Filters"
          >
            <SlidersHorizontal className="w-4 h-4" />
          </button>

          {/* Bookmarks Counter Button */}
          <button
            onClick={onOpenBookmarks}
            className="relative flex items-center space-x-2 px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-white transition-all text-xs font-medium"
            title="Saved Stories"
          >
            <Bookmark className="w-4 h-4 text-teal-400" />
            <span className="hidden sm:inline">Saved</span>
            {savedCount > 0 && (
              <span className="bg-teal-500 text-slate-950 text-[10px] font-black px-1.5 py-0.2 rounded-full">
                {savedCount}
              </span>
            )}
          </button>

          {/* Switch to Admin Mode Button */}
          <button
            onClick={onSwitchToAdmin}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-700/60 text-slate-300 hover:text-teal-300 text-xs font-medium transition-all"
            title="Open Admin Control Center"
          >
            <Shield className="w-3.5 h-3.5 text-amber-400" />
            <span className="hidden sm:inline">Admin</span>
          </button>
        </div>
      </div>

      {/* Expandable Mobile Search Bar */}
      {mobileSearchOpen && (
        <div className="md:hidden px-4 pb-3 pt-1 border-t border-slate-900 bg-slate-950">
          <div className="relative w-full">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              autoFocus
              placeholder="Search destinations, countries, or guides..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl pl-10 pr-9 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-teal-500"
            />
            {searchQuery && (
              <button 
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
