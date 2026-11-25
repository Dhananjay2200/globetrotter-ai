import React, { useState, useEffect, useRef } from 'react';
import UserNavbar from '../components/UserNavbar';
import MobileBottomNav from '../components/MobileBottomNav';
import MobileFilterDrawer from '../components/MobileFilterDrawer';
import BookmarksModal from '../components/BookmarksModal';
import { matchesCombinatorialFilter, resolvePostRegion } from '../utils/geoRegions';
import { 
  Search, MapPin, Calendar, Clock, Award, ArrowRight, 
  Sparkles, Globe2, Filter, Bookmark, RefreshCw, Compass,
  ChevronLeft, ChevronRight, ArrowUpDown, SlidersHorizontal
} from 'lucide-react';

const DATE_FILTERS = [
  { id: 'all', label: 'All Dates' },
  { id: 'today', label: 'Published Today' },
  { id: 'week', label: 'Past 7 Days' },
  { id: 'month', label: 'Past 30 Days' },
  { id: 'custom', label: 'Custom Date' },
];

const REGIONS = [
  'All Regions',
  'East & Southeast Asia',
  'South & Central Asia',
  'Western & Northern Europe',
  'Southern & Eastern Europe',
  'North America',
  'South America',
  'Middle East & North Africa',
  'Sub-Saharan Africa',
  'Oceania & Pacific Islands',
];

const CATEGORIES = [
  'All Categories',
  'Historical Monuments & Heritage Sites',
  'Waterfalls, Mountains & Natural Wonders',
  'Hidden Gems & Unexplored Places',
  'Local Cuisines & Culinary Journeys',
  'Wildlife, Safaris & National Parks',
  'Coastal Escapes & Island Wonders',
];

