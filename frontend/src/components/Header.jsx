import React from 'react';
import { Compass, Search, Bookmark, X, Globe2, Layers } from 'lucide-react';

export default function Header({
  searchQuery,
  onSearchChange,
  regions = [],
  categories = [],
  activeRegion,
  onSelectRegion,
  activeCategory,
  onSelectCategory,
  bookmarkCount = 0,
  onOpenBookmarks,
  onGoHome,
  filterMode,
  onFilterModeChange,
}) {
  const pills = filterMode === 'regions' ? regions : categories;
  const activeValue = filterMode === 'regions' ? activeRegion : activeCategory;
  const handleSelectPill = filterMode === 'regions' ? onSelectRegion : onSelectCategory;

  return (
    <header className="sticky top-0 z-40 bg-[#FAF9F6]/95 backdrop-blur-md border-b border-[#E5E7EB]">
      {/* Primary Editorial Masthead */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 sm:h-18 flex items-center justify-between gap-4">
        {/* Brand Logo */}
        <button
          type="button"
          onClick={onGoHome}
          className="flex items-center gap-2.5 text-left group cursor-pointer shrink-0"
        >
          <span className="w-9 h-9 rounded-xl bg-[#0D9488] text-white flex items-center justify-center shadow-xs group-hover:bg-[#0F766E] transition-colors">
            <Compass className="w-5 h-5" />
          </span>
          <div>
            <span className="font-editorial text-xl sm:text-2xl font-bold tracking-tight text-[#1C1917] block leading-none">
              World Tourist
            </span>
            <span className="text-[10px] uppercase tracking-[0.2em] text-[#57534E] font-medium hidden sm:block mt-0.5">
              Destinations &amp; Culture
            </span>
          </div>
        </button>

        {/* Search Input */}
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="w-4 h-4 text-[#57534E] absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="search"
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="Search destinations, countries, stories…"
              aria-label="Search stories"
              className="w-full pl-10 pr-9 py-2 rounded-full bg-white border border-[#E5E7EB] text-sm text-[#1C1917] placeholder:text-[#57534E]/70 focus:outline-none focus:border-[#0D9488] focus:ring-2 focus:ring-[#0D9488]/15 transition-all"
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => onSearchChange('')}
                aria-label="Clear search"
                className="absolute right-3 top-1/2 -translate-y-1/2 text-[#57534E] hover:text-[#1C1917] cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Saved Bookmarks Action */}
        <button
          type="button"
          onClick={onOpenBookmarks}
          className="inline-flex items-center gap-2 px-3.5 py-2 rounded-full bg-white border border-[#E5E7EB] text-sm font-medium text-[#1C1917] hover:border-[#0D9488] hover:text-[#0D9488] transition-colors shrink-0 cursor-pointer"
        >
          <Bookmark className="w-4 h-4 text-[#0D9488]" />
          <span className="hidden sm:inline">Saved</span>
          {bookmarkCount > 0 && (
            <span className="px-1.5 py-0.5 text-xs font-semibold rounded-full bg-[#0D9488] text-white leading-none">
              {bookmarkCount}
            </span>
          )}
        </button>
      </div>

      {/* Sticky Region / Category Pill Bar */}
      <div className="border-t border-[#E5E7EB]/80 bg-[#FAF9F6]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2.5 flex items-center gap-3">
          {/* Switcher between Regions & Categories */}
          <div className="inline-flex rounded-full bg-white border border-[#E5E7EB] p-0.5 shrink-0">
            <button
              type="button"
              onClick={() => onFilterModeChange('regions')}
              className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold transition-colors cursor-pointer ${
                filterMode === 'regions'
                  ? 'bg-[#1C1917] text-white'
                  : 'text-[#57534E] hover:text-[#1C1917]'
              }`}
            >
              <Globe2 className="w-3.5 h-3.5" />
              Regions
            </button>
            <button
              type="button"
              onClick={() => onFilterModeChange('categories')}
              className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold transition-colors cursor-pointer ${
                filterMode === 'categories'
                  ? 'bg-[#1C1917] text-white'
                  : 'text-[#57534E] hover:text-[#1C1917]'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              Categories
            </button>
          </div>

          {/* Horizontal Scrollable Pills */}
          <div className="flex items-center gap-2 overflow-x-auto pill-scrollbar py-0.5">
            <button
              type="button"
              onClick={() => handleSelectPill('All')}
              className={`px-3.5 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap border transition-colors cursor-pointer ${
                activeValue === 'All'
                  ? 'bg-[#0D9488] text-white border-[#0D9488]'
                  : 'bg-white text-[#57534E] border-[#E5E7EB] hover:border-[#0D9488]/60 hover:text-[#1C1917]'
              }`}
            >
              All {filterMode === 'regions' ? 'Regions' : 'Categories'}
            </button>

            {pills.map((item) => {
              const isSelected = activeValue === item;
              return (
                <button
                  key={item}
                  type="button"
                  onClick={() => handleSelectPill(item)}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap border transition-colors cursor-pointer ${
                    isSelected
                      ? 'bg-[#0D9488] text-white border-[#0D9488]'
                      : 'bg-white text-[#57534E] border-[#E5E7EB] hover:border-[#0D9488]/60 hover:text-[#1C1917]'
                  }`}
                >
                  {item}
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </header>
  );
}
