import React, { useState } from 'react';
import { Bookmark, MapPin, Calendar } from 'lucide-react';
import {
  formatLocation,
  formatPublishedDate,
  getExcerpt,
  getFallbackImageUrl,
} from '../utils/editorial';

function CardImage({ post, className }) {
  const [failed, setFailed] = useState(false);
  const src =
    !failed && post.featured_image?.url
      ? post.featured_image.url
      : getFallbackImageUrl(post.destination || post.title);

  return (
    <img
      src={src}
      alt={post.featured_image?.alt_text || post.title}
      onError={() => setFailed(true)}
      loading="lazy"
      className={className}
    />
  );
}

function LargeEditorialCard({ post, isBookmarked, onToggleBookmark, onOpenPost }) {
  const dateStr = formatPublishedDate(post.published_at);
  const location = formatLocation(post);
  const excerpt = getExcerpt(post, 150);

  return (
    <article
      onClick={() => onOpenPost(post)}
      className="group bg-white border border-[#E5E7EB] rounded-2xl overflow-hidden flex flex-col justify-between hover:border-[#0D9488]/50 transition-all cursor-pointer h-full"
    >
      <div>
        <div className="relative h-60 sm:h-72 overflow-hidden bg-[#FAF9F6]">
          <CardImage
            post={post}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onToggleBookmark(post);
            }}
            aria-label={isBookmarked ? 'Remove bookmark' : 'Bookmark story'}
            className="absolute top-3.5 right-3.5 w-9 h-9 rounded-full bg-white/95 border border-[#E5E7EB] flex items-center justify-center text-[#1C1917] hover:border-[#0D9488] transition-colors cursor-pointer"
          >
            <Bookmark
              className={`w-4 h-4 ${
                isBookmarked ? 'fill-[#0D9488] text-[#0D9488]' : 'text-[#57534E]'
              }`}
            />
          </button>
        </div>

        <div className="p-6">
          {post.category && (
            <span className="inline-block px-2.5 py-1 rounded-full bg-[#0D9488]/10 text-[#0D9488] text-xs font-semibold mb-3">
              {post.category}
            </span>
          )}
          <h3 className="font-editorial text-xl sm:text-2xl font-bold text-[#1C1917] leading-snug mb-2.5 group-hover:text-[#0D9488] transition-colors">
            {post.title}
          </h3>
          {excerpt && (
            <p className="text-sm text-[#57534E] leading-relaxed line-clamp-3">
              {excerpt}
            </p>
          )}
        </div>
      </div>

      <div className="px-6 pb-5 pt-2 flex flex-wrap items-center gap-4 text-xs text-[#57534E] border-t border-[#E5E7EB]/60">
        {location && (
          <span className="inline-flex items-center gap-1">
            <MapPin className="w-3.5 h-3.5 text-[#0D9488]" />
            {location}
          </span>
        )}
        {dateStr && (
          <span className="inline-flex items-center gap-1 ml-auto">
            <Calendar className="w-3.5 h-3.5" />
            {dateStr}
          </span>
        )}
      </div>
    </article>
  );
}

function CompactHorizontalCard({ post, isBookmarked, onToggleBookmark, onOpenPost }) {
  const dateStr = formatPublishedDate(post.published_at);
  const location = formatLocation(post);

  return (
    <article
      onClick={() => onOpenPost(post)}
      className="group bg-white border border-[#E5E7EB] rounded-2xl p-3.5 sm:p-4 flex items-stretch gap-4 hover:border-[#0D9488]/50 transition-all cursor-pointer"
    >
      <div className="w-28 sm:w-32 h-24 sm:h-28 rounded-xl overflow-hidden bg-[#FAF9F6] shrink-0">
        <CardImage
          post={post}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
        />
      </div>

      <div className="flex-1 min-w-0 flex flex-col justify-between py-0.5">
        <div>
          <div className="flex items-center justify-between gap-2 mb-1.5">
            {post.category ? (
              <span className="text-[11px] font-semibold uppercase tracking-wider text-[#0D9488] truncate">
                {post.category}
              </span>
            ) : (
              <span />
            )}
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onToggleBookmark(post);
              }}
              aria-label={isBookmarked ? 'Remove bookmark' : 'Bookmark story'}
              className="p-1 rounded-full hover:bg-[#FAF9F6] text-[#57534E] cursor-pointer shrink-0"
            >
              <Bookmark
                className={`w-4 h-4 ${
                  isBookmarked ? 'fill-[#0D9488] text-[#0D9488]' : 'text-[#57534E]'
                }`}
              />
            </button>
          </div>

          <h3 className="font-editorial text-base sm:text-lg font-bold text-[#1C1917] leading-snug line-clamp-2 group-hover:text-[#0D9488] transition-colors">
            {post.title}
          </h3>
        </div>

        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-[#57534E] mt-2">
          {location && (
            <span className="inline-flex items-center gap-1 truncate">
              <MapPin className="w-3 h-3 text-[#0D9488] shrink-0" />
              <span className="truncate">{location}</span>
            </span>
          )}
          {dateStr && (
            <span className="inline-flex items-center gap-1 shrink-0">
              <Calendar className="w-3 h-3" />
              {dateStr}
            </span>
          )}
        </div>
      </div>
    </article>
  );
}

export default function EditorialGrid({
  posts,
  isBookmarked,
  onToggleBookmark,
  onOpenPost,
}) {
  if (!posts || posts.length === 0) return null;

  // Group into balanced bento sections: 1 lead card + up to 3 compact horizontal cards,
  // then alternating standard / asymmetric rows so the grid stays varied.
  const leadFeatured = posts[0];
  const sideStack = posts.slice(1, 4);
  const remaining = posts.slice(4);

  return (
    <section aria-label="Editorial Stories" className="space-y-8">
      {/* Top Asymmetric Bento Block */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        <div className={sideStack.length > 0 ? 'lg:col-span-7' : 'lg:col-span-12'}>
          <LargeEditorialCard
            post={leadFeatured}
            isBookmarked={isBookmarked(leadFeatured.slug)}
            onToggleBookmark={onToggleBookmark}
            onOpenPost={onOpenPost}
          />
        </div>

        {sideStack.length > 0 && (
          <div className="lg:col-span-5 flex flex-col justify-between gap-4">
            {sideStack.map((item) => (
              <CompactHorizontalCard
                key={item.slug}
                post={item}
                isBookmarked={isBookmarked(item.slug)}
                onToggleBookmark={onToggleBookmark}
                onOpenPost={onOpenPost}
              />
            ))}
          </div>
        )}
      </div>

      {/* Remaining Editorial Mix */}
      {remaining.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {remaining.map((post, idx) =>
            idx % 5 === 0 ? (
              <div key={post.slug} className="md:col-span-2 lg:col-span-2">
                <LargeEditorialCard
                  post={post}
                  isBookmarked={isBookmarked(post.slug)}
                  onToggleBookmark={onToggleBookmark}
                  onOpenPost={onOpenPost}
                />
              </div>
            ) : (
              <div key={post.slug} className="md:col-span-1">
                <LargeEditorialCard
                  post={post}
                  isBookmarked={isBookmarked(post.slug)}
                  onToggleBookmark={onToggleBookmark}
                  onOpenPost={onOpenPost}
                />
              </div>
            )
          )}
        </div>
      )}
    </section>
  );
}
