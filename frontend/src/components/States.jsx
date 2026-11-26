import React from 'react';
import { AlertTriangle, RefreshCw, SearchX } from 'lucide-react';

export function HeroSkeleton() {
  return (
    <div className="w-full h-[380px] sm:h-[460px] rounded-2xl bg-[#E5E7EB]/60 animate-pulse border border-[#E5E7EB] overflow-hidden relative">
      <div className="absolute inset-x-0 bottom-0 p-6 sm:p-10 space-y-3">
        <div className="h-6 w-36 rounded-full bg-[#D6D3D1]" />
        <div className="h-9 sm:h-11 w-3/4 rounded-lg bg-[#D6D3D1]" />
        <div className="h-4 w-2/3 rounded bg-[#D6D3D1]" />
      </div>
    </div>
  );
}

export function GridSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
      <div className="md:col-span-7 bg-white border border-[#E5E7EB] rounded-2xl overflow-hidden animate-pulse">
        <div className="h-64 bg-[#E5E7EB]/70" />
        <div className="p-6 space-y-3">
          <div className="h-5 w-28 rounded-full bg-[#E5E7EB]" />
          <div className="h-7 w-4/5 rounded bg-[#E5E7EB]" />
          <div className="h-4 w-full rounded bg-[#E5E7EB]" />
        </div>
      </div>

      <div className="md:col-span-5 flex flex-col gap-5">
        {[1, 2, 3].map((idx) => (
          <div
            key={idx}
            className="flex gap-4 p-4 bg-white border border-[#E5E7EB] rounded-2xl animate-pulse"
          >
            <div className="w-28 h-24 rounded-xl bg-[#E5E7EB]/70 shrink-0" />
            <div className="flex-1 space-y-2.5 py-1">
              <div className="h-4 w-24 rounded-full bg-[#E5E7EB]" />
              <div className="h-5 w-full rounded bg-[#E5E7EB]" />
              <div className="h-3.5 w-1/2 rounded bg-[#E5E7EB]" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function EmptyState({ searchQuery, activeRegion, activeCategory, onReset }) {
  return (
    <div className="bg-white border border-[#E5E7EB] rounded-2xl p-10 sm:p-14 text-center max-w-xl mx-auto my-8">
      <div className="w-12 h-12 rounded-full bg-[#0D9488]/10 text-[#0D9488] flex items-center justify-center mx-auto mb-4">
        <SearchX className="w-6 h-6" />
      </div>
      <h3 className="font-editorial text-2xl font-bold text-[#1C1917] mb-2">
        No stories match your filter
      </h3>
      <p className="text-sm text-[#57534E] leading-relaxed mb-6">
        {searchQuery
          ? `We couldn't find any published stories matching "${searchQuery}".`
          : `No published dispatches found for ${activeRegion !== 'All' ? activeRegion : activeCategory}.`}
      </p>
      <button
        type="button"
        onClick={onReset}
        className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-[#0D9488] text-white text-sm font-semibold hover:bg-[#0F766E] transition-colors cursor-pointer"
      >
        Reset all filters
      </button>
    </div>
  );
}

export function ErrorBanner({ message, onRetry }) {
  return (
    <div
      role="alert"
      className="bg-white border border-red-200 rounded-2xl p-5 sm:p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-xs"
    >
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-xl bg-red-50 text-red-600 flex items-center justify-center shrink-0">
          <AlertTriangle className="w-5 h-5" />
        </div>
        <div>
          <h3 className="font-semibold text-[#1C1917] text-base">
            Unable to reach World Tourist newsroom
          </h3>
          <p className="text-sm text-[#57534E] mt-0.5">
            {message || 'The backend service is temporarily unreachable. Please try again.'}
          </p>
        </div>
      </div>

      <button
        type="button"
        onClick={onRetry}
        className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-[#0D9488] text-white text-sm font-semibold hover:bg-[#0F766E] transition-colors shrink-0 cursor-pointer"
      >
        <RefreshCw className="w-4 h-4" />
        Retry
      </button>
    </div>
  );
}
