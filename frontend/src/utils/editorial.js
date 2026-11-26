/**
 * World Tourist - Editorial Formatting & Fallback Utilities.
 * Maps strictly to real backend fields and computes safe fallbacks when optional data is missing.
 */

/**
 * Formats ISO date string into an editorial magazine date (e.g., "Nov 24, 2026").
 * Returns null if no valid date exists so components can gracefully hide it.
 */
export function formatPublishedDate(isoString) {
  if (!isoString) return null;
  const parsed = new Date(isoString);
  if (Number.isNaN(parsed.getTime())) return null;
  return parsed.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

/**
 * Computes estimated read time from word_count (or body_markdown length).
 * Returns null if neither field has content.
 */
export function computeReadTime(post) {
  if (!post) return null;
  let words = Number(post.word_count) || 0;
  if (!words && post.body_markdown) {
    words = post.body_markdown.trim().split(/\s+/).filter(Boolean).length;
  }
  if (words <= 0) return null;
  const mins = Math.max(1, Math.ceil(words / 200));
  return `${mins} min read`;
}

/**
 * Extracts a clean plain-text excerpt from summary, seo.description, or body_markdown.
 */
export function getExcerpt(post, maxLength = 165) {
  if (!post) return '';
  const raw =
    post.summary ||
    post.seo?.description ||
    post.unique_angle ||
    (post.body_markdown
      ? post.body_markdown
          .replace(/^#+\s+.*$/gm, '')
          .replace(/[*_`>#[\]()!-]/g, ' ')
          .replace(/\s+/g, ' ')
          .trim()
      : '');

  if (!raw) return '';
  if (raw.length <= maxLength) return raw;
  return `${raw.slice(0, maxLength).trimEnd()}…`;
}

/**
 * Builds a compact location string ("Destination, Country") from real fields.
 */
export function formatLocation(post) {
  if (!post) return null;
  const parts = [post.destination, post.country].filter(
    (v) => typeof v === 'string' && v.trim().length > 0
  );
  if (parts.length === 0) return null;
  // Avoid repeating if destination === country
  if (parts.length === 2 && parts[0].toLowerCase() === parts[1].toLowerCase()) {
    return parts[0];
  }
  return parts.join(', ');
}

/**
 * Generates a crisp warm-alabaster & ocean-teal inline SVG fallback placeholder
 * when featured_image.url is absent or fails to load.
 */
export function getFallbackImageUrl(label = 'World Tourist') {
  const safeText = String(label || 'World Tourist')
    .slice(0, 32)
    .replace(/[<>&"']/g, '');

  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800">
      <defs>
        <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#0F766E" />
          <stop offset="55%" stop-color="#115E59" />
          <stop offset="100%" stop-color="#1C1917" />
        </linearGradient>
      </defs>
      <rect width="1200" height="800" fill="url(#bg)" />
      <circle cx="960" cy="180" r="220" fill="#14B8A6" fill-opacity="0.12" />
      <circle cx="220" cy="650" r="260" fill="#FAF9F6" fill-opacity="0.06" />
      <path d="M0 640 Q 320 520 620 610 T 1200 560 L 1200 800 L 0 800 Z" fill="#1C1917" fill-opacity="0.35" />
      <text x="600" y="385" text-anchor="middle" fill="#FAF9F6" fill-opacity="0.92" font-family="Georgia, serif" font-size="44" font-weight="600">${safeText}</text>
      <text x="600" y="438" text-anchor="middle" fill="#CCFBF1" fill-opacity="0.75" font-family="sans-serif" font-size="20" letter-spacing="4">WORLD TOURIST DISPATCH</text>
    </svg>
  `.trim();

  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
}
