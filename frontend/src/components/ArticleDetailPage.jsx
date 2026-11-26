import React, { useEffect, useState } from 'react';
import {
  ArrowLeft,
  Bookmark,
  Calendar,
  Clock,
  Globe2,
  MapPin,
  Tag,
} from 'lucide-react';
import MarkdownArticle from './MarkdownArticle';
import {
  computeReadTime,
  formatLocation,
  formatPublishedDate,
  getFallbackImageUrl,
} from '../utils/editorial';

export default function ArticleDetailPage({
  post,
  relatedPosts = [],
  isBookmarked,
  onToggleBookmark,
  onBack,
  onOpenPost,
}) {
  const [scrollProgress, setScrollProgress] = useState(0);
  const [failedUrl, setFailedUrl] = useState(null);

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'instant' });
  }, [post?.slug]);

  useEffect(() => {
    const updateProgress = () => {
      const doc = document.documentElement;
      const totalScrollable = doc.scrollHeight - window.innerHeight;
      if (totalScrollable <= 0) {
        setScrollProgress(0);
        return;
      }
      const pct = Math.min(100, Math.max(0, (window.scrollY / totalScrollable) * 100));
      setScrollProgress(pct);
    };

    updateProgress();
    window.addEventListener('scroll', updateProgress, { passive: true });
    return () => window.removeEventListener('scroll', updateProgress);
  }, [post?.slug]);

  if (!post) return null;

  const location = formatLocation(post);
  const dateStr = formatPublishedDate(post.published_at);
  const readTime = computeReadTime(post);
  const coverFailed = Boolean(post.featured_image?.url && failedUrl === post.featured_image.url);
  const coverSrc =
    !coverFailed && post.featured_image?.url
      ? post.featured_image.url
      : getFallbackImageUrl(post.destination || post.title);

  // Quick Facts strip strictly built from non-empty backend fields
  const quickFacts = [
    location && { icon: MapPin, label: 'Destination', value: location },
    post.region && { icon: Globe2, label: 'Region', value: post.region },
    post.category && { icon: Tag, label: 'Category', value: post.category },
    readTime && { icon: Clock, label: 'Reading Time', value: readTime },
  ].filter(Boolean);

  return (
    <div className="min-h-screen bg-[#FAF9F6]">
      {/* Reading Progress Bar pinned at the top of the viewport */}
      <div className="fixed top-0 left-0 right-0 h-1 bg-[#E5E7EB]/60 z-50">
        <div
          className="h-full bg-[#0D9488] transition-[width] duration-75"
          style={{ width: `${scrollProgress}%` }}
        />
      </div>

      {/* Article Top Bar */}
      <div className="sticky top-0 z-40 bg-[#FAF9F6]/95 backdrop-blur-md border-b border-[#E5E7EB]">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between gap-4">
          <button
            type="button"
            onClick={onBack}
            className="inline-flex items-center gap-2 text-sm font-semibold text-[#1C1917] hover:text-[#0D9488] transition-colors cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to World Tourist
          </button>

          <button
            type="button"
            onClick={() => onToggleBookmark(post)}
            className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white border border-[#E5E7EB] text-xs font-semibold text-[#1C1917] hover:border-[#0D9488] transition-colors cursor-pointer"
          >
            <Bookmark
              className={`w-3.5 h-3.5 ${
                isBookmarked ? 'fill-[#0D9488] text-[#0D9488]' : 'text-[#57534E]'
              }`}
            />
            {isBookmarked ? 'Saved' : 'Save Story'}
          </button>
        </div>
      </div>

      {/* Centered Editorial Reading Column */}
      <article className="max-w-3xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
        {/* Story Category & Headline */}
        <header className="mb-8">
          <div className="flex flex-wrap items-center gap-2.5 mb-4">
            {post.category && (
              <span className="px-3 py-1 rounded-full bg-[#0D9488] text-white text-xs font-semibold">
                {post.category}
              </span>
            )}
            {dateStr && (
              <span className="inline-flex items-center gap-1.5 text-xs text-[#57534E] font-medium">
                <Calendar className="w-3.5 h-3.5" />
                {dateStr}
              </span>
            )}
          </div>

          <h1 className="font-editorial text-3xl sm:text-5xl font-bold text-[#1C1917] leading-[1.15] mb-4">
            {post.title}
          </h1>

          {(post.summary || post.seo?.description) && (
            <p className="text-lg sm:text-xl text-[#57534E] leading-relaxed">
              {post.summary || post.seo?.description}
            </p>
          )}
        </header>

        {/* Optional Quick Facts Strip */}
        {quickFacts.length > 0 && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-white border border-[#E5E7EB] rounded-2xl p-4 mb-8">
            {quickFacts.map((fact) => {
              const Icon = fact.icon;
              return (
                <div key={fact.label} className="min-w-0">
                  <div className="flex items-center gap-1.5 text-[11px] uppercase tracking-wider text-[#57534E] font-semibold mb-1">
                    <Icon className="w-3.5 h-3.5 text-[#0D9488] shrink-0" />
                    <span className="truncate">{fact.label}</span>
                  </div>
                  <div className="text-xs sm:text-sm font-semibold text-[#1C1917] truncate">
                    {fact.value}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Large Cover Photo */}
        <figure className="mb-10">
          <div className="w-full h-[260px] sm:h-[420px] rounded-2xl overflow-hidden border border-[#E5E7EB] bg-white">
            <img
              src={coverSrc}
              alt={post.featured_image?.alt_text || post.title}
              onError={() => setFailedUrl(post.featured_image?.url || '__fallback__')}
              className="w-full h-full object-cover"
            />
          </div>
          {(post.featured_image?.attribution || post.featured_image?.license) && (
            <figcaption className="text-xs text-[#57534E] mt-2.5 flex flex-wrap justify-between gap-2">
              <span>{post.featured_image.alt_text}</span>
              <span>
                {[post.featured_image.attribution, post.featured_image.license]
                  .filter(Boolean)
                  .join(' · ')}
              </span>
            </figcaption>
          )}
        </figure>

        {/* Body Prose */}
        <div className="leading-relaxed">
          <MarkdownArticle markdown={post.body_markdown} />
        </div>

        {/* Optional Gallery */}
        {Array.isArray(post.gallery_images) && post.gallery_images.length > 0 && (
          <section className="mt-12 pt-8 border-t border-[#E5E7EB]">
            <h2 className="font-editorial text-2xl font-bold text-[#1C1917] mb-4">
              Destination Gallery
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {post.gallery_images.map((img, i) => (
                <figure
                  key={`${img.url}-${i}`}
                  className="bg-white border border-[#E5E7EB] rounded-2xl overflow-hidden"
                >
                  <img
                    src={img.url}
                    alt={img.alt_text || post.destination || 'Gallery view'}
                    loading="lazy"
                    className="w-full h-48 object-cover"
                  />
                  {(img.alt_text || img.attribution) && (
                    <figcaption className="p-3 text-xs text-[#57534E]">
                      {img.alt_text || img.attribution}
                    </figcaption>
                  )}
                </figure>
              ))}
            </div>
          </section>
        )}
      </article>

      {/* Related Stories Section */}
      {relatedPosts.length > 0 && (
        <section className="border-t border-[#E5E7EB] bg-white py-12">
          <div className="max-w-5xl mx-auto px-4 sm:px-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="font-editorial text-2xl sm:text-3xl font-bold text-[#1C1917]">
                Related Stories
              </h2>
              <button
                type="button"
                onClick={onBack}
                className="text-sm font-semibold text-[#0D9488] hover:underline cursor-pointer"
              >
                Explore all stories
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
              {relatedPosts.map((item) => {
                const relImg =
                  item.featured_image?.url ||
                  getFallbackImageUrl(item.destination || item.title);
                const relDate = formatPublishedDate(item.published_at);

                return (
                  <article
                    key={item.slug}
                    onClick={() => onOpenPost(item)}
                    className="group bg-[#FAF9F6] border border-[#E5E7EB] rounded-2xl overflow-hidden hover:border-[#0D9488]/60 transition-colors cursor-pointer flex flex-col"
                  >
                    <div className="h-40 overflow-hidden bg-[#E5E7EB]/40">
                      <img
                        src={relImg}
                        alt={item.featured_image?.alt_text || item.title}
                        loading="lazy"
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                      />
                    </div>
                    <div className="p-4 flex-1 flex flex-col justify-between">
                      <div>
                        {item.category && (
                          <span className="text-[11px] font-semibold uppercase tracking-wider text-[#0D9488] block mb-1.5">
                            {item.category}
                          </span>
                        )}
                        <h3 className="font-editorial text-base font-bold text-[#1C1917] leading-snug line-clamp-2 group-hover:text-[#0D9488] transition-colors">
                          {item.title}
                        </h3>
                      </div>
                      {relDate && (
                        <span className="text-xs text-[#57534E] mt-3 block">
                          {relDate}
                        </span>
                      )}
                    </div>
                  </article>
                );
              })}
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