export default function UserBlogPortal({ 
  posts = [], 
  loading = false, 
  onSelectPost, 
  onRefresh, 
  onSwitchToAdmin 
}) {
  const [selectedRegion, setSelectedRegion] = useState('All Regions');
  const [selectedCategory, setSelectedCategory] = useState('All Categories');
  const [selectedDateFilter, setSelectedDateFilter] = useState('all');
  const [customDate, setCustomDate] = useState('');
  const [sortOrder, setSortOrder] = useState('desc');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Horizontal Scroll & Date Picker Refs
  const regionScrollRef = useRef(null);
  const categoryScrollRef = useRef(null);
  const dateInputRef = useRef(null);

  const scrollRegions = (direction) => {
    if (regionScrollRef.current) {
      regionScrollRef.current.scrollBy({
        left: direction === 'left' ? -280 : 280,
        behavior: 'smooth',
      });
    }
  };

  const scrollCategories = (direction) => {
    if (categoryScrollRef.current) {
      categoryScrollRef.current.scrollBy({
        left: direction === 'left' ? -280 : 280,
        behavior: 'smooth',
      });
    }
  };

  const handleHorizontalWheel = (e) => {
    if (e.deltaY !== 0) {
      e.currentTarget.scrollLeft += e.deltaY;
    }
  };
  
  // Mobile Drawers
  const [filterDrawerOpen, setFilterDrawerOpen] = useState(false);
  const [bookmarksModalOpen, setBookmarksModalOpen] = useState(false);

  // Bookmarks saved in browser localStorage
  const [bookmarks, setBookmarks] = useState(() => {
    try {
      const saved = localStorage.getItem('globetrotter_saved_posts');
      return saved ? JSON.parse(saved) : [];
    } catch (_) {
      return [];
    }
  });

  const toggleBookmark = (post) => {
    setBookmarks(prev => {
      const exists = prev.some(p => (p.slug || p.id) === (post.slug || post.id));
      let updated;
      if (exists) {
        updated = prev.filter(p => (p.slug || p.id) !== (post.slug || post.id));
      } else {
        updated = [post, ...prev];
      }
      try {
        localStorage.setItem('globetrotter_saved_posts', JSON.stringify(updated));
      } catch (_) {}
      return updated;
    });
  };

  const isPostBookmarked = (post) => {
    return bookmarks.some(p => (p.slug || p.id) === (post.slug || post.id));
  };

  const removeBookmark = (identifier) => {
    setBookmarks(prev => {
      const updated = prev.filter(p => (p.slug || p.id) !== identifier);
      try {
        localStorage.setItem('globetrotter_saved_posts', JSON.stringify(updated));
      } catch (_) {}
      return updated;
    });
  };

  // Combinatorial Multi-Filter (Region AND Category AND Date AND Search Query)
  const filteredPosts = (posts || [])
    .filter(post => 
      matchesCombinatorialFilter(post, selectedRegion, selectedCategory, selectedDateFilter, searchQuery, customDate)
    )
    .sort((a, b) => {
      const dateA = new Date(a.published_at || a.created_at).getTime() || 0;
      const dateB = new Date(b.published_at || b.created_at).getTime() || 0;
      return sortOrder === 'desc' ? dateB - dateA : dateA - dateB;
    });

  const resetAllFilters = () => {
    setSelectedRegion('All Regions');
    setSelectedCategory('All Categories');
    setSelectedDateFilter('all');
    setCustomDate('');
    setSearchQuery('');
  };

  const hasActiveFilters = selectedRegion !== 'All Regions' || 
    selectedCategory !== 'All Categories' || 
    selectedDateFilter !== 'all' || 
    Boolean(customDate) || 
    Boolean(searchQuery.trim());

  const heroPost = filteredPosts.length > 0 ? filteredPosts[0] : null;
  const gridPosts = filteredPosts.length > 1 ? filteredPosts.slice(1) : filteredPosts;

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-teal-500 selection:text-slate-950 pb-20 md:pb-0">
      
      {/* User Header */}
      <UserNavbar
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        savedCount={bookmarks.length}
        onOpenBookmarks={() => setBookmarksModalOpen(true)}
        onOpenFilter={() => setFilterDrawerOpen(true)}
        onSwitchToAdmin={onSwitchToAdmin}
      />

      {/* Main Reading Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-8 sm:space-y-10">
        
        {/* Horizontal Region Filter Pills (Visible Scrollbar, Chevrons & Wheel Scroll) */}
        <section className="relative">
          {/* Scroll Left Button */}
          <button
            onClick={() => scrollRegions('left')}
            className="hidden sm:flex absolute -left-3 top-1/2 -translate-y-1/2 z-10 w-8 h-8 rounded-full bg-slate-900/90 border border-slate-700 text-slate-300 hover:text-white hover:bg-slate-800 items-center justify-center shadow-lg transition-all"
            aria-label="Scroll regions left"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>

          {/* Scrollable Container with Custom Visible Scrollbar */}
          <div 
            ref={regionScrollRef}
            onWheel={handleHorizontalWheel}
            className="flex items-center space-x-2 overflow-x-auto pb-3 pt-1 custom-scrollbar scroll-smooth px-1"
          >
            {REGIONS.map(reg => {
              const active = selectedRegion === reg;
              return (
                <button
                  key={reg}
                  onClick={() => setSelectedRegion(reg)}
                  className={`flex-shrink-0 px-4 py-2 rounded-full text-xs font-semibold transition-all flex items-center space-x-1.5 whitespace-nowrap ${
                    active
                      ? 'bg-teal-500 text-slate-950 shadow-md shadow-teal-500/20 font-bold'
                      : 'bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:border-slate-700'
                  }`}
                >
                  <Globe2 className="w-3.5 h-3.5" />
                  <span>{reg}</span>
                </button>
              );
            })}
          </div>

          {/* Scroll Right Button */}
          <button
            onClick={() => scrollRegions('right')}
            className="hidden sm:flex absolute -right-3 top-1/2 -translate-y-1/2 z-10 w-8 h-8 rounded-full bg-slate-900/90 border border-slate-700 text-slate-300 hover:text-white hover:bg-slate-800 items-center justify-center shadow-lg transition-all"
            aria-label="Scroll regions right"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </section>

        {/* Featured / Hero Travel Story */}
        {heroPost && !searchQuery && selectedCategory === 'All Categories' && selectedRegion === 'All Regions' && (
          <section className="relative rounded-3xl overflow-hidden border border-slate-800 bg-slate-900 shadow-2xl group">
            <div className="grid grid-cols-1 lg:grid-cols-12 min-h-[380px] sm:min-h-[440px]">
              
              {/* Image Side */}
              <div className="lg:col-span-7 relative h-64 sm:h-80 lg:h-auto overflow-hidden bg-slate-950">
                <img
                  src={heroPost.featured_image?.url || 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800'}
                  alt={heroPost.title}
                  className="w-full h-full object-cover group-hover:scale-103 transition-transform duration-700"
                />
                <div className="absolute inset-0 bg-gradient-to-t lg:bg-gradient-to-r from-slate-900 via-slate-900/40 to-transparent" />
                
                <div className="absolute top-4 left-4 bg-slate-950/85 backdrop-blur-md px-3 py-1.5 rounded-full text-xs font-semibold text-teal-300 border border-teal-500/30 flex items-center space-x-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                  <span>Featured Travel Story</span>
                </div>

                {/* Bookmark Button on Hero */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleBookmark(heroPost);
                  }}
                  className={`absolute top-4 right-4 p-2.5 rounded-full backdrop-blur-md border transition-all ${
                    isPostBookmarked(heroPost)
                      ? 'bg-teal-500 text-slate-950 border-teal-400'
                      : 'bg-slate-950/70 text-slate-300 border-slate-700/60 hover:text-white'
                  }`}
                  title="Bookmark"
                >
                  <Bookmark className={`w-4 h-4 ${isPostBookmarked(heroPost) ? 'fill-current' : ''}`} />
                </button>
              </div>

              {/* Content Side */}
              <div className="lg:col-span-5 p-6 sm:p-8 flex flex-col justify-between">
                <div>
                  <div className="flex items-center space-x-2 text-xs font-medium mb-3">
                    <span className="text-teal-400 flex items-center space-x-1 font-semibold">
                      <MapPin className="w-3.5 h-3.5" />
                      <span>{heroPost.destination}, {heroPost.country}</span>
                    </span>
                    <span className="text-slate-600">•</span>
                    <span className="text-slate-400 truncate">{heroPost.category}</span>
                  </div>

                  <h2 
                    onClick={() => onSelectPost(heroPost)}
                    className="text-xl sm:text-2xl md:text-3xl font-extrabold text-white leading-tight mb-4 tracking-tight group-hover:text-teal-300 transition-colors cursor-pointer"
                  >
                    {heroPost.title}
                  </h2>

                  <p className="text-slate-300 text-xs sm:text-sm leading-relaxed mb-6 line-clamp-3">
                    {heroPost.summary || heroPost.unique_angle}
                  </p>
                </div>

                <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between">
                  <div className="flex items-center space-x-2 sm:space-x-3 text-xs">
                    <span className="text-slate-400 font-medium">
                      {heroPost.published_at 
                        ? new Date(heroPost.published_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
                        : 'Featured Guide'}
                    </span>
                    <span className="text-slate-600">•</span>
                    <span className="text-slate-400">{heroPost.word_count} words</span>
                  </div>

                  <button
                    onClick={() => onSelectPost(heroPost)}
                    className="flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 text-xs font-bold transition-all shadow-lg shadow-teal-500/20"
                  >
                    <span>Read Guide</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Category Pill Filters (Visible Scrollbar, Chevrons & Wheel Scroll) */}
        <section className="bg-slate-900/70 border border-slate-800/90 rounded-2xl p-4 backdrop-blur-sm space-y-3 shadow-lg">
          <div className="flex items-center justify-between text-xs">
            <span className="font-bold text-teal-400 uppercase tracking-wider text-[11px] flex items-center space-x-1.5">
              <Filter className="w-3.5 h-3.5" />
              <span>Travel Themes & Categories</span>
            </span>
            <span className="text-slate-400 font-mono text-[11px]">
              {filteredPosts.length} stories available
            </span>
          </div>

          <div className="relative">
            {/* Scroll Left Button */}
            <button
              onClick={() => scrollCategories('left')}
              className="hidden sm:flex absolute -left-3 top-1/2 -translate-y-1/2 z-10 w-7 h-7 rounded-full bg-slate-950/90 border border-slate-700 text-slate-300 hover:text-white hover:bg-slate-800 items-center justify-center shadow-md transition-all"
              aria-label="Scroll categories left"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>

            {/* Scrollable Container with Custom Visible Scrollbar */}
            <div 
              ref={categoryScrollRef}
              onWheel={handleHorizontalWheel}
              className="flex items-center space-x-2 overflow-x-auto pb-3 pt-1 custom-scrollbar scroll-smooth px-1"
            >
              {CATEGORIES.map(cat => {
                const active = selectedCategory === cat;
                return (
                  <button
                    key={cat}
                    onClick={() => setSelectedCategory(cat)}
                    className={`flex-shrink-0 px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all whitespace-nowrap ${
                      active
                        ? 'bg-teal-500/20 text-teal-300 border border-teal-500/50 font-bold shadow-sm'
                        : 'bg-slate-950/70 border border-slate-800/80 text-slate-400 hover:text-white hover:border-slate-700'
                    }`}
                  >
                    {cat}
                  </button>
                );
              })}
            </div>

            {/* Scroll Right Button */}
            <button
              onClick={() => scrollCategories('right')}
              className="hidden sm:flex absolute -right-3 top-1/2 -translate-y-1/2 z-10 w-7 h-7 rounded-full bg-slate-950/90 border border-slate-700 text-slate-300 hover:text-white hover:bg-slate-800 items-center justify-center shadow-md transition-all"
              aria-label="Scroll categories right"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </section>

        {/* Date Filter & Sorting Section */}
        <section className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4 backdrop-blur-sm shadow-md space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
            <div className="flex items-center space-x-2">
              <span className="font-bold text-amber-400 uppercase tracking-wider text-[11px] flex items-center space-x-1.5">
                <Calendar className="w-3.5 h-3.5" />
                <span>Publication Timeline</span>
              </span>
              <span className="text-slate-600">•</span>
              <span className="text-slate-400 text-[11px]">Filter & sort stories date-wise</span>
            </div>

            {/* Sort Order Toggle */}
            <button
              onClick={() => setSortOrder(prev => prev === 'desc' ? 'asc' : 'desc')}
              className="flex items-center space-x-1.5 text-xs text-slate-300 hover:text-white px-3 py-1.5 rounded-xl bg-slate-950/80 border border-slate-800 self-start sm:self-auto transition-colors shadow-sm"
              title="Toggle Chronological Sorting Order"
            >
              <ArrowUpDown className="w-3.5 h-3.5 text-teal-400" />
              <span>{sortOrder === 'desc' ? 'Newest First' : 'Oldest First'}</span>
            </button>
          </div>

          <div className="flex flex-wrap items-center gap-2 pt-1">
            {DATE_FILTERS.map(df => {
              const active = selectedDateFilter === df.id;
              return (
                <button
                  key={df.id}
                  onClick={() => {
                    setSelectedDateFilter(df.id);
                    if (df.id !== 'custom') setCustomDate('');
                  }}
                  className={`px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all flex items-center space-x-1.5 ${
                    active
                      ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold shadow-sm'
                      : 'bg-slate-950/70 border border-slate-800/80 text-slate-400 hover:text-white hover:border-slate-700'
                  }`}
                >
                  <Calendar className="w-3 h-3" />
                  <span>{df.label}</span>
                </button>
              );
            })}

            {/* Custom Date Input with Interactive Calendar Trigger */}
            {selectedDateFilter === 'custom' && (
              <div 
                onClick={() => dateInputRef.current?.showPicker?.()}
                className="flex items-center space-x-2 bg-slate-950 border border-amber-500/70 rounded-xl px-3 py-1.5 cursor-pointer hover:border-amber-400 transition-all shadow-md group animate-fadeIn"
                title="Click to open calendar"
              >
                <Calendar className="w-4 h-4 text-amber-400 group-hover:scale-110 transition-transform" />
                <input
                  ref={dateInputRef}
                  type="date"
                  value={customDate}
                  onChange={(e) => setCustomDate(e.target.value)}
                  onClick={(e) => {
                    e.stopPropagation();
                    e.target.showPicker?.();
                  }}
                  style={{ colorScheme: 'dark' }}
                  className="bg-transparent text-xs text-amber-200 focus:outline-none cursor-pointer font-medium"
                />
                {customDate && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setCustomDate('');
                    }}
                    className="text-slate-500 hover:text-white text-xs px-1 ml-1"
                    title="Clear date"
                  >
                    ✕
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Active Combinatorial Filter Chips */}
          {hasActiveFilters && (
            <div className="pt-2 border-t border-slate-800/60 flex flex-wrap items-center gap-2 text-[11px] animate-fadeIn">
              <span className="text-slate-500 font-semibold">Active:</span>
              {selectedRegion !== 'All Regions' && (
                <span className="bg-teal-500/10 text-teal-300 border border-teal-500/30 px-2 py-0.5 rounded-md flex items-center space-x-1">
                  <span>Region: {selectedRegion}</span>
                  <button onClick={() => setSelectedRegion('All Regions')} className="hover:text-white ml-1">✕</button>
                </span>
              )}
              {selectedCategory !== 'All Categories' && (
                <span className="bg-teal-500/10 text-teal-300 border border-teal-500/30 px-2 py-0.5 rounded-md flex items-center space-x-1">
                  <span>Category: {selectedCategory}</span>
                  <button onClick={() => setSelectedCategory('All Categories')} className="hover:text-white ml-1">✕</button>
                </span>
              )}
              {selectedDateFilter !== 'all' && (
                <span className="bg-amber-500/10 text-amber-300 border border-amber-500/30 px-2 py-0.5 rounded-md flex items-center space-x-1">
                  <span>Date: {selectedDateFilter === 'custom' ? (customDate || 'Pick Date') : DATE_FILTERS.find(d => d.id === selectedDateFilter)?.label}</span>
                  <button onClick={() => { setSelectedDateFilter('all'); setCustomDate(''); }} className="hover:text-white ml-1">✕</button>
                </span>
              )}
              {searchQuery.trim() && (
                <span className="bg-indigo-500/10 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded-md flex items-center space-x-1">
                  <span>Query: "{searchQuery}"</span>
                  <button onClick={() => setSearchQuery('')} className="hover:text-white ml-1">✕</button>
                </span>
              )}
              <button
                onClick={resetAllFilters}
                className="text-slate-400 hover:text-rose-400 text-[11px] underline ml-auto transition-colors"
              >
                Clear all filters
              </button>
            </div>
          )}
        </section>

        {/* Stories Grid (Responsive: 1 col on mobile, 2 on tablet, 3 on desktop) */}
        <section className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg sm:text-xl font-bold text-white flex items-center space-x-2">
              <span>
                {selectedRegion === 'All Regions' ? 'Worldwide Guides' : selectedRegion}
                {selectedCategory !== 'All Categories' ? ` • ${selectedCategory}` : ''}
              </span>
              <span className="text-xs font-normal text-slate-500">({filteredPosts.length})</span>
            </h3>

            {/* Mobile Filter Button Indicator */}
            <button
              onClick={() => setFilterDrawerOpen(true)}
              className="md:hidden flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300"
            >
              <Filter className="w-3.5 h-3.5 text-teal-400" />
              <span>Filters</span>
            </button>
          </div>

          {filteredPosts.length === 0 ? (
            <div className="p-10 sm:p-14 text-center rounded-3xl bg-slate-900/60 border border-slate-800 space-y-4 shadow-xl">
              <div className="w-16 h-16 mx-auto rounded-2xl bg-slate-800/80 flex items-center justify-center text-slate-500">
                <Compass className="w-8 h-8 text-teal-400" />
              </div>
              <h4 className="text-base font-bold text-white">
                {selectedRegion !== 'All Regions' && selectedCategory !== 'All Categories'
                  ? `No stories found for "${selectedRegion}" + "${selectedCategory}"`
                  : selectedRegion !== 'All Regions'
                  ? `No published stories in ${selectedRegion} yet`
                  : `No travel stories found`}
              </h4>
              <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
                {selectedRegion !== 'All Regions' && selectedCategory !== 'All Categories'
                  ? `There are currently no articles matching both "${selectedRegion}" and "${selectedCategory}". You can view all stories in ${selectedRegion}, or explore all ${selectedCategory} worldwide.`
                  : `Try searching for a different destination, or reset your region and category filters to browse all published guides.`}
              </p>
              
              <div className="flex flex-wrap items-center justify-center gap-2 pt-2">
                {selectedCategory !== 'All Categories' && (
                  <button
                    onClick={() => setSelectedCategory('All Categories')}
                    className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-teal-300 font-semibold text-xs border border-slate-700 transition-colors"
                  >
                    Show all in {selectedRegion}
                  </button>
                )}
                {selectedRegion !== 'All Regions' && (
                  <button
                    onClick={() => setSelectedRegion('All Regions')}
                    className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-teal-300 font-semibold text-xs border border-slate-700 transition-colors"
                  >
                    Show all {selectedCategory}
                  </button>
                )}
                <button
                  onClick={() => {
                    setSearchQuery('');
                    setSelectedRegion('All Regions');
                    setSelectedCategory('All Categories');
                  }}
                  className="px-4 py-2 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs shadow-md transition-all"
                >
                  Reset All Filters
                </button>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6">
              {filteredPosts.map(post => {
                const bookmarked = isPostBookmarked(post);
                const readingTime = Math.ceil((post.word_count || 1200) / 200);

                return (
                  <article
                    key={post.slug || post.id}
                    className="group rounded-2xl bg-slate-900/70 border border-slate-800 hover:border-slate-700 transition-all duration-300 flex flex-col overflow-hidden shadow-lg hover:shadow-teal-500/5"
                  >
                    {/* Thumbnail Image */}
                    <div 
                      className="relative h-48 sm:h-52 w-full overflow-hidden bg-slate-950 cursor-pointer"
                      onClick={() => onSelectPost(post)}
                    >
                      <img
                        src={post.featured_image?.url || 'https://images.unsplash.com/photo-1488646953014-85cb44e25828'}
                        alt={post.title}
                        loading="lazy"
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-transparent" />

                      {/* Destination Pin */}
                      <div className="absolute bottom-3 left-3 flex items-center space-x-1.5 text-xs font-semibold text-white bg-slate-950/80 backdrop-blur-md px-2.5 py-1 rounded-lg border border-slate-800">
                        <MapPin className="w-3.5 h-3.5 text-teal-400" />
                        <span className="truncate max-w-[180px]">{post.destination}, {post.country}</span>
                      </div>

                      {/* Bookmark Icon */}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleBookmark(post);
                        }}
                        className={`absolute top-3 right-3 p-2 rounded-xl backdrop-blur-md border transition-all ${
                          bookmarked
                            ? 'bg-teal-500 text-slate-950 border-teal-400'
                            : 'bg-slate-950/70 text-slate-300 border-slate-700/60 hover:text-white'
                        }`}
                        title="Save story"
                      >
                        <Bookmark className={`w-3.5 h-3.5 ${bookmarked ? 'fill-current' : ''}`} />
                      </button>
                    </div>

                    {/* Card Content */}
                    <div className="p-5 flex-1 flex flex-col justify-between space-y-4">
                      <div>
                        <div className="flex items-center justify-between text-[11px] text-slate-400 mb-2">
                          <span className="text-teal-400/90 font-medium truncate max-w-[180px]">
                            {post.category}
                          </span>
                          <span className="flex items-center space-x-1">
                            <Clock className="w-3 h-3" />
                            <span>{readingTime} min</span>
                          </span>
                        </div>

                        <h4 
                          onClick={() => onSelectPost(post)}
                          className="text-base font-bold text-white group-hover:text-teal-300 transition-colors line-clamp-2 leading-snug cursor-pointer"
                        >
                          {post.title}
                        </h4>

                        <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed mt-2">
                          {post.summary}
                        </p>
                      </div>

                      <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between">
                        <span className="text-[11px] text-slate-500 font-medium">
                          {post.published_at 
                            ? new Date(post.published_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
                            : 'Travel Guide'}
                        </span>

                        <button
                          onClick={() => onSelectPost(post)}
                          className="flex items-center space-x-1 text-xs font-bold text-teal-400 hover:text-teal-300 transition-colors group-hover:translate-x-1 duration-200"
                        >
                          <span>Read</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </section>
      </main>

      {/* Reader Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-10 mt-16 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <Compass className="w-4 h-4 text-teal-400" />
            <span className="font-semibold text-slate-300">GlobeTrotter Stories</span>
            <span>•</span>
            <span>Worldwide Tourism Knowledge Engine</span>
          </div>

          <div className="flex items-center space-x-4">
            <button
              onClick={onSwitchToAdmin}
              className="text-slate-400 hover:text-amber-400 transition-colors flex items-center space-x-1"
            >
              <span>Admin Console</span>
            </button>
          </div>
        </div>
      </footer>

      {/* Mobile Bottom Navigation Bar */}
      <MobileBottomNav
        onScrollToTop={scrollToTop}
        onOpenFilter={() => setFilterDrawerOpen(true)}
        savedCount={bookmarks.length}
        onOpenBookmarks={() => setBookmarksModalOpen(true)}
        onSwitchToAdmin={onSwitchToAdmin}
      />

      {/* Mobile Filter Drawer */}
      <MobileFilterDrawer
        isOpen={filterDrawerOpen}
        onClose={() => setFilterDrawerOpen(false)}
        regions={REGIONS}
        selectedRegion={selectedRegion}
        onSelectRegion={(reg) => {
          setSelectedRegion(reg);
          setFilterDrawerOpen(false);
        }}
        categories={CATEGORIES}
        selectedCategory={selectedCategory}
        onSelectCategory={(cat) => {
          setSelectedCategory(cat);
          setFilterDrawerOpen(false);
        }}
        dateFilters={DATE_FILTERS}
        selectedDateFilter={selectedDateFilter}
        onSelectDateFilter={(df) => {
          setSelectedDateFilter(df);
          if (df !== 'custom') setCustomDate('');
        }}
        customDate={customDate}
        onSelectCustomDate={setCustomDate}
        totalResults={filteredPosts.length}
        onResetFilters={resetAllFilters}
      />

      {/* Saved Stories / Bookmarks Modal */}
      {bookmarksModalOpen && (
        <BookmarksModal
          bookmarks={bookmarks}
          onClose={() => setBookmarksModalOpen(false)}
          onSelectPost={onSelectPost}
          onRemoveBookmark={removeBookmark}
        />
      )}
    </div>
  );
}
