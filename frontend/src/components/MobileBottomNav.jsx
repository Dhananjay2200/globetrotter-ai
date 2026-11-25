import React from 'react';
import { Compass, SlidersHorizontal, Bookmark, Shield, Sparkles } from 'lucide-react';

export default function MobileBottomNav({ 
  onScrollToTop, 
  onOpenFilter, 
  savedCount = 0, 
  onOpenBookmarks, 
  onSwitchToAdmin 
}) {
  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-slate-950/95 backdrop-blur-lg border-t border-slate-800/90 px-3 py-2">
      <div className="flex items-center justify-around max-w-md mx-auto">
        {/* Stories Feed */}
        <button
          onClick={onScrollToTop}
          className="flex flex-col items-center justify-center p-1.5 text-slate-400 hover:text-teal-300 transition-colors"
        >
          <Compass className="w-5 h-5 text-teal-400" />
          <span className="text-[10px] font-medium mt-1">Stories</span>
        </button>

        {/* Filter & Regions */}
        <button
          onClick={onOpenFilter}
          className="flex flex-col items-center justify-center p-1.5 text-slate-400 hover:text-teal-300 transition-colors"
        >
          <SlidersHorizontal className="w-5 h-5 text-slate-300" />
          <span className="text-[10px] font-medium mt-1">Filter</span>
        </button>

        {/* Bookmarks */}
        <button
          onClick={onOpenBookmarks}
          className="relative flex flex-col items-center justify-center p-1.5 text-slate-400 hover:text-teal-300 transition-colors"
        >
          <Bookmark className="w-5 h-5 text-teal-400" />
          <span className="text-[10px] font-medium mt-1">Saved</span>
          {savedCount > 0 && (
            <span className="absolute top-1 right-2 w-4 h-4 bg-teal-500 text-slate-950 text-[9px] font-black rounded-full flex items-center justify-center">
              {savedCount}
            </span>
          )}
        </button>

        {/* Admin Switch */}
        <button
          onClick={onSwitchToAdmin}
          className="flex flex-col items-center justify-center p-1.5 text-slate-400 hover:text-amber-300 transition-colors"
        >
          <Shield className="w-5 h-5 text-amber-400" />
          <span className="text-[10px] font-medium mt-1">Admin</span>
        </button>
      </div>
    </nav>
  );
}
