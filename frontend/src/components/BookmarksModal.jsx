import React from 'react';
import { X, Bookmark, Trash2, ArrowRight, MapPin } from 'lucide-react';

export default function BookmarksModal({ 
  bookmarks = [], 
  onClose, 
  onSelectPost, 
  onRemoveBookmark 
}) {
  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-950/85 backdrop-blur-md flex justify-center items-center p-3 sm:p-6 animate-fadeIn">
      <div className="relative bg-slate-900 border border-slate-800 rounded-3xl max-w-xl w-full shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
        
        {/* Header */}
        <div className="p-5 sm:p-6 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-xl bg-teal-500/20 text-teal-400 border border-teal-500/30">
              <Bookmark className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Saved Travel Stories</h3>
              <p className="text-xs text-slate-400">
                {bookmarks.length} {bookmarks.length === 1 ? 'guide' : 'guides'} saved for offline reading
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-full bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Bookmarks List */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-3">
          {bookmarks.length === 0 ? (
            <div className="py-12 text-center space-y-3">
              <div className="w-14 h-14 mx-auto rounded-2xl bg-slate-800/80 flex items-center justify-center text-slate-500">
                <Bookmark className="w-7 h-7" />
              </div>
              <p className="text-sm font-semibold text-slate-300">No saved stories yet</p>
              <p className="text-xs text-slate-500 max-w-xs mx-auto">
                Tap the bookmark icon on any travel guide to save it for reading later on your phone or computer.
              </p>
            </div>
          ) : (
            bookmarks.map(post => (
              <div
                key={post.slug || post.id}
                className="group p-3 sm:p-4 rounded-2xl bg-slate-950/70 border border-slate-800/90 hover:border-teal-500/40 transition-all flex items-center justify-between gap-3"
              >
                <div 
                  className="flex items-center space-x-3.5 flex-1 min-w-0 cursor-pointer"
                  onClick={() => {
                    onSelectPost(post);
                    onClose();
                  }}
                >
                  {post.featured_image?.url && (
                    <img
                      src={post.featured_image.url}
                      alt={post.title}
                      className="w-16 h-16 rounded-xl object-cover flex-shrink-0"
                    />
                  )}
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center space-x-1.5 text-[11px] text-teal-400 mb-1">
                      <MapPin className="w-3 h-3" />
                      <span className="truncate">{post.destination}, {post.country}</span>
                    </div>
                    <h4 className="text-sm font-bold text-white group-hover:text-teal-300 transition-colors line-clamp-1">
                      {post.title}
                    </h4>
                    <p className="text-[11px] text-slate-400 line-clamp-1 mt-0.5">
                      {post.summary}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => onRemoveBookmark(post.slug || post.id)}
                    className="p-2 rounded-xl text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                    title="Remove from saved"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>

                  <button
                    onClick={() => {
                      onSelectPost(post);
                      onClose();
                    }}
                    className="p-2 rounded-xl bg-teal-500/20 text-teal-300 hover:bg-teal-500 hover:text-slate-950 transition-colors"
                    title="Read"
                  >
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        {bookmarks.length > 0 && (
          <div className="p-4 border-t border-slate-800/80 bg-slate-950/50 text-center text-xs text-slate-500">
            Stories are saved locally in your browser memory for fast instant access.
          </div>
        )}
      </div>
    </div>
  );
}
