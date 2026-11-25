import React, { useState } from 'react';
import { matchesCombinatorialFilter } from '../utils/geoRegions';
import { 
  Search, MapPin, Calendar, Clock, Award, ArrowRight, 
  Sparkles, Globe2, Filter, RefreshCw 
} from 'lucide-react';

const REGIONS = [
  'All',
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

export default function BlogFeed({ posts, loading, onSelectPost, onRefresh }) {
  const [selectedRegion, setSelectedRegion] = useState('All');
  const [selectedCategory, setSelectedCategory] = useState('All Categories');
  const [searchQuery, setSearchQuery] = useState('');

  // Filtering (Combinatorial AND search)
  const filteredPosts = (posts || []).filter(post => 
    matchesCombinatorialFilter(post, selectedRegion === 'All' ? 'All Regions' : selectedRegion, selectedCategory, searchQuery)
  );

  const heroPost = filteredPosts.length > 0 ? filteredPosts[0] : null;
  const gridPosts = filteredPosts.length > 1 ? filteredPosts.slice(1) : filteredPosts;

  return (
    <div className="space-y-10">
      {/* Hero Showcase (Latest Verified Travel Post) */}
      {heroPost && (
        <section className="relative rounded-3xl overflow-hidden border border-slate-800 bg-slate-900 shadow-2xl group">
          <div className="grid grid-cols-1 lg:grid-cols-12 min-h-[420px]">
            {/* Image Side */}
            <div className="lg:col-span-7 relative h-64 lg:h-auto overflow-hidden bg-slate-950">
              <img
                src={heroPost.featured_image?.url || 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800'}
                alt={heroPost.title}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
              />
              <div className="absolute inset-0 bg-gradient-to-t lg:bg-gradient-to-r from-slate-900 via-slate-900/40 to-transparent" />
              
              <div className="absolute top-4 left-4 bg-slate-950/80 backdrop-blur-md px-3 py-1.5 rounded-full text-xs font-semibold text-teal-300 border border-teal-500/30 flex items-center space-x-1.5">
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                <span>Featured AI Travel Story</span>
              </div>
            </div>

            {/* Content Side */}
            <div className="lg:col-span-5 p-6 sm:p-8 md:p-10 flex flex-col justify-between">
              <div>
                <div className="flex items-center space-x-2 text-xs font-medium mb-3">
                  <span className="text-teal-400 flex items-center space-x-1">
                    <MapPin className="w-3.5 h-3.5" />
                    <span>{heroPost.destination}, {heroPost.country}</span>
                  </span>
                  <span className="text-slate-600">•</span>
                  <span className="text-slate-400">{heroPost.category}</span>
                </div>

                <h2 className="text-2xl sm:text-3xl font-extrabold text-white leading-tight mb-4 tracking-tight group-hover:text-teal-300 transition-colors">
                  {heroPost.title}
                </h2>

                <p className="text-slate-300 text-sm leading-relaxed mb-6 line-clamp-3">
                  {heroPost.summary || heroPost.unique_angle}
                </p>
              </div>

              <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between">
                <div className="flex items-center space-x-3 text-xs">
                  <span className="text-slate-400 font-medium">
                    {heroPost.published_at 
                      ? new Date(heroPost.published_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
                      : 'Featured Story'}
                  </span>
                  <span className="text-slate-600">•</span>
                  <span className="text-slate-400">{heroPost.word_count} words</span>
                </div>

                <button
                  onClick={() => onSelectPost(heroPost)}
                  className="flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 text-xs font-bold transition-all shadow-lg shadow-teal-500/20"
                >
                  <span>Read Story</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Filter & Search Bar */}
      <section className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 sm:p-6 backdrop-blur-sm space-y-4">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          {/* Search Box */}
          <div className="relative w-full sm:w-96">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search destinations, countries, or topics..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-950/80 border border-slate-700/80 rounded-xl pl-10 pr-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500 transition-all"
            />
          </div>

          {/* Category Dropdown & Refresh */}
          <div className="flex items-center space-x-3 w-full sm:w-auto">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="bg-slate-950/80 border border-slate-700/80 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
            >
              {CATEGORIES.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>

            <button
              onClick={onRefresh}
              disabled={loading}
              className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors border border-slate-700/70"
              title="Refresh Stories"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-teal-400' : ''}`} />
            </button>
          </div>
        </div>

        {/* Global Region Filter Pills */}
        <div 
          onWheel={(e) => { if (e.deltaY !== 0) e.currentTarget.scrollLeft += e.deltaY; }}
          className="flex items-center space-x-2 overflow-x-auto pb-3 custom-scrollbar text-xs"
        >
          <span className="text-slate-500 font-semibold uppercase text-[10px] pr-2 shrink-0 flex items-center space-x-1">
            <Globe2 className="w-3 h-3 text-teal-400" />
            <span>Regions:</span>
          </span>
          {REGIONS.map(reg => (
            <button
              key={reg}
              onClick={() => setSelectedRegion(reg)}
              className={`px-3 py-1.5 rounded-lg shrink-0 transition-colors ${
                selectedRegion === reg
                  ? 'bg-teal-500 text-slate-950 font-bold shadow-sm'
                  : 'bg-slate-950/70 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {reg}
            </button>
          ))}
        </div>
      </section>

      {/* Blog Cards Grid */}
      <section>
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <span>Verified Global Articles</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-teal-300 font-mono">
              {filteredPosts.length} Stories
            </span>
          </h3>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map(n => (
              <div key={n} className="bg-slate-900 border border-slate-800 rounded-2xl h-80 animate-pulse" />
            ))}
          </div>
        ) : filteredPosts.length === 0 ? (
          <div className="text-center py-16 bg-slate-900/40 rounded-2xl border border-slate-800">
            <Globe2 className="w-12 h-12 text-slate-600 mx-auto mb-3 animate-bounce" />
            <p className="text-slate-300 font-medium">No published travel stories matching this filter yet.</p>
            <p className="text-slate-500 text-xs mt-1">Run the AI Pipeline in Operations to generate stories for this region!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredPosts.map((post) => (
              <article
                key={post.post_id || post.article_id}
                onClick={() => onSelectPost(post)}
                className="bg-slate-900/90 border border-slate-800/80 rounded-2xl overflow-hidden hover:border-slate-700 transition-all duration-300 hover:shadow-xl hover:shadow-slate-950/50 flex flex-col cursor-pointer group"
              >
                {/* Featured Card Image */}
                <div className="relative h-48 w-full bg-slate-950 overflow-hidden">
                  <img
                    src={post.featured_image?.url || 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e'}
                    alt={post.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent" />
                  
                  {/* Category Pill */}
                  <span className="absolute top-3 left-3 bg-slate-950/80 backdrop-blur-sm text-teal-300 text-[10px] font-semibold px-2.5 py-1 rounded-md border border-teal-500/20">
                    {post.category}
                  </span>
                </div>

                {/* Card Content */}
                <div className="p-5 flex-1 flex flex-col justify-between">
                  <div>
                    <div className="text-[11px] text-teal-400 font-medium flex items-center space-x-1 mb-2">
                      <MapPin className="w-3 h-3" />
                      <span>{post.destination}, {post.country}</span>
                    </div>

                    <h4 className="text-base font-bold text-white group-hover:text-teal-300 transition-colors line-clamp-2 leading-snug mb-2">
                      {post.title}
                    </h4>

                    <p className="text-xs text-slate-400 line-clamp-3 leading-relaxed mb-4">
                      {post.summary || post.unique_angle}
                    </p>
                  </div>

                  {/* Card Footer */}
                  <div className="pt-3 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-500">
                    <span className="flex items-center space-x-1">
                      <Clock className="w-3 h-3" />
                      <span>{post.word_count} words</span>
                    </span>

                    <span className="text-teal-400 font-semibold group-hover:translate-x-1 transition-transform flex items-center space-x-1">
                      <span>Explore</span>
                      <ArrowRight className="w-3 h-3" />
                    </span>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
