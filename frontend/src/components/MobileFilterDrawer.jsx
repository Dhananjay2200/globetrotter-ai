import React, { useRef } from 'react';
import { X, Check, Globe2, Layers, RotateCcw, Calendar } from 'lucide-react';

export default function MobileFilterDrawer({
  isOpen,
  onClose,
  regions = [],
  selectedRegion,
  onSelectRegion,
  categories = [],
  selectedCategory,
  onSelectCategory,
  dateFilters = [],
  selectedDateFilter = 'all',
  onSelectDateFilter,
  customDate = '',
  onSelectCustomDate,
  totalResults = 0,
  onResetFilters,
}) {
  const mobileDateRef = useRef(null);
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-950/80 backdrop-blur-md flex flex-col justify-end animate-fadeIn">
      <div className="bg-slate-900 border-t border-slate-800 rounded-t-3xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-teal-500/20 text-teal-400 flex items-center justify-center">
              <Globe2 className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Filter Travel Stories</h3>
              <p className="text-[11px] text-slate-400">{totalResults} guides available</p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={onResetFilters}
              className="p-2 text-xs text-slate-400 hover:text-teal-300 flex items-center space-x-1"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>
            <button
              onClick={onClose}
              className="p-2 rounded-full bg-slate-800 text-slate-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Filter Body */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
          {/* Global Regions */}
          <div>
            <h4 className="text-xs font-bold text-teal-400 uppercase tracking-wider mb-3 flex items-center space-x-1.5">
              <Globe2 className="w-3.5 h-3.5" />
              <span>Worldwide Regions</span>
            </h4>
            <div className="grid grid-cols-2 gap-2">
              {regions.map(reg => {
                const isSelected = selectedRegion === reg;
                return (
                  <button
                    key={reg}
                    onClick={() => onSelectRegion(reg)}
                    className={`p-2.5 rounded-xl text-left text-xs font-medium transition-all flex items-center justify-between ${
                      isSelected
                        ? 'bg-teal-500 text-slate-950 font-bold shadow-md shadow-teal-500/20'
                        : 'bg-slate-950/60 border border-slate-800 text-slate-300 hover:border-slate-700'
                    }`}
                  >
                    <span className="truncate pr-1">{reg}</span>
                    {isSelected && <Check className="w-3.5 h-3.5 flex-shrink-0" />}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Travel Categories */}
          <div>
            <h4 className="text-xs font-bold text-teal-400 uppercase tracking-wider mb-3 flex items-center space-x-1.5">
              <Layers className="w-3.5 h-3.5" />
              <span>Travel Themes & Categories</span>
            </h4>
            <div className="space-y-1.5">
              {categories.map(cat => {
                const isSelected = selectedCategory === cat;
                return (
                  <button
                    key={cat}
                    onClick={() => onSelectCategory(cat)}
                    className={`w-full p-2.5 rounded-xl text-left text-xs font-medium transition-all flex items-center justify-between ${
                      isSelected
                        ? 'bg-teal-500/20 border border-teal-500/40 text-teal-300 font-bold'
                        : 'bg-slate-950/60 border border-slate-800 text-slate-300 hover:border-slate-700'
                    }`}
                  >
                    <span className="truncate">{cat}</span>
                    {isSelected && <Check className="w-4 h-4 text-teal-400 flex-shrink-0" />}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Publication Date Filter */}
          {dateFilters.length > 0 && (
            <div>
              <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider mb-3 flex items-center space-x-1.5">
                <Calendar className="w-3.5 h-3.5" />
                <span>Publication Timeline</span>
              </h4>
              <div className="grid grid-cols-2 gap-2">
                {dateFilters.map(df => {
                  const isSelected = selectedDateFilter === df.id;
                  return (
                    <button
                      key={df.id}
                      onClick={() => onSelectDateFilter && onSelectDateFilter(df.id)}
                      className={`p-2.5 rounded-xl text-left text-xs font-medium transition-all flex items-center justify-between ${
                        isSelected
                          ? 'bg-amber-500/20 border border-amber-500/40 text-amber-300 font-bold'
                          : 'bg-slate-950/60 border border-slate-800 text-slate-300 hover:border-slate-700'
                      }`}
                    >
                      <span className="truncate pr-1">{df.label}</span>
                      {isSelected && <Check className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />}
                    </button>
                  );
                })}
              </div>

              {selectedDateFilter === 'custom' && (
                <div 
                  onClick={() => mobileDateRef.current?.showPicker?.()}
                  className="mt-2.5 p-2.5 rounded-xl bg-slate-950/90 border border-amber-500/60 flex items-center justify-between cursor-pointer hover:border-amber-400 transition-all shadow-md group"
                >
                  <div className="flex items-center space-x-2 text-xs text-slate-300">
                    <Calendar className="w-4 h-4 text-amber-400 group-hover:scale-110 transition-transform" />
                    <span>Choose Date:</span>
                  </div>
                  <input
                    ref={mobileDateRef}
                    type="date"
                    value={customDate}
                    onChange={(e) => onSelectCustomDate && onSelectCustomDate(e.target.value)}
                    onClick={(e) => {
                      e.stopPropagation();
                      e.target.showPicker?.();
                    }}
                    style={{ colorScheme: 'dark' }}
                    className="bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-amber-200 focus:outline-none cursor-pointer font-medium"
                  />
                </div>
              )}
            </div>
          )}
        </div>

        {/* Done Button */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/80">
          <button
            onClick={onClose}
            className="w-full py-3 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-sm shadow-lg shadow-teal-500/20 transition-all flex items-center justify-center space-x-2"
          >
            <span>Show {totalResults} Travel {totalResults === 1 ? 'Story' : 'Stories'}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
