import React, { useState } from 'react';
import { Bookmark, MapPin, Calendar, Clock, ArrowUpRight } from 'lucide-react';
import {
  computeReadTime,
  formatLocation,
  formatPublishedDate,
  getExcerpt,
  getFallbackImageUrl,
} from '../utils/editorial';

export default function HeroSection({ post, isBookmarked, onToggleBookmark, onOpenPost }) {
  const [imgError, setImgError] = useState(false);

  if (!post) return null;

  const fallbackImg = getFallbackImageUrl(post.destination || post.title);
  const coverSrc = !imgError && post.featured_image?.url ? post.featured_image.url : fallbackImg;
  const location = formatLocation(post);
  const dateStr = formatPublishedDate(post.published_at);
  const readTime = computeReadTime(post);
  const excerpt = getExcerpt(post, 190);

  return (
    <section aria-label="Featured Story" className="mb-10">
      <article className="group relative w-full min-h-[380px] sm:min-h-[470px] rounded-2xl overflow-hidden border border-[#E5E7EB] bg-[#1C1917]">
        {/* Background Cover Image */}
        <img
          src={coverSrc}
          alt={post.featured_image?.alt_text || post.title}
          onError={() => setImgError(true)}
          onClick={() => onOpenPost(post)}
          className="absolute inset-0 w-full h-full object-cover object-center group-hover:scale-[1.02] transition-transform duration-700 cursor-pointer"
        />

        {/* Subtle Bottom Dark Gradient Overlay */}
        <div
          onClick={() => onOpenPost(post)}
          className="absolute inset-0 bg-gradient-to-t from-[#1C1917]/95 via-[#1C1917]/45 to-transparent cursor-pointer"
        />

        {/* Top Bookmark Button */}
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onToggleBookmark(post);
          }}
          aria-label={isBookmarked ? 'Remove bookmark' : 'Save story'}
          className="absolute top-4 right-4 sm:top-6 sm:right-6 z-10 w-10 h-10 rounded-full bg-white/90 backdrop-blur-sm border border-[#E5E7EB] flex items-center justify-center text-[#1C1917] hover:bg-white transition-colors cursor-pointer"
        >
          <Bookmark
            className={`w-4 h-4 ${
              isBookmarked ? 'fill-[#0D9488] text-[#0D9488]' : 'text-[#1C1917]'
            }`}
          />
        </button>

        {/* Bottom Editorial Content Overlay */}
        <div
          onClick={() => onOpenPost(post)}
          className="relative z-10 flex flex-col justify-end min-h-[380px] sm:min-h-[470px] p-6 sm:p-10 max-w-4xl cursor-pointer"
        >
          <div className="flex flex-wrap items-center gap-2.5 mb-3">
            {post.category && (
              <span className="px-3 py-1 rounded-full bg-[#0D9488] text-white text-xs font-semibold tracking-wide">
                {post.category}
              </span>
            )}
            {post.region && (
              <span className="px-3 py-1 rounded-full bg-white/15 backdrop-blur-sm text-white text-xs font-medium">
                {post.region}
              </span>
            )}
          </div>

          <h1 className="font-editorial text-2xl sm:text-4xl lg:text-[42px] font-bold text-white leading-[1.15] mb-3 group-hover:text-[#CCFBF1] transition-colors">
            {post.title}
          </h1>

          {excerpt && (
            <p className="text-white/85 text-sm sm:text-base leading-relaxed max-w-2xl mb-4 line-clamp-2">
              {excerpt}
            </p>
          )}

          <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-xs sm:text-sm text-white/80">
            {location && (
              <span className="inline-flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-[#5EEAD4]" />
                {location}
              </span>
            )}
            {dateStr && (
              <span className="inline-flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-[#5EEAD4]" />
                {dateStr}
              </span>
            )}
            {readTime && (
              <span className="inline-flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-[#5EEAD4]" />
                {readTime}
              </span>
            )}
            <span className="inline-flex items-center gap-1 text-[#5EEAD4] font-semibold ml-auto">
              Read Story
              <ArrowUpRight className="w-4 h-4" />
            </span>
          </div>
        </div>
      </article>
    </section>
  );
}
