/**
 * GlobeTrotter AI - Frontend API Service Client.
 * Connects to the FastAPI backend with proxy support and full fallback handling.
 */

const API_BASE = '/api/v1';

async function fetchJson(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  // Attach admin session token if available
  const token = localStorage.getItem('globetrotter_admin_token') || sessionStorage.getItem('globetrotter_admin_token');
  if (token && !headers['Authorization']) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const res = await fetch(url, { cache: 'no-cache', ...options, headers });
    if (!res.ok) {
      const errText = await res.text();
      let errMsg = `Request failed: ${res.status}`;
      try {
        const errJson = JSON.parse(errText);
        errMsg = errJson.detail || errMsg;
      } catch (_) {
        errMsg = errText || errMsg;
      }
      throw new Error(errMsg);
    }
    return await res.json();
  } catch (err) {
    console.error(`API call to ${url} failed:`, err);
    throw err;
  }
}

export const api = {
  // Public Feed & Post Viewer
  async getFeed(category, country, limit = 100, offset = 0) {
    const params = new URLSearchParams();
    if (category && category !== 'All') params.append('category', category);
    if (country) params.append('country', country);
    params.append('limit', limit);
    params.append('offset', offset);
    params.append('_t', Date.now());
    return fetchJson(`/publish/feed?${params.toString()}`);
  },

  async getPostBySlug(slug) {
    return fetchJson(`/publish/post/${slug}`);
  },

  // Publishing & Jobs
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

  // 24/7 Autonomous Publisher (200 Articles/Day Engine)
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

  // Admin Authentication (.env-configured)
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
    return localStorage.getItem('globetrotter_admin_token') || sessionStorage.getItem('globetrotter_admin_token');
  },
};
