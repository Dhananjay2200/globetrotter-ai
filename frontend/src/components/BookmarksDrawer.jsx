import React from 'react';
import { Bookmark, MapPin, Trash2, X } from 'lucide-react';
import { formatLocation, formatPublishedDate, getFallbackImageUrl } from '../utils/editorial';

export default function BookmarksDrawer({
  isOpen,
  bookmarks = [],
  onClose,
  onSelectPost,
  onRemoveBookmark,
}) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-[#1C1917]/40 backdrop-blur-xs">
      <div className="w-full max-w-md bg-[#FAF9F6] h-full border-l border-[#E5E7EB] flex flex-col shadow-xl">
        <div className="px-6 py-4 bg-white border-b border-[#E5E7EB] flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Bookmark className="w-5 h-5 text-[#0D9488]" />
            <h2 className="font-editorial text-xl font-bold text-[#1C1917]">
              Saved Stories ({bookmarks.length})
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close saved stories"
            className="p-1.5 rounded-full hover:bg-[#FAF9F6] text-[#57534E] hover:text-[#1C1917] cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-5 space-y-3">
          {bookmarks.length === 0 ? (
            <div className="text-center py-14 px-4 bg-white border border-[#E5E7EB] rounded-2xl">
              <Bookmark className="w-8 h-8 text-[#0D9488]/40 mx-auto mb-3" />
              <p className="font-editorial text-lg font-semibold text-[#1C1917] mb-1">
                No saved stories yet
              </p>
              <p className="text-sm text-[#57534E]">
                Tap the bookmark icon on any dispatch to save it for later reading.
              </p>
            </div>
          ) : (
            bookmarks.map((item) => {
              const loc = formatLocation(item);
              const dateStr = formatPublishedDate(item.published_at);
              const imgUrl =
                item.featured_image?.url ||
                getFallbackImageUrl(item.destination || item.title);

              return (
                <div
                  key={item.slug}
                  className="bg-white border border-[#E5E7EB] rounded-2xl p-3 flex gap-3.5 items-center hover:border-[#0D9488]/60 transition-colors"
                >
                  <img
                    src={imgUrl}
                    alt={item.title}
                    onClick={() => {
                      onSelectPost(item);
                      onClose();
                    }}
                    className="w-20 h-20 rounded-xl object-cover shrink-0 cursor-pointer"
                  />

                  <div
                    onClick={() => {
                      onSelectPost(item);
                      onClose();
                    }}
                    className="flex-1 min-w-0 cursor-pointer"
                  >
                    {item.category && (
                      <span className="text-[11px] font-semibold text-[#0D9488] block truncate">
                        {item.category}
                      </span>
                    )}
                    <h3 className="font-editorial text-sm font-bold text-[#1C1917] line-clamp-2 leading-snug mt-0.5">
                      {item.title}
                    </h3>
                    <div className="flex items-center gap-2 text-[11px] text-[#57534E] mt-1.5">
                      {loc && (
                        <span className="inline-flex items-center gap-1 truncate">
                          <MapPin className="w-3 h-3 text-[#0D9488]" />
                          {loc}
                        </span>
                      )}
                      {dateStr && <span className="shrink-0">· {dateStr}</span>}
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() => onRemoveBookmark(item)}
                    aria-label="Remove bookmark"
                    className="p-2 rounded-full text-[#57534E] hover:text-red-600 hover:bg-red-50 transition-colors cursor-pointer shrink-0"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
