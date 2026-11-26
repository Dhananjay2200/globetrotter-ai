import React from 'react';

/**
 * Renders inline markdown formatting: **bold**, *italic*, and [label](url).
 */
function renderInline(text) {
  if (!text) return null;
  const tokens = [];
  const pattern = /(\*\*[^*]+\*\*|\*[^*]+\*|\[[^\]]+\]\([^)]+\))/g;
  let lastIndex = 0;
  let match;
  let keyIdx = 0;

  while ((match = pattern.exec(text)) !== null) {
    if (match.index > lastIndex) {
      tokens.push(text.slice(lastIndex, match.index));
    }
    const token = match[0];
    if (token.startsWith('**') && token.endsWith('**')) {
      tokens.push(
        <strong key={`b-${keyIdx++}`} className="font-semibold text-[#1C1917]">
          {token.slice(2, -2)}
        </strong>
      );
    } else if (token.startsWith('*') && token.endsWith('*')) {
      tokens.push(
        <em key={`i-${keyIdx++}`} className="italic">
          {token.slice(1, -1)}
        </em>
      );
    } else if (token.startsWith('[')) {
      const linkMatch = /^\[([^\]]+)\]\(([^)]+)\)$/.exec(token);
      if (linkMatch) {
        tokens.push(
          <a
            key={`a-${keyIdx++}`}
            href={linkMatch[2]}
            target="_blank"
            rel="noopener noreferrer"
            className="text-[#0D9488] underline decoration-[#0D9488]/40 underline-offset-4 hover:text-[#0F766E] transition-colors"
          >
            {linkMatch[1]}
          </a>
        );
      } else {
        tokens.push(token);
      }
    }
    lastIndex = pattern.lastIndex;
  }

  if (lastIndex < text.length) {
    tokens.push(text.slice(lastIndex));
  }
  return tokens;
}

/**
 * Editorial Markdown Renderer for Article Detail view.
 */
export default function MarkdownArticle({ markdown }) {
  if (!markdown) return null;

  const lines = markdown.split('\n');
  const blocks = [];
  let paragraphBuffer = [];
  let listBuffer = [];
  let listOrdered = false;
  let skippingSourcesSection = false;

  const flushParagraph = (key) => {
    if (paragraphBuffer.length > 0) {
      blocks.push(
        <p key={`p-${key}`} className="text-[#1C1917]/90 text-base sm:text-[17px] leading-relaxed mb-5">
          {renderInline(paragraphBuffer.join(' '))}
        </p>
      );
      paragraphBuffer = [];
    }
  };

  const flushList = (key) => {
    if (listBuffer.length > 0) {
      const ListTag = listOrdered ? 'ol' : 'ul';
      const listClass = listOrdered
        ? 'list-decimal ml-6 mb-6 space-y-2 text-[#1C1917]/90 text-base sm:text-[17px] leading-relaxed'
        : 'list-disc ml-6 mb-6 space-y-2 text-[#1C1917]/90 text-base sm:text-[17px] leading-relaxed marker:text-[#0D9488]';

      blocks.push(
        <ListTag key={`list-${key}`} className={listClass}>
          {listBuffer.map((item, idx) => (
            <li key={`li-${key}-${idx}`}>{renderInline(item)}</li>
          ))}
        </ListTag>
      );
      listBuffer = [];
    }
  };

  lines.forEach((rawLine, idx) => {
    const line = rawLine.trim();

    if (!line) {
      flushParagraph(idx);
      flushList(idx);
      return;
    }

    if (line.startsWith('# ')) {
      flushParagraph(idx);
      flushList(idx);
      // H1 title is already displayed in the article header
      return;
    }

    if (line.startsWith('## ')) {
      flushParagraph(idx);
      flushList(idx);
      const headingText = line.slice(3).trim();
      if (/^(sources(\s+(&|and)\s+references)?|references)$/i.test(headingText)) {
        skippingSourcesSection = true;
        return;
      }
      skippingSourcesSection = false;
      blocks.push(
        <h2
          key={`h2-${idx}`}
          className="font-editorial text-2xl sm:text-[28px] font-bold text-[#1C1917] mt-10 mb-4 pb-2 border-b border-[#E5E7EB] leading-snug"
        >
          {headingText}
        </h2>
      );
      return;
    }

    if (skippingSourcesSection) {
      return;
    }

    if (line.startsWith('### ')) {
      flushParagraph(idx);
      flushList(idx);
      blocks.push(
        <h3
          key={`h3-${idx}`}
          className="font-editorial text-xl font-semibold text-[#1C1917] mt-7 mb-3 leading-snug"
        >
          {line.slice(4)}
        </h3>
      );
      return;
    }

    if (line.startsWith('> ')) {
      flushParagraph(idx);
      flushList(idx);
      blocks.push(
        <blockquote
          key={`bq-${idx}`}
          className="border-l-4 border-[#0D9488] bg-white px-5 py-4 my-6 rounded-r-xl border-y border-r border-[#E5E7EB] text-[#57534E] italic text-base sm:text-lg leading-relaxed"
        >
          {renderInline(line.slice(2))}
        </blockquote>
      );
      return;
    }

    const unorderedMatch = /^[-*]\s+(.+)$/.exec(line);
    if (unorderedMatch) {
      flushParagraph(idx);
      if (listBuffer.length > 0 && listOrdered) flushList(idx);
      listOrdered = false;
      listBuffer.push(unorderedMatch[1]);
      return;
    }

    const orderedMatch = /^\d+\.\s+(.+)$/.exec(line);
    if (orderedMatch) {
      flushParagraph(idx);
      if (listBuffer.length > 0 && !listOrdered) flushList(idx);
      listOrdered = true;
      listBuffer.push(orderedMatch[1]);
      return;
    }

    flushList(idx);
    paragraphBuffer.push(line);
  });

  flushParagraph(lines.length);
  flushList(lines.length);

  return <div className="editorial-prose">{blocks}</div>;
}
