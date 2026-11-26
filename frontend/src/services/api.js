/**
 * World Tourist & Admin Command Center - Centralized API Service Layer.
 * Uses VITE_API_URL environment variable with the production Render URL as fallback.
 */

const rawBaseUrl =
  import.meta.env.VITE_API_URL ?? 'https://globetrotter-ai-e58e.onrender.com';
const API_ORIGIN = rawBaseUrl.replace(/\/+$/, '');
const API_BASE = `${API_ORIGIN}/api/v1`;

async function fetchJson(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
    ...(options.headers || {}),
  };

  // Attach admin session token if available
  const token =
    localStorage.getItem('globetrotter_admin_token') ||
    sessionStorage.getItem('globetrotter_admin_token');
  if (token && !headers['Authorization']) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(url, { cache: 'no-cache', ...options, headers });
  if (!res.ok) {
    const errText = await res.text();
    let errMsg = `Request failed (${res.status})`;
    try {
      const errJson = JSON.parse(errText);
      errMsg = errJson.detail || errMsg;
    } catch {
      errMsg = errText || errMsg;
    }
    throw new Error(errMsg);
  }
  return res.json();
}

export const api = {
  // Public Feed, Post Viewer & Metadata (World Tourist)
  async getFeed(categoryOrOpts = null, country = null, limit = 100, offset = 0) {
    let cat = categoryOrOpts;
    let cntry = country;
    let lim = limit;
    let off = offset;

    if (categoryOrOpts && typeof categoryOrOpts === 'object' && !Array.isArray(categoryOrOpts)) {
      cat = categoryOrOpts.category ?? null;
      cntry = categoryOrOpts.country ?? null;
      lim = categoryOrOpts.limit ?? 100;
      off = categoryOrOpts.offset ?? 0;
    }

    const params = new URLSearchParams();
    if (cat && cat !== 'All') params.append('category', cat);
    if (cntry) params.append('country', cntry);
    params.append('limit', String(lim));
    params.append('offset', String(off));
    params.append('_t', String(Date.now()));
    return fetchJson(`/publish/feed?${params.toString()}`);
  },

  async getPostBySlug(slug) {
    return fetchJson(`/publish/post/${encodeURIComponent(slug)}`);
  },

  async getMetadata() {
    return fetchJson('/topics/metadata');
  },

  // Publishing & Jobs (Admin Portal)
  async getPublishingJobs() {
    return fetchJson('/publish/jobs?limit=50');
  },

  async publishArticle(articleId) {
    return fetchJson(`/publish/${articleId}?force=true`, { method: 'POST' });
  },

  async unpublishArticle(articleId) {
    return fetchJson(`/publish/unpublish/${articleId}`, { method: 'POST' });
  },

  async batchPublish() {
    return fetchJson('/publish/batch/run', { method: 'POST' });
  },

  async publishSelected(articleIds) {
    return fetchJson('/publish/batch/selected', {
      method: 'POST',
      body: JSON.stringify({ article_ids: articleIds, force: true }),
    });
  },

  // Articles & Pipeline
  async getArticles(limit = 250) {
    return fetchJson(`/articles?limit=${limit}`);
  },

  async getArticleDetail(articleId) {
    return fetchJson(`/articles/${articleId}`);
  },

  async deleteArticle(articleId) {
    return fetchJson(`/articles/${articleId}`, { method: 'DELETE' });
  },

  // High-Concurrency Cache Management
  async getCacheStats() {
    return fetchJson('/publish/cache/stats');
  },

  async flushCache() {
    return fetchJson('/publish/cache/flush', { method: 'POST' });
  },

  async runWorkflow(payload) {
    return fetchJson('/workflow/run', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async getWorkflowStages() {
    return fetchJson('/workflow/stages');
  },

  // 24/7 Autonomous Publisher
  async getAutomationStatus() {
    return fetchJson('/automation/status');
  },

  async startAutomation(interval_seconds = 432, daily_target = 200) {
    return fetchJson('/automation/start', {
      method: 'POST',
      body: JSON.stringify({ interval_seconds, daily_target }),
    });
  },

  async stopAutomation() {
    return fetchJson('/automation/stop', { method: 'POST' });
  },

  async triggerSingleAutonomousRun() {
    return fetchJson('/automation/trigger-single', { method: 'POST' });
  },

  // System Health
  async getHealth() {
    return fetchJson('/health');
  },

  // Admin Authentication
  async login(username, password) {
    const data = await fetchJson('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    if (data.token) {
      localStorage.setItem('globetrotter_admin_token', data.token);
      localStorage.setItem('globetrotter_admin_user', data.username);
    }
    return data;
  },

  async verifyAuth() {
    return fetchJson('/auth/verify');
  },

  logout() {
    localStorage.removeItem('globetrotter_admin_token');
    localStorage.removeItem('globetrotter_admin_user');
    sessionStorage.removeItem('globetrotter_admin_token');
    sessionStorage.removeItem('globetrotter_admin_user');
  },

  getStoredToken() {
    return (
      localStorage.getItem('globetrotter_admin_token') ||
      sessionStorage.getItem('globetrotter_admin_token')
    );
  },
};
