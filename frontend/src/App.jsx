import React, { useState, useEffect } from 'react';
import UserBlogPortal from './views/UserBlogPortal';
import AdminPortal from './views/AdminPortal';
import BlogPostModal from './components/BlogPostModal';
import { api } from './services/api';

export default function App() {
  // Determine initial portal based on URL hash or path
  const [portal, setPortal] = useState(() => {
    const hash = window.location.hash.toLowerCase();
    const path = window.location.pathname.toLowerCase();
    const search = window.location.search.toLowerCase();
    if (hash === '#admin' || path.includes('/admin') || search.includes('portal=admin')) {
      return 'admin';
    }
    return 'user';
  });

  const [posts, setPosts] = useState([]);
  const [selectedPost, setSelectedPost] = useState(null);
  const [loading, setLoading] = useState(true);

  // Synchronize hash routing
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.toLowerCase();
      if (hash === '#admin') {
        setPortal('admin');
      } else {
        setPortal('user');
        loadFeed();
      }
    };

    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const loadFeed = async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      const data = await api.getFeed(null, null, 100);
      setPosts(data.posts || []);
    } catch (err) {
      console.error('Failed to load blog feed:', err);
    } finally {
      if (!silent) setLoading(false);
    }
  };

  useEffect(() => {
    loadFeed();
    // Silently poll for newly published articles every 3 seconds
    const interval = setInterval(() => {
      loadFeed(true);
    }, 3000);

    // Refresh immediately when window gains focus or tab becomes active
    const handleFocus = () => {
      if (document.visibilityState === 'visible') {
        loadFeed(true);
      }
    };
    window.addEventListener('focus', handleFocus);
    document.addEventListener('visibilitychange', handleFocus);

    return () => {
      clearInterval(interval);
      window.removeEventListener('focus', handleFocus);
      document.removeEventListener('visibilitychange', handleFocus);
    };
  }, []);

  const switchToAdmin = () => {
    setPortal('admin');
    window.location.hash = '#admin';
  };

  const switchToUser = () => {
    setPortal('user');
    window.location.hash = '#stories';
    loadFeed();
  };

  // Handle article selection from either Admin table or User feed
  const handleSelectArticleFromDashboard = async (article) => {
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
          featured_image: detail.images?.[0] ? {
            url: detail.images[0].image_url,
            alt_text: detail.images[0].alt_text,
            attribution: detail.images[0].attribution,
            license: detail.images[0].license_name,
          } : null,
          gallery_images: detail.images?.slice(1).map(img => ({
            url: img.image_url,
            alt_text: img.alt_text,
            attribution: img.attribution,
            license: img.license_name,
          })) || [],
          citations: detail.sources?.map(s => ({
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

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Dynamic View: Mobile-Optimized User Frontend OR Full-Control Admin Frontend */}
      {portal === 'admin' ? (
        <AdminPortal
          onSelectArticle={handleSelectArticleFromDashboard}
          onExitToUserPortal={switchToUser}
        />
      ) : (
        <UserBlogPortal
          posts={posts}
          loading={loading}
          onSelectPost={setSelectedPost}
          onRefresh={loadFeed}
          onSwitchToAdmin={switchToAdmin}
        />
      )}

      {/* Full Article Reader Modal (Optimized for Mobile Screens & Full-Screen) */}
      {selectedPost && (
        <BlogPostModal
          post={selectedPost}
          onClose={() => setSelectedPost(null)}
        />
      )}
    </div>
  );
}
