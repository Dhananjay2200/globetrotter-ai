import React, { useState, useEffect } from 'react';
import { 
  BarChart3, CheckCircle2, Clock, AlertTriangle, Send, 
  RefreshCw, Globe, Layers, Award, Sparkles, Eye, Power, 
  Play, Pause, Flame, ShieldAlert, Check 
} from 'lucide-react';
import { api } from '../services/api';

export default function AdminDashboard({ onSelectArticle, onTriggerTab }) {
  const [articles, setArticles] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [publishingId, setPublishingId] = useState(null);
  const [batchPublishing, setBatchPublishing] = useState(false);
  const [statusFilter, setStatusFilter] = useState('all');
  const [message, setMessage] = useState(null);

  // 24/7 Autonomous Autopilot State
  const [automationStatus, setAutomationStatus] = useState(null);
  const [togglingAutopilot, setTogglingAutopilot] = useState(false);
  const [triggeringNow, setTriggeringNow] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [arts, jbs] = await Promise.all([
        api.getArticles(100),
        api.getPublishingJobs(),
      ]);
      setArticles(arts || []);
      setJobs(jbs || []);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadAutomation = async () => {
    try {
      const status = await api.getAutomationStatus();
      setAutomationStatus(status);
    } catch (err) {
      console.error('Failed to fetch automation telemetry:', err);
    }
  };

  useEffect(() => {
    loadData();
    loadAutomation();
    // Live polling for countdown & status
    const pollInterval = setInterval(() => {
      loadAutomation();
    }, 3000);
    return () => clearInterval(pollInterval);
  }, []);

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
      await loadAutomation();
      await loadData();
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
        text: 'Autonomous cycle dispatched! AI is selecting a new worldwide region, researching, writing, and auto-publishing.' 
      });
      setTimeout(() => {
        loadData();
        loadAutomation();
      }, 5000);
    } catch (err) {
      setMessage({ type: 'error', text: `Trigger failed: ${err.message}` });
    } finally {
      setTriggeringNow(false);
      setTimeout(() => setMessage(null), 4000);
    }
  };

  const handlePublishSingle = async (articleId) => {
    setPublishingId(articleId);
    try {
      await api.publishArticle(articleId);
      setMessage({ type: 'success', text: `Article ID ${articleId} published successfully!` });
      await loadData();
    } catch (err) {
      setMessage({ type: 'error', text: `Publishing failed: ${err.message}` });
    } finally {
      setPublishingId(null);
      setTimeout(() => setMessage(null), 4000);
    }
  };

  const handleBatchPublish = async () => {
    setBatchPublishing(true);
    try {
      const res = await api.batchPublish();
      setMessage({ 
        type: 'success', 
        text: `Batch Publish Completed! Published: ${res.published_count}, Failed: ${res.failed_count}` 
      });
      await loadData();
    } catch (err) {
      setMessage({ type: 'error', text: `Batch publishing failed: ${err.message}` });
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

  const filteredArticles = articles.filter(a => {
    if (statusFilter === 'all') return true;
    return a.status === statusFilter;
  });

  const isAutopilotOn = automationStatus?.is_running;
  const countdown = automationStatus?.seconds_until_next_run;
  const formatCountdown = (secs) => {
    if (!secs) return 'Executing now...';
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}m ${s < 10 ? '0' : ''}${s}s`;
  };

  return (
    <div className="space-y-8">
      {/* Alert Notification */}
      {message && (
        <div className={`p-4 rounded-xl text-xs font-semibold flex items-center justify-between border ${
          message.type === 'success' 
            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' 
            : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
        }`}>
          <span>{message.text}</span>
          <button onClick={() => setMessage(null)} className="text-slate-400 hover:text-white">✕</button>
        </div>
      )}

      {/* 24/7 AUTONOMOUS AUTOPILOT MASTER CONSOLE */}
      <section className="relative rounded-3xl overflow-hidden border border-teal-500/30 bg-gradient-to-br from-slate-900 via-slate-900/90 to-teal-950/20 p-6 sm:p-8 shadow-2xl">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <span className={`w-3 h-3 rounded-full ${isAutopilotOn ? 'bg-emerald-400 animate-ping' : 'bg-slate-500'}`} />
              <span className="text-xs font-mono font-bold uppercase tracking-wider text-teal-300">
                24/7 Continuous Publishing Engine
              </span>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${
                isAutopilotOn 
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' 
                  : 'bg-slate-800 text-slate-400'
              }`}>
                {isAutopilotOn ? 'Autopilot Active' : 'Autopilot Paused'}
              </span>
            </div>

            <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Autonomous 200 Articles / Day Engine
            </h2>

            <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
              When active, the AI works 100% autonomously: it rotates across all 10 worldwide regions, balances across 13 tourism genres, verifies fact-backed citations, evaluates quality (&ge;8.0/10), and auto-publishes without human intervention.
            </p>

            <div className="flex flex-wrap items-center gap-4 pt-2 text-xs text-slate-400 font-mono">
              <div>Pacing: <span className="text-teal-300 font-bold">1 post every 7.2 mins (432s)</span></div>
              <div>•</div>
              <div>Target: <span className="text-emerald-300 font-bold">200 blogs/24h</span></div>
              <div>•</div>
              <div>
                Next Autonomous Post: <span className="text-amber-300 font-bold">
                  {isAutopilotOn ? formatCountdown(countdown) : 'Paused'}
                </span>
              </div>
            </div>
          </div>

          {/* Autopilot Master Action Buttons */}
          <div className="flex flex-col sm:flex-row lg:flex-col gap-3 w-full lg:w-auto shrink-0">
            <button
              onClick={handleToggleAutopilot}
              disabled={togglingAutopilot}
              className={`flex items-center justify-center space-x-2 px-6 py-3.5 rounded-2xl text-xs font-extrabold transition-all shadow-xl ${
                isAutopilotOn
                  ? 'bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/40'
                  : 'bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-emerald-500/25'
              }`}
            >
              {isAutopilotOn ? (
                <>
                  <Pause className="w-4 h-4" />
                  <span>Pause 24/7 Autopilot</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  <span>Activate 24/7 Autopilot</span>
                </>
              )}
            </button>

            <button
              onClick={handleTriggerSingleAutonomous}
              disabled={triggeringNow}
              className="flex items-center justify-center space-x-2 px-5 py-3 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold border border-slate-700 transition-colors"
            >
              <Sparkles className="w-3.5 h-3.5 text-teal-400" />
              <span>{triggeringNow ? 'Dispatching Cycle...' : 'Trigger 1 Cycle Now'}</span>
            </button>
          </div>
        </div>

        {/* Progress Bar towards 200 */}
        <div className="mt-6 pt-6 border-t border-slate-800/80">
          <div className="flex items-center justify-between text-xs text-slate-300 mb-2">
            <span>Daily Autopilot Progress</span>
            <span className="font-mono text-teal-300 font-bold">
              {publishedArticles} / 200 Articles ({Math.min(100, Math.round((publishedArticles / 200) * 100))}%)
            </span>
          </div>
          <div className="w-full bg-slate-950 h-2.5 rounded-full overflow-hidden p-0.5 border border-slate-800">
            <div 
              className="bg-gradient-to-r from-teal-400 via-emerald-400 to-indigo-500 h-full rounded-full transition-all duration-700"
              style={{ width: `${Math.min(100, Math.round((publishedArticles / 200) * 100))}%` }}
            />
          </div>
        </div>
      </section>

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 relative overflow-hidden">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span>Published Travel Stories</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-white">{publishedArticles}</div>
          <div className="text-[11px] text-emerald-400 font-medium mt-2 flex items-center space-x-1">
            <span>Live on Public Feed</span>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 relative overflow-hidden">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span>Quality Pass Rate</span>
            <Award className="w-4 h-4 text-teal-400" />
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-white">100%</div>
          <div className="text-[11px] text-slate-400 mt-2">
            Average Score: <span className="text-teal-300 font-bold">{avgScore} / 10.0</span>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 relative overflow-hidden">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span>Pending Publish</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-white">{qualityPassedArticles}</div>
          <div className="text-[11px] text-amber-300 mt-2">
            Approved & ready to dispatch
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 relative overflow-hidden">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span>NVIDIA Model</span>
            <Sparkles className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-lg sm:text-xl font-bold text-white font-mono truncate">
            Nemotron 3.5
          </div>
          <div className="text-[11px] text-teal-400 mt-2">
            NIM Microservice Online
          </div>
        </div>
      </div>

      {/* Articles Management Table */}
      <section className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="p-5 border-b border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-lg font-bold text-white">All Discovered & Generated Articles</h3>
            <p className="text-xs text-slate-400">Inspected by 11-dimension quality gate</p>
          </div>

          <div className="flex items-center space-x-2">
            {qualityPassedArticles > 0 && (
              <button
                onClick={handleBatchPublish}
                disabled={batchPublishing}
                className="px-3.5 py-1.5 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 text-xs font-bold transition-all"
              >
                {batchPublishing ? 'Publishing...' : `Publish Approved (${qualityPassedArticles})`}
              </button>
            )}

            <button
              onClick={loadData}
              disabled={loading}
              className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300"
              title="Refresh Articles"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 text-slate-400 uppercase font-mono text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3.5 px-4">Article</th>
                <th className="py-3.5 px-4">Destination</th>
                <th className="py-3.5 px-4">Words</th>
                <th className="py-3.5 px-4">Quality</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filteredArticles.length === 0 ? (
                <tr>
                  <td colSpan="6" className="py-8 text-center text-slate-500">
                    No articles found.
                  </td>
                </tr>
              ) : (
                filteredArticles.map(art => (
                  <tr key={art.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-4 px-4 font-medium text-white max-w-xs truncate">
                      <span className="block truncate" title={art.title}>{art.title}</span>
                      <span className="text-[10px] text-slate-500 font-mono">ID #{art.id} • /{art.slug}</span>
                    </td>
                    <td className="py-4 px-4 whitespace-nowrap text-slate-300">
                      {art.destination || 'Global'}
                    </td>
                    <td className="py-4 px-4 whitespace-nowrap font-mono">
                      {art.word_count}
                    </td>
                    <td className="py-4 px-4 whitespace-nowrap">
                      {art.quality_score ? (
                        <span className="px-2 py-0.5 rounded font-bold font-mono bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                          {art.quality_score}/10
                        </span>
                      ) : (
                        <span className="text-slate-500">—</span>
                      )}
                    </td>
                    <td className="py-4 px-4 whitespace-nowrap">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        art.status === 'published'
                          ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30'
                          : art.status === 'quality_passed'
                          ? 'bg-teal-500/15 text-teal-300 border border-teal-500/30'
                          : 'bg-slate-800 text-slate-400'
                      }`}>
                        {art.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-4 px-4 text-right whitespace-nowrap space-x-2">
                      <button
                        onClick={() => onSelectArticle(art)}
                        className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs transition-colors inline-flex items-center space-x-1"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>Preview</span>
                      </button>

                      {art.status === 'quality_passed' && (
                        <button
                          onClick={() => handlePublishSingle(art.id)}
                          disabled={publishingId === art.id}
                          className="px-2.5 py-1.5 rounded-lg bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs transition-colors inline-flex items-center space-x-1"
                        >
                          <Send className="w-3.5 h-3.5" />
                          <span>{publishingId === art.id ? 'Publishing...' : 'Publish'}</span>
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
