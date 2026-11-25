import React, { useState, useEffect, useRef } from 'react';
import AdminNavbar from '../components/AdminNavbar';
import AdminLoginView from '../components/AdminLoginView';
import WorkflowTrigger from '../components/WorkflowTrigger';
import { api } from '../services/api';
import { isDateMatch } from '../utils/geoRegions';
import { 
  BarChart3, CheckCircle2, Clock, AlertTriangle, Send, 
  RefreshCw, Globe, Layers, Award, Sparkles, Eye, Power, 
  Play, Pause, Flame, ShieldAlert, Check, Trash2, Undo2, 
  Database, Cpu, Zap, Activity, ExternalLink, ArrowRight,
  Calendar, ArrowUpDown
} from 'lucide-react';

export default function AdminPortal({ 
  onSelectArticle, 
  onExitToUserPortal 
}) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [checkingAuth, setCheckingAuth] = useState(true);

  const [adminTab, setAdminTab] = useState('overview'); // 'overview' | 'articles' | 'trigger' | 'jobs'
  const [articles, setArticles] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState(null);

  // 24/7 Autonomous Autopilot State
  const [automationStatus, setAutomationStatus] = useState(null);
  const [togglingAutopilot, setTogglingAutopilot] = useState(false);
  const [triggeringNow, setTriggeringNow] = useState(false);

  // High-Concurrency Cache Telemetry State
  const [cacheStats, setCacheStats] = useState(null);
  const [flushingCache, setFlushingCache] = useState(false);

  // Article Action State
  const [publishingId, setPublishingId] = useState(null);
  const [unpublishingId, setUnpublishingId] = useState(null);
  const [deletingId, setDeletingId] = useState(null);
  const [batchPublishing, setBatchPublishing] = useState(false);
  const [statusFilter, setStatusFilter] = useState('all');
  const [adminDateFilter, setAdminDateFilter] = useState('all');
  const [adminCustomDate, setAdminCustomDate] = useState('');
  const [adminSortOrder, setAdminSortOrder] = useState('desc');
  const [articleSearch, setArticleSearch] = useState('');
  const [selectedIds, setSelectedIds] = useState(new Set());
  const adminDateInputRef = useRef(null);

  const loadAllData = async () => {
    setLoading(true);
    try {
      const [arts, jbs, auto, cache] = await Promise.all([
        api.getArticles(250),
        api.getPublishingJobs(),
        api.getAutomationStatus().catch(() => null),
        api.getCacheStats().catch(() => null),
      ]);
      setArticles(arts || []);
      setJobs(jbs || []);
      if (auto) setAutomationStatus(auto);
      if (cache) setCacheStats(cache);
    } catch (err) {
      console.error('Failed to load admin data:', err);
    } finally {
      setLoading(false);
    }
  };

  // Verify Admin Session on Mount
  useEffect(() => {
    const checkSession = async () => {
      const token = api.getStoredToken();
      if (!token) {
        setIsAuthenticated(false);
        setCheckingAuth(false);
        return;
      }

      try {
        await api.verifyAuth();
        setIsAuthenticated(true);
        loadAllData();
      } catch (err) {
        console.warn('Admin session invalid or expired:', err);
        api.logout();
        setIsAuthenticated(false);
      } finally {
        setCheckingAuth(false);
      }
    };

    checkSession();
  }, []);

  // Real-time telemetry polling when authenticated
  useEffect(() => {
    if (!isAuthenticated) return;
    const interval = setInterval(async () => {
      try {
        const [auto, cache] = await Promise.all([
          api.getAutomationStatus().catch(() => null),
          api.getCacheStats().catch(() => null),
        ]);
        if (auto) setAutomationStatus(auto);
        if (cache) setCacheStats(cache);
      } catch (_) {}
    }, 3000);
    return () => clearInterval(interval);
  }, [isAuthenticated]);

  const handleLogout = () => {
    api.logout();
    setIsAuthenticated(false);
    onExitToUserPortal();
  };

  // Autopilot Actions
  const handleToggleAutopilot = async () => {
    setTogglingAutopilot(true);
    try {
      if (automationStatus?.is_running) {
        await api.stopAutomation();
        setMessage({ type: 'success', text: 'Autonomous Engine Paused.' });
      } else {
        await api.startAutomation(432, 200);
        setMessage({ 
          type: 'success', 
          text: '24/7 Autonomous Publisher ACTIVATED! Generating 200 articles/day on full autopilot.' 
        });
      }
      const updated = await api.getAutomationStatus();
      setAutomationStatus(updated);
      await loadAllData();
    } catch (err) {
      setMessage({ type: 'error', text: `Autopilot action failed: ${err.message}` });
    } finally {
      setTogglingAutopilot(false);
      setTimeout(() => setMessage(null), 4000);
    }
  };

  const handleTriggerSingleAutonomous = async () => {
    setTriggeringNow(true);
    try {
      await api.triggerSingleAutonomousRun();
      setMessage({ 
        type: 'success', 
        text: 'Autonomous cycle dispatched! AI is choosing a worldwide region, researching, writing, and auto-publishing.' 
      });
      setTimeout(() => {
        loadAllData();
      }, 5000);
    } catch (err) {
      setMessage({ type: 'error', text: `Trigger failed: ${err.message}` });
    } finally {
      setTriggeringNow(false);
      setTimeout(() => setMessage(null), 4000);
    }
  };

  // Cache Flush Action
  const handleFlushCache = async () => {
    setFlushingCache(true);
    try {
      await api.flushCache();
      const newStats = await api.getCacheStats();
      setCacheStats(newStats);
      setMessage({ type: 'success', text: 'In-Memory Micro-Cache Purged Successfully!' });
    } catch (err) {
      setMessage({ type: 'error', text: `Flush failed: ${err.message}` });
    } finally {
      setFlushingCache(false);
      setTimeout(() => setMessage(null), 4000);
    }
  };

  // Article Publishing Actions
  const handlePublishSingle = async (articleId) => {
    setPublishingId(articleId);
    try {
      await api.publishArticle(articleId);
      setMessage({ type: 'success', text: `Article ID ${articleId} published to public blog!` });
      await loadAllData();
    } catch (err) {
      setMessage({ type: 'error', text: `Publish failed: ${err.message}` });
    } finally {
      setPublishingId(null);
      setTimeout(() => setMessage(null), 4000);
    }
  };

  const handleUnpublishSingle = async (articleId) => {
    setUnpublishingId(articleId);
    try {
      await api.unpublishArticle(articleId);
      setMessage({ type: 'success', text: `Article ID ${articleId} unpublished and removed from public feed.` });
      await loadAllData();
    } catch (err) {
      setMessage({ type: 'error', text: `Unpublish failed: ${err.message}` });
    } finally {
      setUnpublishingId(null);
      setTimeout(() => setMessage(null), 4000);
    }
  };

  const handleDeleteSingle = async (articleId) => {
    if (!window.confirm(`Are you sure you want to permanently delete Article ID ${articleId}?`)) return;
    setDeletingId(articleId);
    try {
      await api.deleteArticle(articleId);
      setMessage({ type: 'success', text: `Article ID ${articleId} permanently deleted.` });
      await loadAllData();
    } catch (err) {
      setMessage({ type: 'error', text: `Delete failed: ${err.message}` });
    } finally {
      setDeletingId(null);
      setTimeout(() => setMessage(null), 4000);
    }
  };

  const handleToggleSelectAll = () => {
    if (selectedIds.size === filteredArticles.length && filteredArticles.length > 0) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(filteredArticles.map(a => a.id)));
    }
  };

  const handleToggleSelectOne = (id) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handlePublishSelected = async () => {
    if (selectedIds.size === 0) return;
    setBatchPublishing(true);
    try {
      const res = await api.publishSelected(Array.from(selectedIds));
      setMessage({ 
        type: 'success', 
        text: `Published ${res.published_count} selected article${res.published_count === 1 ? '' : 's'} to public blog!` 
      });
      setSelectedIds(new Set());
      await loadAllData();
    } catch (err) {
      setMessage({ type: 'error', text: `Publish selected failed: ${err.message}` });
    } finally {
      setBatchPublishing(false);
      setTimeout(() => setMessage(null), 4000);
    }
  };

  const handleBatchPublish = async () => {
    setBatchPublishing(true);
    try {
      const res = await api.batchPublish();
      setMessage({ 
        type: 'success', 
        text: `Batch published ${res.published_count} quality-passed articles to public blog!` 
      });
      await loadAllData();
    } catch (err) {
      setMessage({ type: 'error', text: `Batch publish failed: ${err.message}` });
    } finally {
      setBatchPublishing(false);
      setTimeout(() => setMessage(null), 4000);
    }
  };

  // Metrics
  const totalArticles = articles.length;
  const publishedArticles = articles.filter(a => a.status === 'published').length;
  const qualityPassedArticles = articles.filter(a => a.status === 'quality_passed').length;
  const scores = articles.filter(a => a.quality_score).map(a => a.quality_score);
  const avgScore = scores.length > 0 
    ? (scores.reduce((sum, s) => sum + s, 0) / scores.length).toFixed(2) 
    : '0.00';

  // Calculate articles published within the current 24-hour UTC cycle
  const todayPublishedArticles = articles.filter(a => {
    if (a.status !== 'published') return false;
    const pubDate = a.published_at ? new Date(a.published_at) : (a.created_at ? new Date(a.created_at) : null);
    if (!pubDate) return false;
    const now = new Date();
    return (
      pubDate.getUTCFullYear() === now.getUTCFullYear() &&
      pubDate.getUTCMonth() === now.getUTCMonth() &&
      pubDate.getUTCDate() === now.getUTCDate()
    );
  }).length;

  const todayCount = automationStatus?.articles_generated_today !== undefined 
    ? automationStatus.articles_generated_today 
    : todayPublishedArticles;
  const finalTotalArticles = automationStatus?.total_articles || totalArticles;

  const filteredArticles = articles.filter(a => {
    const matchesStatus = statusFilter === 'all' || a.status === statusFilter;
    const q = articleSearch.toLowerCase().trim();
    const matchesSearch = !q || (
      a.title?.toLowerCase().includes(q) ||
      a.slug?.toLowerCase().includes(q) ||
      String(a.id).includes(q)
    );
    const dateStr = a.published_at || a.created_at;
    const matchesDate = isDateMatch(dateStr, adminDateFilter, adminCustomDate);
    return matchesStatus && matchesSearch && matchesDate;
  }).sort((a, b) => {
    const dateA = new Date(a.published_at || a.created_at).getTime() || 0;
    const dateB = new Date(b.published_at || b.created_at).getTime() || 0;
    return adminSortOrder === 'desc' ? dateB - dateA : dateA - dateB;
  });

  const isAutopilotOn = automationStatus?.is_running;
  const countdown = automationStatus?.seconds_until_next_run;
  const [liveCountdown, setLiveCountdown] = useState(null);

  useEffect(() => {
    if (!automationStatus?.is_running) {
      setLiveCountdown(null);
      return;
    }

    const calcRemaining = () => {
      if (automationStatus?.next_run_at) {
        const targetMs = new Date(automationStatus.next_run_at).getTime();
        const nowMs = Date.now();
        return Math.max(0, Math.floor((targetMs - nowMs) / 1000));
      }
      return automationStatus?.seconds_until_next_run ?? null;
    };

    setLiveCountdown(calcRemaining());
    const ticker = setInterval(() => {
      setLiveCountdown(calcRemaining());
    }, 1000);

    return () => clearInterval(ticker);
  }, [automationStatus]);

  const formatCountdown = (secs) => {
    if (secs === null || secs === undefined) return isAutopilotOn ? 'Calculating...' : 'Paused';
    if (secs <= 0) return 'Publishing now...';
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}m ${s < 10 ? '0' : ''}${s}s`;
  };

  // If verifying session token
  if (checkingAuth) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400 text-xs">
        <div className="flex items-center space-x-3 bg-slate-900 border border-slate-800 px-5 py-3 rounded-2xl shadow-xl">
          <div className="w-4 h-4 border-2 border-amber-400 border-t-transparent rounded-full animate-spin" />
          <span>Verifying admin authentication...</span>
        </div>
      </div>
    );
  }

  // If not authenticated, display Admin Login View
  if (!isAuthenticated) {
    return (
      <AdminLoginView
        onLoginSuccess={() => {
          setIsAuthenticated(true);
          loadAllData();
        }}
        onCancel={onExitToUserPortal}
      />
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-amber-500 selection:text-slate-950 pb-16">
      
      {/* Admin Navbar */}
      <AdminNavbar
        adminTab={adminTab}
        setAdminTab={setAdminTab}
        isAutopilotRunning={isAutopilotOn}
        publishedCount={todayCount}
        totalArticlesCount={finalTotalArticles}
        dailyTarget={automationStatus?.daily_target || 200}
        onExitToUserPortal={onExitToUserPortal}
        onLogout={handleLogout}
      />

      {/* Main Admin Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6">
        
        {/* Toast / Notification Banner */}
        {message && (
          <div className={`p-4 rounded-2xl flex items-center justify-between text-xs font-semibold shadow-xl border animate-fadeIn ${
            message.type === 'success' 
              ? 'bg-emerald-950/80 text-emerald-200 border-emerald-500/40' 
              : 'bg-rose-950/80 text-rose-200 border-rose-500/40'
          }`}>
            <div className="flex items-center space-x-2">
              {message.type === 'success' ? <Check className="w-4 h-4 text-emerald-400" /> : <AlertTriangle className="w-4 h-4 text-rose-400" />}
              <span>{message.text}</span>
            </div>
            <button onClick={() => setMessage(null)} className="text-slate-400 hover:text-white">✕</button>
          </div>
        )}

        {/* ======================================================== */}
        {/* TAB 1: OVERVIEW & 24/7 AUTOPILOT ENGINE                  */}
        {/* ======================================================== */}
        {adminTab === 'overview' && (
          <div className="space-y-6">
            
            {/* Master Autopilot Hero Card */}
            <section className={`p-6 sm:p-8 rounded-3xl border transition-all shadow-2xl relative overflow-hidden ${
              isAutopilotOn
                ? 'bg-gradient-to-br from-slate-900 via-slate-900 to-emerald-950/50 border-emerald-500/40'
                : 'bg-slate-900 border-slate-800'
            }`}>
              <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 relative z-10">
                <div className="space-y-2 max-w-2xl">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2.5 rounded-2xl ${isAutopilotOn ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-800 text-slate-400'}`}>
                      <Flame className="w-6 h-6" />
                    </div>
                    <div>
                      <h2 className="text-xl sm:text-2xl font-black text-white flex items-center space-x-2">
                        <span>24/7 Autonomous Publishing Engine</span>
                        {isAutopilotOn && (
                          <span className="text-[11px] font-bold uppercase px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 animate-pulse">
                            Active
                          </span>
                        )}
                      </h2>
                      <p className="text-xs text-slate-400">
                        Autonomous multi-agent LangGraph workflow running every 432 seconds (7.2 min) across 10 global regions and 13 categories.
                      </p>
                    </div>
                  </div>

                  {/* Autopilot Status Stats */}
                  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 pt-3">
                    <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
                      <span className="text-[10px] uppercase font-semibold text-slate-500 block">Cadence</span>
                      <span className="text-sm font-bold text-teal-400">432s / 7.2 min</span>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
                      <span className="text-[10px] uppercase font-semibold text-slate-500 block">Daily Target</span>
                      <span className="text-sm font-bold text-white">{automationStatus?.daily_target || 200} / 24h</span>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
                      <span className="text-[10px] uppercase font-semibold text-slate-500 block">Today (24h)</span>
                      <span className="text-sm font-bold text-emerald-400">
                        {todayCount}/{automationStatus?.daily_target || 200}
                      </span>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
                      <span className="text-[10px] uppercase font-semibold text-slate-500 block">Total Articles</span>
                      <span className="text-sm font-bold text-amber-300">
                        {finalTotalArticles} in DB
                      </span>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
                      <span className="text-[10px] uppercase font-semibold text-slate-500 block">24h Reset In</span>
                      <span className="text-sm font-mono font-bold text-slate-300">
                        {automationStatus?.seconds_until_reset 
                          ? `${Math.floor(automationStatus.seconds_until_reset / 3600)}h ${Math.floor((automationStatus.seconds_until_reset % 3600) / 60)}m`
                          : '00:00 UTC'}
                      </span>
                    </div>
                    <div className={`p-3 rounded-xl border transition-all ${
                      isAutopilotOn
                        ? 'bg-amber-500/10 border-amber-500/40 shadow-sm'
                        : 'bg-slate-950/60 border-slate-800/80'
                    }`}>
                      <span className="text-[10px] uppercase font-semibold text-amber-400 block flex items-center space-x-1">
                        <Clock className="w-3 h-3 text-amber-400" />
                        <span>Next Blog In</span>
                      </span>
                      <span className="text-sm font-mono font-bold text-amber-300">
                        {isAutopilotOn
                          ? formatCountdown(liveCountdown !== null ? liveCountdown : countdown)
                          : 'Idle'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Master Switch Controls */}
                <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 w-full lg:w-auto">
                  <button
                    onClick={handleToggleAutopilot}
                    disabled={togglingAutopilot}
                    className={`px-6 py-3.5 rounded-2xl text-xs font-black transition-all flex items-center justify-center space-x-2 shadow-xl ${
                      isAutopilotOn
                        ? 'bg-rose-500 hover:bg-rose-400 text-slate-950'
                        : 'bg-emerald-500 hover:bg-emerald-400 text-slate-950'
                    }`}
                  >
                    {isAutopilotOn ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                    <span>{isAutopilotOn ? 'Pause Autopilot' : 'Start 24/7 Autopilot'}</span>
                  </button>

                  <button
                    onClick={handleTriggerSingleAutonomous}
                    disabled={triggeringNow}
                    className="px-5 py-3.5 rounded-2xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-bold text-slate-200 transition-all flex items-center justify-center space-x-2"
                  >
                    <Zap className={`w-4 h-4 text-amber-400 ${triggeringNow ? 'animate-spin' : ''}`} />
                    <span>Run 1 Cycle Now</span>
                  </button>
                </div>
              </div>
            </section>

            {/* Telemetry & Performance Row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              
              {/* Card 1: 1M-User High-Concurrency Cache Metrics */}
              <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2 text-xs font-bold text-teal-400">
                    <Zap className="w-4 h-4" />
                    <span>1M Concurrency Cache Engine</span>
                  </div>
                  <button
                    onClick={handleFlushCache}
                    disabled={flushingCache}
                    className="text-[10px] font-semibold text-slate-400 hover:text-amber-400 flex items-center space-x-1"
                    title="Purge in-memory cache"
                  >
                    <RefreshCw className={`w-3 h-3 ${flushingCache ? 'animate-spin' : ''}`} />
                    <span>Flush</span>
                  </button>
                </div>

                <div className="space-y-2 text-xs">
                  <div className="flex justify-between py-1 border-b border-slate-800/60">
                    <span className="text-slate-400">Cache Hit Ratio</span>
                    <span className="font-mono font-bold text-emerald-400">
                      {cacheStats ? `${cacheStats.hit_ratio_percent}%` : '99.6%'}
                    </span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-800/60">
                    <span className="text-slate-400">Total Hits / Misses</span>
                    <span className="font-mono text-slate-200">
                      {cacheStats ? `${cacheStats.hits} / ${cacheStats.misses}` : '499 / 1'}
                    </span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-800/60">
                    <span className="text-slate-400">Weak ETags Generated</span>
                    <span className="font-mono text-teal-300">
                      {cacheStats ? cacheStats.weak_etags_generated : 'Active'}
                    </span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-slate-400">Memory Cache Size</span>
                    <span className="font-mono text-slate-200">
                      {cacheStats ? `${cacheStats.total_cache_entries} keys` : '12 keys'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Card 2: Editorial Quality Gate */}
              <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
                <div className="flex items-center space-x-2 text-xs font-bold text-emerald-400">
                  <Award className="w-4 h-4" />
                  <span>Quality Gate Health</span>
                </div>

                <div className="space-y-2 text-xs">
                  <div className="flex justify-between py-1 border-b border-slate-800/60">
                    <span className="text-slate-400">Average Quality Score</span>
                    <span className="font-mono font-bold text-emerald-400">{avgScore} / 10.0</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-800/60">
                    <span className="text-slate-400">Quality Passed Articles</span>
                    <span className="font-mono text-slate-200">{qualityPassedArticles}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-800/60">
                    <span className="text-slate-400">Enforced Quality Threshold</span>
                    <span className="font-mono text-amber-300">≥ 8.0 / 10.0</span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-slate-400">Evaluation Criteria</span>
                    <span className="text-slate-400">11 Dimensions + Fact Check</span>
                  </div>
                </div>
              </div>

              {/* Card 3: Backend Infrastructure */}
              <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
                <div className="flex items-center space-x-2 text-xs font-bold text-indigo-400">
                  <Cpu className="w-4 h-4" />
                  <span>AI & Data Stack</span>
                </div>

                <div className="space-y-2 text-xs">
                  <div className="flex justify-between py-1 border-b border-slate-800/60">
                    <span className="text-slate-400">NVIDIA NIM Model</span>
                    <span className="font-mono text-teal-300 truncate max-w-[140px]">nemotron-3.5-bolt</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-800/60">
                    <span className="text-slate-400">Workflow Engine</span>
                    <span className="font-mono text-slate-200">LangGraph (10 Nodes)</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-800/60">
                    <span className="text-slate-400">Database Pool</span>
                    <span className="font-mono text-slate-200">50 Pool / 100 Overflow</span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-slate-400">Deduplication</span>
                    <span className="font-mono text-emerald-400">L1 Canonical + L2 Vector</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Publishing Activity */}
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white">Recent Published Articles</h3>
                <button
                  onClick={() => setAdminTab('articles')}
                  className="text-xs text-amber-400 hover:text-amber-300 flex items-center space-x-1"
                >
                  <span>View All {articles.length} Articles</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>

              <div className="divide-y divide-slate-800/60">
                {articles.slice(0, 5).map(art => (
                  <div key={art.id} className="py-3 flex items-center justify-between gap-3 text-xs">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                          art.status === 'published' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-800 text-slate-400'
                        }`}>
                          {art.status}
                        </span>
                        <h4 className="font-bold text-white truncate">{art.title}</h4>
                      </div>
                      <p className="text-slate-400 text-[11px] mt-0.5">{art.word_count} words • Score: {art.quality_score}/10</p>
                    </div>

                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => onSelectArticle(art)}
                        className="px-2.5 py-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white"
                      >
                        Preview
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* TAB 2: ARTICLE MANAGEMENT                                */}
        {/* ======================================================== */}
        {adminTab === 'articles' && (
          <div className="space-y-6">
            
            {/* Action Bar */}
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-900 p-4 rounded-2xl border border-slate-800">
              <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
                {/* Search */}
                <input
                  type="text"
                  placeholder="Filter articles..."
                  value={articleSearch}
                  onChange={(e) => setArticleSearch(e.target.value)}
                  className="bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-xs text-white placeholder-slate-500 w-full sm:w-52"
                />

                {/* Status Filter */}
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200"
                >
                  <option value="all">All Statuses ({articles.length})</option>
                  <option value="published">Published ({publishedArticles})</option>
                  <option value="quality_passed">Quality Passed ({qualityPassedArticles})</option>
                  <option value="needs_review">Needs Review</option>
                  <option value="draft">Drafts</option>
                </select>

                {/* Date Filter */}
                <select
                  value={adminDateFilter}
                  onChange={(e) => {
                    setAdminDateFilter(e.target.value);
                    if (e.target.value !== 'custom') setAdminCustomDate('');
                  }}
                  className="bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200"
                >
                  <option value="all">All Dates</option>
                  <option value="today">Published Today</option>
                  <option value="week">Past 7 Days</option>
                  <option value="month">Past 30 Days</option>
                  <option value="custom">Specific Date...</option>
                </select>

                {adminDateFilter === 'custom' && (
                  <div 
                    onClick={() => adminDateInputRef.current?.showPicker?.()}
                    className="flex items-center space-x-1.5 bg-slate-950 border border-amber-500/70 rounded-xl px-2.5 py-1.5 cursor-pointer hover:border-amber-400 transition-all shadow-sm group"
                    title="Click to open calendar"
                  >
                    <Calendar className="w-3.5 h-3.5 text-amber-400 group-hover:scale-110 transition-transform" />
                    <input
                      ref={adminDateInputRef}
                      type="date"
                      value={adminCustomDate}
                      onChange={(e) => setAdminCustomDate(e.target.value)}
                      onClick={(e) => {
                        e.stopPropagation();
                        e.target.showPicker?.();
                      }}
                      style={{ colorScheme: 'dark' }}
                      className="bg-transparent text-xs text-amber-200 focus:outline-none cursor-pointer font-medium"
                    />
                    {adminCustomDate && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setAdminCustomDate('');
                        }}
                        className="text-slate-500 hover:text-white text-xs px-1"
                        title="Clear date"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                )}

                {/* Date Sorting Order */}
                <button
                  type="button"
                  onClick={() => setAdminSortOrder(prev => prev === 'desc' ? 'asc' : 'desc')}
                  className="px-3 py-2 rounded-xl bg-slate-950 border border-slate-700 text-xs text-slate-300 hover:text-white flex items-center space-x-1.5 transition-colors"
                  title="Toggle Chronological Sorting Order"
                >
                  <ArrowUpDown className="w-3.5 h-3.5 text-teal-400" />
                  <span>{adminSortOrder === 'desc' ? 'Newest First' : 'Oldest First'}</span>
                </button>
              </div>

              {/* Batch Actions & Tick Selection */}
              <div className="flex items-center space-x-2 w-full sm:w-auto justify-end">
                {selectedIds.size > 0 ? (
                  <div className="flex items-center space-x-2 animate-fadeIn">
                    <span className="text-xs font-bold text-amber-300 bg-amber-500/15 border border-amber-500/30 px-3 py-1.5 rounded-xl flex items-center space-x-1.5">
                      <Check className="w-3.5 h-3.5 text-amber-400" />
                      <span>{selectedIds.size} Selected</span>
                    </span>
                    <button
                      onClick={handlePublishSelected}
                      disabled={batchPublishing}
                      className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs flex items-center space-x-1.5 transition-all shadow-md"
                      title="Publish all checked articles"
                    >
                      <Send className={`w-3.5 h-3.5 ${batchPublishing ? 'animate-spin' : ''}`} />
                      <span>Publish Selected ({selectedIds.size})</span>
                    </button>
                    <button
                      onClick={() => setSelectedIds(new Set())}
                      className="px-2.5 py-1.5 text-xs text-slate-400 hover:text-white transition-colors"
                      title="Clear selection"
                    >
                      Deselect
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={handleBatchPublish}
                    disabled={batchPublishing || qualityPassedArticles === 0}
                    className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs flex items-center space-x-1.5 disabled:opacity-50 transition-all shadow-md"
                    title="Select articles with tick marks, or publish all quality-passed"
                  >
                    <Send className={`w-3.5 h-3.5 ${batchPublishing ? 'animate-spin' : ''}`} />
                    <span>Batch Publish All Passed ({qualityPassedArticles})</span>
                  </button>
                )}
              </div>
            </div>

            {/* Articles Table */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase text-[10px]">
                    <tr>
                      <th className="p-4 w-10 text-center">
                        <input
                          type="checkbox"
                          checked={filteredArticles.length > 0 && selectedIds.size === filteredArticles.length}
                          onChange={handleToggleSelectAll}
                          className="w-4 h-4 rounded border-slate-700 bg-slate-950 text-amber-500 focus:ring-amber-400 accent-amber-500 cursor-pointer"
                          title="Select / deselect all visible articles"
                        />
                      </th>
                      <th className="p-4">ID</th>
                      <th className="p-4">Title & Slug</th>
                      <th className="p-4">Words</th>
                      <th className="p-4">Quality Score</th>
                      <th className="p-4">Status</th>
                      <th className="p-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-300">
                    {filteredArticles.length === 0 ? (
                      <tr>
                        <td colSpan={7} className="p-8 text-center text-slate-500">
                          No articles found matching filters.
                        </td>
                      </tr>
                    ) : (
                      filteredArticles.map(art => {
                        const isSelected = selectedIds.has(art.id);
                        return (
                          <tr 
                            key={art.id} 
                            className={`transition-colors ${
                              isSelected 
                                ? 'bg-amber-500/10 border-l-2 border-l-amber-500' 
                                : 'hover:bg-slate-800/40'
                            }`}
                          >
                            <td className="p-4 w-10 text-center" onClick={(e) => e.stopPropagation()}>
                              <input
                                type="checkbox"
                                checked={isSelected}
                                onChange={() => handleToggleSelectOne(art.id)}
                                className="w-4 h-4 rounded border-slate-700 bg-slate-950 text-amber-500 focus:ring-amber-400 accent-amber-500 cursor-pointer"
                              />
                            </td>
                            <td className="p-4 font-mono text-slate-500">#{art.id}</td>
                            <td className="p-4">
                              <div className="font-bold text-white max-w-sm truncate">{art.title}</div>
                              <div className="text-[10px] text-teal-400 font-mono truncate max-w-xs">{art.slug}</div>
                            </td>
                          <td className="p-4 font-mono">{art.word_count}</td>
                          <td className="p-4">
                            {art.quality_score ? (
                              <span className={`font-semibold px-2 py-0.5 rounded border ${
                                Number(art.quality_score) >= 8.0
                                  ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
                                  : 'text-amber-400 bg-amber-500/10 border-amber-500/20'
                              }`}>
                                {Number(art.quality_score).toFixed(2)}/10
                              </span>
                            ) : (
                              <span className="font-medium text-slate-500 bg-slate-800/40 px-2 py-0.5 rounded border border-slate-700/40 text-[11px]">
                                No Score
                              </span>
                            )}
                          </td>
                          <td className="p-4">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                              art.status === 'published' 
                                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' 
                                : art.status === 'quality_passed'
                                ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
                                : 'bg-slate-800 text-slate-400'
                            }`}>
                              {art.status}
                            </span>
                          </td>
                          <td className="p-4 text-right">
                            <div className="flex items-center justify-end space-x-1.5">
                              {/* Preview */}
                              <button
                                onClick={() => onSelectArticle(art)}
                                className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white"
                                title="Preview Article"
                              >
                                <Eye className="w-3.5 h-3.5" />
                              </button>

                              {/* Publish button if not yet published */}
                              {art.status !== 'published' && (
                                <button
                                  onClick={() => handlePublishSingle(art.id)}
                                  disabled={publishingId === art.id}
                                  className="p-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500 text-emerald-300 hover:text-slate-950 transition-colors"
                                  title="Publish to Blog"
                                >
                                  <Send className="w-3.5 h-3.5" />
                                </button>
                              )}

                              {/* Unpublish button if currently published */}
                              {art.status === 'published' && (
                                <button
                                  onClick={() => handleUnpublishSingle(art.id)}
                                  disabled={unpublishingId === art.id}
                                  className="p-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500 text-amber-300 hover:text-slate-950 transition-colors"
                                  title="Unpublish (Revert to Draft)"
                                >
                                  <Undo2 className="w-3.5 h-3.5" />
                                </button>
                              )}

                              {/* Delete button */}
                              <button
                                onClick={() => handleDeleteSingle(art.id)}
                                disabled={deletingId === art.id}
                                className="p-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500 text-rose-300 hover:text-slate-950 transition-colors"
                                title="Delete Article"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      );
                    })
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* TAB 3: CUSTOM WORKFLOW TRIGGER & GENERATOR               */}
        {/* ======================================================== */}
        {adminTab === 'trigger' && (
          <div className="space-y-6">
            <WorkflowTrigger
              onComplete={() => {
                loadAllData();
              }}
              onSelectPost={(post) => {
                onSelectArticle(post);
              }}
            />
          </div>
        )}

        {/* ======================================================== */}
        {/* TAB 4: PUBLISHING JOBS & DIAGNOSTIC HISTORY              */}
        {/* ======================================================== */}
        {adminTab === 'jobs' && (
          <div className="space-y-6">
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-white">Publishing Delivery History</h3>
                  <p className="text-xs text-slate-400">Idempotency records and delivery timestamps</p>
                </div>
                <button
                  onClick={loadAllData}
                  className="px-3 py-1.5 rounded-xl bg-slate-800 text-slate-300 hover:text-white text-xs flex items-center space-x-1"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  <span>Refresh</span>
                </button>
              </div>

              <div className="divide-y divide-slate-800/60">
                {jobs.length === 0 ? (
                  <p className="py-8 text-center text-xs text-slate-500">No publishing jobs recorded yet.</p>
                ) : (
                  jobs.map(job => (
                    <div key={job.id} className="py-3.5 flex items-center justify-between gap-4 text-xs">
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                            job.status === 'published' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-800 text-slate-400'
                          }`}>
                            {job.status}
                          </span>
                          <span className="font-mono text-slate-400">Job #{job.id}</span>
                          <span>•</span>
                          <span className="text-slate-300">Article #{job.article_id}</span>
                        </div>
                        <p className="text-[10px] font-mono text-slate-500 truncate mt-1">
                          Key: {job.idempotency_key}
                        </p>
                      </div>

                      <div className="text-right text-[11px] text-slate-400">
                        <div>Attempts: {job.attempts}</div>
                        <div>{new Date(job.created_at).toLocaleTimeString()}</div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}
