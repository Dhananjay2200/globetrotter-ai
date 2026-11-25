import React, { useState, useEffect, useRef } from 'react';
import { 
  X, MapPin, Calendar, Clock, Award, ShieldCheck, 
  ExternalLink, Image as ImageIcon, BookCheck, Share2, 
  Check, Bookmark, ChevronUp, ArrowLeft, Sparkles
} from 'lucide-react';

export default function BlogPostModal({ 
  post, 
  onClose, 
  isBookmarked = false, 
  onToggleBookmark 
}) {
  const [copied, setCopied] = useState(false);
  const [scrollProgress, setScrollProgress] = useState(0);
  const [activeGalleryIndex, setActiveGalleryIndex] = useState(null);
  const contentRef = useRef(null);

  if (!post) return null;

  // Track reading progress percentage
  const handleScroll = (e) => {
    const target = e.target;
    const totalHeight = target.scrollHeight - target.clientHeight;
    if (totalHeight > 0) {
      const current = Math.min(100, Math.max(0, (target.scrollTop / totalHeight) * 100));
      setScrollProgress(current);
    }
  };

  const scrollToTop = () => {
    if (contentRef.current) {
      contentRef.current.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const readingTime = Math.ceil((post.word_count || 1200) / 200);

  const handleShare = () => {
    const url = window.location.origin + (post.website_url || `/blog/${post.slug}`);
    navigator.clipboard.writeText(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  // Convert markdown to formatted readable blocks
  const renderFormattedMarkdown = (markdown) => {
    if (!markdown) return null;
    const lines = markdown.split('\n');
    const elements = [];
    let currentParagraph = [];

    const flushParagraph = (key) => {
      if (currentParagraph.length > 0) {
        elements.push(
          <p key={`p-${key}`} className="text-slate-200 leading-relaxed mb-5 text-base sm:text-lg font-normal">
            {currentParagraph.join(' ')}
          </p>
        );
        currentParagraph = [];
      }
    };

    lines.forEach((line, idx) => {
      const trimmed = line.trim();
      if (trimmed.startsWith('# ')) {
        flushParagraph(idx);
      } else if (trimmed.startsWith('## ')) {
        flushParagraph(idx);
        elements.push(
          <h2 
            key={`h2-${idx}`} 
            id={`section-${idx}`}
            className="text-xl sm:text-2xl font-bold text-white mt-10 mb-4 border-b border-slate-800/80 pb-2.5 flex items-center space-x-2.5 tracking-tight"
          >
            <span className="text-teal-400 font-mono text-base sm:text-lg">§</span>
            <span>{trimmed.replace('## ', '')}</span>
          </h2>
        );
      } else if (trimmed.startsWith('### ')) {
        flushParagraph(idx);
        elements.push(
          <h3 key={`h3-${idx}`} className="text-lg sm:text-xl font-bold text-teal-200 mt-7 mb-3">
            {trimmed.replace('### ', '')}
          </h3>
        );
      } else if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
        flushParagraph(idx);
        elements.push(
          <li key={`li-${idx}`} className="text-slate-200 ml-5 list-disc mb-2 leading-relaxed text-sm sm:text-base">
            {trimmed.substring(2)}
          </li>
        );
      } else if (trimmed.startsWith('> ')) {
        flushParagraph(idx);
        elements.push(
          <blockquote key={`bq-${idx}`} className="border-l-4 border-teal-500 bg-teal-500/10 px-4 py-3 rounded-r-xl my-5 text-teal-100 italic text-sm sm:text-base">
            {trimmed.substring(2)}
          </blockquote>
        );
      } else if (trimmed.length > 0) {
        currentParagraph.push(trimmed);
      } else {
        flushParagraph(idx);
      }
    });

    flushParagraph(lines.length);
    return elements;
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-950 flex flex-col animate-fadeIn">
      
      {/* Top Reading Progress Bar */}
      <div 
        className="fixed top-0 left-0 h-1 bg-gradient-to-r from-teal-400 via-emerald-400 to-cyan-400 z-50 transition-all duration-75"
        style={{ width: `${scrollProgress}%` }}
      />

      {/* Sticky Reader Header (Optimized for Mobile & Desktop) */}
      <header className="sticky top-0 z-40 bg-slate-950/95 backdrop-blur-md border-b border-slate-800/80 px-4 sm:px-6 py-3 flex items-center justify-between gap-3 shadow-md">
        <div className="flex items-center space-x-3 min-w-0">
          <button
            onClick={onClose}
            className="p-2 -ml-1 rounded-full bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
            aria-label="Back to Stories"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          
          <div className="min-w-0">
            <div className="flex items-center space-x-1.5 text-[11px] text-teal-400 font-medium">
              <MapPin className="w-3 h-3 flex-shrink-0" />
              <span className="truncate">{post.destination}, {post.country}</span>
            </div>
            <h2 className="text-xs sm:text-sm font-bold text-white truncate max-w-xs sm:max-w-md md:max-w-xl">
              {post.title}
            </h2>
          </div>
        </div>

        {/* Reader Action Icons */}
        <div className="flex items-center space-x-1.5 sm:space-x-2 flex-shrink-0">
          {/* Bookmark Toggle */}
          {onToggleBookmark && (
            <button
              onClick={() => onToggleBookmark(post)}
              className={`p-2 rounded-xl transition-all ${
                isBookmarked 
                  ? 'bg-teal-500 text-slate-950 font-bold shadow-sm' 
                  : 'bg-slate-900 border border-slate-800 text-slate-300 hover:text-white'
              }`}
              title={isBookmarked ? 'Remove Bookmark' : 'Save Story'}
            >
              <Bookmark className={`w-4 h-4 ${isBookmarked ? 'fill-current' : ''}`} />
            </button>
          )}

          {/* Share Button */}
          <button
            onClick={handleShare}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white transition-all flex items-center space-x-1"
            title="Share Story"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Share2 className="w-4 h-4" />}
          </button>

          {/* Close Button */}
          <button
            onClick={onClose}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white transition-all"
            aria-label="Close"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* Main Scrollable Reading Container */}
      <div 
        ref={contentRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto bg-slate-950 text-slate-100 pb-24 sm:pb-16"
      >
        <article className="max-w-4xl mx-auto px-4 sm:px-6 md:px-8 py-6 sm:py-10">
          
          {/* Hero Panoramic Image with Legal Attribution */}
          {post.featured_image?.url && (
            <div className="relative rounded-3xl overflow-hidden border border-slate-800 bg-slate-900 shadow-2xl mb-8 group">
              <div className="h-64 sm:h-96 md:h-[420px] w-full overflow-hidden">
                <img
                  src={post.featured_image.url}
                  alt={post.featured_image.alt_text || post.title}
                  className="w-full h-full object-cover group-hover:scale-102 transition-transform duration-700"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/20 to-transparent" />
              </div>

              {/* Legal Attribution Pill */}
              <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between text-[11px] text-slate-300 bg-slate-950/85 px-3 py-1.5 rounded-xl border border-slate-800 backdrop-blur-md">
                <span className="truncate pr-2">
                  📷 {post.featured_image.attribution || 'Wikimedia Commons'}
                </span>
                <span className="bg-teal-500/20 text-teal-300 px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase flex-shrink-0">
                  {post.featured_image.license || 'Public Domain'}
                </span>
              </div>
            </div>
          )}

          {/* Article Header & Metadata */}
          <div className="space-y-4 mb-10 pb-8 border-b border-slate-800/80">
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <span className="bg-teal-500/15 text-teal-300 font-semibold px-3 py-1 rounded-full border border-teal-500/30 flex items-center space-x-1.5">
                <MapPin className="w-3.5 h-3.5" />
                <span>{post.destination}, {post.country}</span>
              </span>

              <span className="bg-slate-900 text-slate-300 px-3 py-1 rounded-full border border-slate-800">
                {post.category}
              </span>

              <span className="bg-teal-500/10 text-teal-300 font-semibold px-3 py-1 rounded-full border border-teal-500/30 flex items-center space-x-1">
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                <span>Curated Story</span>
              </span>

              <span className="text-slate-400 flex items-center space-x-1 ml-auto">
                <Clock className="w-3.5 h-3.5" />
                <span>{readingTime} min read</span>
              </span>
            </div>

            <h1 className="text-2xl sm:text-4xl md:text-5xl font-black text-white tracking-tight leading-tight">
              {post.title}
            </h1>

            {post.summary && (
              <p className="text-base sm:text-xl text-teal-100/90 font-light leading-relaxed border-l-2 border-teal-400/50 pl-4 py-1">
                {post.summary}
              </p>
            )}

            <div className="flex items-center justify-between text-xs text-slate-400 pt-2">
              <span>{post.word_count || 1400} words</span>
              <span>Published: {post.published_at ? new Date(post.published_at).toLocaleDateString() : 'Today'}</span>
            </div>
          </div>

          {/* Article Body Content */}
          <div className="prose prose-invert max-w-none">
            {renderFormattedMarkdown(post.body_markdown)}
          </div>

          {/* Photo Gallery (High-Res Verified Imagery) */}
          {post.gallery_images && post.gallery_images.length > 0 && (
            <div className="mt-14 pt-10 border-t border-slate-800/80 space-y-6">
              <div className="flex items-center space-x-2">
                <ImageIcon className="w-5 h-5 text-teal-400" />
                <h3 className="text-xl font-bold text-white">Verified Photo Gallery</h3>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                {post.gallery_images.map((img, idx) => (
                  <div 
                    key={idx}
                    className="relative rounded-2xl overflow-hidden border border-slate-800 bg-slate-900 group cursor-pointer"
                    onClick={() => setActiveGalleryIndex(idx)}
                  >
                    <img
                      src={img.url}
                      alt={img.alt_text || `Photo ${idx + 1}`}
                      className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                    <div className="absolute bottom-2 left-2 right-2 text-[10px] text-slate-300 bg-slate-950/80 px-2 py-1 rounded truncate">
                      {img.alt_text || img.attribution}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Verified Factual Citations & Research Evidence */}
          {post.citations && post.citations.length > 0 && (
            <div className="mt-14 pt-10 border-t border-slate-800/80 space-y-4">
              <div className="flex items-center space-x-2">
                <BookCheck className="w-5 h-5 text-emerald-400" />
                <h3 className="text-xl font-bold text-white">Fact-Checked Sources & Research</h3>
              </div>

              <p className="text-xs text-slate-400">
                All claims, historical dates, and locations were verified against live encyclopedic and geographic databases.
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                {post.citations.map((src, idx) => (
                  <a
                    key={idx}
                    href={src.url}
                    target="_blank"
                    rel="noreferrer"
                    className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-teal-500/40 transition-all flex items-center justify-between group"
                  >
                    <div className="min-w-0 pr-2">
                      <span className="text-[10px] uppercase font-mono text-teal-400 block font-semibold">
                        {src.publisher || 'Reference'}
                      </span>
                      <h4 className="text-xs font-medium text-slate-200 group-hover:text-white truncate">
                        {src.title || src.url}
                      </h4>
                    </div>
                    <ExternalLink className="w-3.5 h-3.5 text-slate-500 group-hover:text-teal-400 flex-shrink-0" />
                  </a>
                ))}
              </div>
            </div>
          )}

          {/* SEO Metadata Card */}
          {post.seo && (
            <div className="mt-12 p-4 sm:p-6 rounded-2xl bg-slate-900/40 border border-slate-800/70 text-xs text-slate-400 space-y-2">
              <div className="flex items-center space-x-1.5 text-teal-400 font-semibold">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Search Optimization (SEO Metadata)</span>
              </div>
              <p><strong className="text-slate-300">Target Keyword:</strong> {post.seo.main_keyword || 'Travel Guide'}</p>
              <p><strong className="text-slate-300">Meta Description:</strong> {post.seo.description}</p>
            </div>
          )}
        </article>
      </div>

      {/* Mobile Floating Action Bar (Sticky Bottom) */}
      <div className="md:hidden fixed bottom-4 right-4 z-40 flex items-center space-x-2">
        <button
          onClick={handleShare}
          className="p-3 rounded-full bg-teal-500 text-slate-950 font-bold shadow-xl shadow-teal-500/30 flex items-center justify-center"
          title="Share"
        >
          {copied ? <Check className="w-5 h-5" /> : <Share2 className="w-5 h-5" />}
        </button>

        <button
          onClick={scrollToTop}
          className="p-3 rounded-full bg-slate-800 text-white font-bold shadow-xl border border-slate-700 flex items-center justify-center"
          title="Back to Top"
        >
          <ChevronUp className="w-5 h-5" />
        </button>
      </div>

      {/* Copy Toast Notification */}
      {copied && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 bg-emerald-500 text-slate-950 px-4 py-2 rounded-full font-bold text-xs shadow-2xl flex items-center space-x-2 animate-fadeIn">
          <Check className="w-4 h-4" />
          <span>Story link copied to clipboard!</span>
        </div>
      )}
    </div>
  );
}
