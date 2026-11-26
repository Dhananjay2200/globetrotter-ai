import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { api } from './services/api';
import AdminPortal from './views/AdminPortal';
import Header from './components/Header';
import HeroSection from './components/HeroSection';
import EditorialGrid from './components/EditorialGrid';
import ArticleDetailPage from './components/ArticleDetailPage';
import BookmarksDrawer from './components/BookmarksDrawer';
import {
  EmptyState,
  ErrorBanner,
  GridSkeleton,
  HeroSkeleton,
} from './components/States';

const BOOKMARKS_KEY = 'world_tourist_bookmarks';

function isAdminLocation() {
  const hash = window.location.hash.toLowerCase();
  const path = window.location.pathname.toLowerCase();
  const search = window.location.search.toLowerCase();
  return (
    path === '/admin' ||
    path.endsWith('/admin') ||
    path.includes('/admin/') ||
    hash === '#admin' ||
    search.includes('portal=admin')
  );
}

function loadSavedBookmarks() {
  try {
    const raw = localStorage.getItem(BOOKMARKS_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export default function App() {
  const [portal, setPortal] = useState(() => (isAdminLocation() ? 'admin' : 'user'));
  const [posts, setPosts] = useState([]);
  const [metadata, setMetadata] = useState({ regions: [], categories: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filter & Search States
  const [searchQuery, setSearchQuery] = useState('');
  const [filterMode, setFilterMode] = useState('regions'); // 'regions' | 'categories'
  const [activeRegion, setActiveRegion] = useState('All');
  const [activeCategory, setActiveCategory] = useState('All');

  // Detail View & Bookmarks States
  const [selectedPost, setSelectedPost] = useState(null);
  const [bookmarks, setBookmarks] = useState(loadSavedBookmarks);
  const [bookmarksOpen, setBookmarksOpen] = useState(false);

  const fetchAndSyncContent = useCallback(async () => {
    const [feedData, metaData] = await Promise.all([
      api.getFeed({ limit: 150, offset: 0 }),
      api.getMetadata().catch(() => null),
    ]);

    const fetchedPosts = Array.isArray(feedData?.posts) ? feedData.posts : [];
    const apiRegions = Array.isArray(metaData?.global_regions) ? metaData.global_regions : [];
    const apiCategories = Array.isArray(metaData?.tourism_categories)
      ? metaData.tourism_categories
      : [];

    const postRegions = Array.from(
      new Set(fetchedPosts.map((p) => p.region).filter(Boolean))
    );
    const postCategories = Array.from(
      new Set(fetchedPosts.map((p) => p.category).filter(Boolean))
    );

    return {
      fetchedPosts,
      regions: apiRegions.length > 0 ? apiRegions : postRegions,
      categories: apiCategories.length > 0 ? apiCategories : postCategories,
    };
  }, []);

  const loadContent = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchAndSyncContent();
      setPosts(data.fetchedPosts);
      setMetadata({ regions: data.regions, categories: data.categories });
    } catch (err) {
      setError(err?.message || 'Unable to connect to the backend service.');
    } finally {
      setLoading(false);
    }
  }, [fetchAndSyncContent]);

  useEffect(() => {
    let active = true;
    fetchAndSyncContent()
      .then((data) => {
        if (!active) return;
        setPosts(data.fetchedPosts);
        setMetadata({ regions: data.regions, categories: data.categories });
        setError(null);
      })
      .catch((err) => {
        if (!active) return;
        setError(err?.message || 'Unable to connect to the backend service.');
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [fetchAndSyncContent]);

  // Sync URL navigation (/admin, #admin, #post/<slug>)
  useEffect(() => {
    const syncFromUrl = async () => {
      if (isAdminLocation()) {
        setPortal('admin');
        return;
      }

      setPortal('user');
      const hash = window.location.hash;
      if (hash.startsWith('#post/')) {
        const slug = decodeURIComponent(hash.slice('#post/'.length));
        const localMatch = posts.find((p) => p.slug === slug);
        if (localMatch) {
          setSelectedPost(localMatch);
          return;
        }
        try {
          const singlePost = await api.getPostBySlug(slug);
          setSelectedPost(singlePost);
        } catch {
          setSelectedPost(null);
        }
      } else {
        setSelectedPost(null);
      }
    };

    syncFromUrl();
    window.addEventListener('hashchange', syncFromUrl);
    window.addEventListener('popstate', syncFromUrl);
    return () => {
      window.removeEventListener('hashchange', syncFromUrl);
      window.removeEventListener('popstate', syncFromUrl);
    };
  }, [posts]);

  // Exit from Admin back to World Tourist public portal
  const exitToUserPortal = () => {
    setPortal('user');
    setSelectedPost(null);
    const targetPath = window.location.pathname.toLowerCase().includes('/admin')
      ? '/'
      : window.location.pathname;
    window.history.pushState('', document.title, targetPath);
    loadContent();
  };

  // Preview or open article triggered from AdminPortal
  const handleSelectArticleFromAdmin = async (article) => {
    try {
      if (article.status === 'published' && article.slug) {
        const fullPost = await api.getPostBySlug(article.slug);
        setSelectedPost(fullPost);
      } else {
        const detail = await api.getArticleDetail(article.id);
        setSelectedPost({
          id: detail.id,
          title: detail.title,
          slug: detail.slug,
          destination: detail.destination || 'Global',
          country: detail.country || 'World',
          category: detail.category || 'Travel Guide',
          summary: detail.summary,
          body_markdown: detail.body_markdown,
          word_count: detail.word_count,
          quality_score: detail.quality_score,
          featured_image: detail.images?.[0]
            ? {
                url: detail.images[0].image_url,
                alt_text: detail.images[0].alt_text,
                attribution: detail.images[0].attribution,
                license: detail.images[0].license_name,
              }
            : null,
          gallery_images:
            detail.images?.slice(1).map((img) => ({
              url: img.image_url,
              alt_text: img.alt_text,
              attribution: img.attribution,
              license: img.license_name,
            })) || [],
          citations:
            detail.sources?.map((s) => ({
              title: s.title,
              publisher: s.publisher,
              url: s.url,
            })) || [],
          seo: {
            title: detail.seo_title,
            description: detail.seo_description,
            main_keyword: detail.main_keyword,
          },
          website_url: `/blog/${detail.slug}`,
        });
      }
    } catch (err) {
      console.error('Failed to load article detail:', err);
    }
  };

  // Client-side bookmark persistence in localStorage
  const toggleBookmark = useCallback((post) => {
    if (!post?.slug) return;
    setBookmarks((prev) => {
      const exists = prev.some((b) => b.slug === post.slug);
      const next = exists
        ? prev.filter((b) => b.slug !== post.slug)
        : [post, ...prev];
      try {
        localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(next));
      } catch {
        // Ignore storage quota errors
      }
      return next;
    });
  }, []);

  const isBookmarked = useCallback(
    (slug) => bookmarks.some((b) => b.slug === slug),
    [bookmarks]
  );

  // Filter stories by region, category, and search query
  const filteredPosts = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    return posts.filter((post) => {
      if (activeRegion !== 'All' && post.region !== activeRegion) {
        return false;
      }
      if (activeCategory !== 'All' && post.category !== activeCategory) {
        return false;
      }
      if (!q) return true;
      const haystack = [
        post.title,
        post.destination,
        post.country,
        post.region,
        post.category,
        post.summary,
        post.unique_angle,
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();
      return haystack.includes(q);
    });
  }, [posts, activeRegion, activeCategory, searchQuery]);

  const handleOpenPost = async (post) => {
    if (!post?.slug) return;
    setSelectedPost(post);
    window.location.hash = `post/${encodeURIComponent(post.slug)}`;

    try {
      const fresh = await api.getPostBySlug(post.slug);
      if (fresh?.slug === post.slug) {
        setSelectedPost(fresh);
      }
    } catch {
      // Already displaying feed post cleanly
    }
  };

  const handleClosePost = () => {
    setSelectedPost(null);
    if (window.location.hash.startsWith('#post/')) {
      window.history.pushState('', document.title, window.location.pathname + window.location.search);
    }
  };

  const handleResetFilters = () => {
    setSearchQuery('');
    setActiveRegion('All');
    setActiveCategory('All');
  };

  const relatedPosts = useMemo(() => {
    if (!selectedPost) return [];
    return posts
      .filter((p) => p.slug !== selectedPost.slug)
      .sort((a, b) => {
        const aScore =
          (a.region === selectedPost.region ? 2 : 0) +
          (a.category === selectedPost.category ? 1 : 0);
        const bScore =
          (b.region === selectedPost.region ? 2 : 0) +
          (b.category === selectedPost.category ? 1 : 0);
        return bScore - aScore;
      })
      .slice(0, 3);
  }, [posts, selectedPost]);

  // Article Detail View (accessible both from World Tourist feed and Admin preview)
  if (selectedPost) {
    return (
      <>
        <ArticleDetailPage
          post={selectedPost}
          relatedPosts={relatedPosts}
          isBookmarked={isBookmarked(selectedPost.slug)}
          onToggleBookmark={toggleBookmark}
          onBack={handleClosePost}
          onOpenPost={handleOpenPost}
        />
        <BookmarksDrawer
          isOpen={bookmarksOpen}
          bookmarks={bookmarks}
          onClose={() => setBookmarksOpen(false)}
          onSelectPost={handleOpenPost}
          onRemoveBookmark={toggleBookmark}
        />
      </>
    );
  }

  // Hidden Admin View (reachable directly via /admin or #admin URL)
  if (portal === 'admin') {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100">
        <AdminPortal
          onSelectArticle={handleSelectArticleFromAdmin}
          onExitToUserPortal={exitToUserPortal}
        />
      </div>
    );
  }

  const heroPost = filteredPosts[0] || null;
  const gridPosts = filteredPosts.slice(1);

  return (
    <div className="min-h-screen bg-[#FAF9F6] text-[#1C1917] flex flex-col">
      <Header
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        regions={metadata.regions}
        categories={metadata.categories}
        activeRegion={activeRegion}
        onSelectRegion={setActiveRegion}
        activeCategory={activeCategory}
        onSelectCategory={setActiveCategory}
        bookmarkCount={bookmarks.length}
        onOpenBookmarks={() => setBookmarksOpen(true)}
        onGoHome={handleResetFilters}
        filterMode={filterMode}
        onFilterModeChange={setFilterMode}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10">
        {error && (
          <div className="mb-8">
            <ErrorBanner message={error} onRetry={loadContent} />
          </div>
        )}

        {loading ? (
          <div className="space-y-8">
            <HeroSkeleton />
            <GridSkeleton />
          </div>
        ) : filteredPosts.length === 0 ? (
          <EmptyState
            searchQuery={searchQuery}
            activeRegion={activeRegion}
            activeCategory={activeCategory}
            onReset={handleResetFilters}
          />
        ) : (
          <>
            <HeroSection
              post={heroPost}
              isBookmarked={isBookmarked(heroPost?.slug)}
              onToggleBookmark={toggleBookmark}
              onOpenPost={handleOpenPost}
            />

            {gridPosts.length > 0 && (
              <>
                <div className="flex items-baseline justify-between mb-6 pb-3 border-b border-[#E5E7EB]">
                  <h2 className="font-editorial text-2xl sm:text-3xl font-bold text-[#1C1917]">
                    Latest Dispatches
                  </h2>
                  <span className="text-xs sm:text-sm text-[#57534E]">
                    Showing {filteredPosts.length}{' '}
                    {filteredPosts.length === 1 ? 'story' : 'stories'}
                  </span>
                </div>

                <EditorialGrid
                  posts={gridPosts}
                  isBookmarked={isBookmarked}
                  onToggleBookmark={toggleBookmark}
                  onOpenPost={handleOpenPost}
                />
              </>
            )}
          </>
        )}
      </main>

      <footer className="border-t border-[#E5E7EB] bg-white py-8 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-[#57534E]">
          <span className="font-editorial text-base font-bold text-[#1C1917]">
            World Tourist
          </span>
          <span>Global Destination Journalism &amp; Cultural Travel Guides</span>
        </div>
      </footer>

      <BookmarksDrawer
        isOpen={bookmarksOpen}
        bookmarks={bookmarks}
        onClose={() => setBookmarksOpen(false)}
        onSelectPost={handleOpenPost}
        onRemoveBookmark={toggleBookmark}
      />
    </div>
  );
}
