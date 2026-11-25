import React, { useState } from 'react';
import { 
  Sparkles, Play, CheckCircle2, AlertCircle, 
  RotateCw, Globe, Layers, ArrowRight, ShieldCheck, 
  FileText, Image as ImageIcon, Award 
} from 'lucide-react';
import { api } from '../services/api';

const GLOBAL_REGIONS = [
  'East & Southeast Asia',
  'South & Central Asia',
  'Western & Northern Europe',
  'Southern & Eastern Europe',
  'North America',
  'Central America & Caribbean',
  'South America',
  'Middle East & North Africa',
  'Sub-Saharan Africa',
  'Oceania & Pacific Islands',
];

const TOURISM_CATEGORIES = [
  'Historical Monuments & Heritage Sites',
  'Waterfalls, Mountains & Natural Wonders',
  'Hidden Gems & Unexplored Places',
  'Festivals & Cultural Traditions',
  'Local Cuisines & Culinary Journeys',
  'Travel Experiences & Immersive Activities',
  'Road Trips & Scenic Itineraries',
  'Adventure Tourism & Extreme Expeditions',
  'Wildlife, Safaris & National Parks',
  'Ancient Civilizations & Historic Cities',
  'Seasonal & Winter/Summer Escapes',
  'Budget Travel & Backpacker Guides',
  'Coastal Escapes & Island Wonders',
];

const STAGES = [
  { id: 'discover', label: '1. Topic Discovery', desc: 'NVIDIA NIM Worldwide Intelligence' },
  { id: 'dedup', label: '2. Deduplication Gate', desc: 'Canonical & Semantic Similarity' },
  { id: 'research', label: '3. Research Agent', desc: 'Wikipedia & Multi-Source Citations' },
  { id: 'writer', label: '4. Article Writer', desc: '12-Section Long-Form Markdown' },
  { id: 'seo', label: '5. SEO Optimizer', desc: 'Meta, Slug & Keyword Synthesis' },
  { id: 'media', label: '6. Media Discovery', desc: 'Wikimedia Commons CC Licensing' },
  { id: 'quality', label: '7. Quality Gate', desc: '11-Dimension Rubric (Threshold: 8.0)' },
];

export default function WorkflowTrigger({ onComplete, onSelectPost }) {
  const [mode, setMode] = useState('auto'); // 'auto' | 'custom'
  const [running, setRunning] = useState(false);
  const [activeStage, setActiveStage] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Custom Form Fields
  const [destination, setDestination] = useState('');
  const [country, setCountry] = useState('');
  const [region, setRegion] = useState(GLOBAL_REGIONS[0]);
  const [category, setCategory] = useState(TOURISM_CATEGORIES[0]);
  const [uniqueAngle, setUniqueAngle] = useState('');
  const [qualityThreshold, setQualityThreshold] = useState(8.0);

  const handleRunPipeline = async () => {
    setRunning(true);
    setError(null);
    setResult(null);
    setActiveStage(1);

    // Simulated visual progression across stages while pipeline executes
    const stageInterval = setInterval(() => {
      setActiveStage(prev => (prev < 6 ? prev + 1 : prev));
    }, 4500);

    try {
      const payload = mode === 'auto' 
        ? { quality_threshold: qualityThreshold }
        : {
            destination: destination.trim() || undefined,
            country: country.trim() || undefined,
            region,
            category,
            unique_angle: uniqueAngle.trim() || undefined,
            quality_threshold: qualityThreshold,
          };

      const finalState = await api.runWorkflow(payload);
      clearInterval(stageInterval);
      setActiveStage(7);
      setResult(finalState);
      if (onComplete) onComplete();
    } catch (err) {
      clearInterval(stageInterval);
      setError(err.message);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Title */}
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight flex items-center space-x-2">
          <Sparkles className="w-6 h-6 text-amber-400" />
          <span>Autonomous LangGraph Pipeline Trigger</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Execute the end-to-end multi-agent pipeline powered by NVIDIA NIM & LangGraph
        </p>
      </div>

      {/* Mode Switcher */}
      <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 p-1.5 rounded-2xl w-fit">
        <button
          onClick={() => setMode('auto')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
            mode === 'auto'
              ? 'bg-teal-500 text-slate-950 shadow-md font-bold'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <Globe className="w-3.5 h-3.5" />
          <span>Autonomous Worldwide (Auto-Rotate)</span>
        </button>

        <button
          onClick={() => setMode('custom')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
            mode === 'custom'
              ? 'bg-teal-500 text-slate-950 shadow-md font-bold'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          <span>Custom Destination / Angle</span>
        </button>
      </div>

      {/* Form Container */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-6 shadow-xl">
        {mode === 'auto' ? (
          <div className="bg-slate-950/60 border border-slate-800/80 rounded-2xl p-5 text-xs text-slate-300 space-y-2">
            <h4 className="font-bold text-teal-300 flex items-center space-x-2 text-sm">
              <Globe className="w-4 h-4" />
              <span>Full Autonomous Mode Configured</span>
            </h4>
            <p>
              The system will automatically balance across the 10 global regions and 13 tourism categories, 
              query the database to exclude recently covered destinations, and produce a novel, fully-verified blog post.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="text-slate-400 font-semibold block mb-1.5">Destination Name</label>
              <input
                type="text"
                placeholder="e.g. Cappadocia Fairy Chimneys"
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white placeholder-slate-600 focus:outline-none focus:border-teal-500"
              />
            </div>

            <div>
              <label className="text-slate-400 font-semibold block mb-1.5">Country</label>
              <input
                type="text"
                placeholder="e.g. Turkey"
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white placeholder-slate-600 focus:outline-none focus:border-teal-500"
              />
            </div>

            <div>
              <label className="text-slate-400 font-semibold block mb-1.5">Target Global Region</label>
              <select
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-teal-500"
              >
                {GLOBAL_REGIONS.map(r => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-slate-400 font-semibold block mb-1.5">Tourism Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-teal-500"
              >
                {TOURISM_CATEGORIES.map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            <div className="sm:col-span-2">
              <label className="text-slate-400 font-semibold block mb-1.5">Unique Editorial Perspective (Optional)</label>
              <input
                type="text"
                placeholder="e.g. Exploring underground cave hotels and sunrise hot air balloon photography"
                value={uniqueAngle}
                onChange={(e) => setUniqueAngle(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white placeholder-slate-600 focus:outline-none focus:border-teal-500"
              />
            </div>
          </div>
        )}

        {/* Action Button */}
        <div className="flex items-center justify-between pt-4 border-t border-slate-800">
          <div className="text-xs text-slate-400">
            Quality Gate Threshold: <span className="font-bold text-teal-300">{qualityThreshold} / 10.0</span>
          </div>

          <button
            onClick={handleRunPipeline}
            disabled={running}
            className="flex items-center space-x-2 px-6 py-3 rounded-xl bg-teal-500 hover:bg-teal-400 disabled:opacity-40 disabled:cursor-not-allowed text-slate-950 text-xs font-extrabold transition-all shadow-lg shadow-teal-500/25"
          >
            {running ? (
              <>
                <RotateCw className="w-4 h-4 animate-spin" />
                <span>Agents Executing (~40s)...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                <span>Run Full LangGraph Pipeline</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Live Stage Progress Visualizer */}
      {(running || result) && (
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-6 shadow-xl animate-fadeIn">
          <h3 className="text-base font-bold text-white flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-teal-400 animate-ping" />
            <span>Multi-Agent Workflow Progress</span>
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
            {STAGES.map((stg, idx) => {
              const isPast = activeStage > idx + 1;
              const isCurrent = activeStage === idx + 1 && running;
              return (
                <div 
                  key={stg.id}
                  className={`p-3 rounded-xl border transition-all ${
                    isPast
                      ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                      : isCurrent
                      ? 'bg-teal-500/15 border-teal-500/40 text-teal-200 animate-pulse'
                      : 'bg-slate-950/60 border-slate-800/80 text-slate-500'
                  }`}
                >
                  <div className="flex items-center justify-between font-bold mb-1">
                    <span>{stg.label}</span>
                    {isPast && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                  </div>
                  <div className="text-[10px] opacity-80">{stg.desc}</div>
                </div>
              );
            })}
          </div>

          {/* Success Result Card */}
          {result && (
            <div className="p-5 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-xs text-slate-200 space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-bold text-emerald-400 text-sm flex items-center space-x-1.5">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Pipeline Succeeded: Status '{result.status}'</span>
                </span>
                <span className="px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-300 font-bold font-mono">
                  Score: {result.quality_score}/10.0
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-slate-300 pt-2 border-t border-emerald-500/20">
                <div>Title: <span className="text-white font-medium">{result.article_title}</span></div>
                <div>Destination: <span className="text-teal-300 font-medium">{result.destination}, {result.country}</span></div>
                <div>Word Count: <span className="text-white font-mono">{result.word_count} words</span></div>
                <div>Media: <span className="text-white font-mono">{result.images_count} verified images</span></div>
              </div>
            </div>
          )}

          {/* Error Card */}
          {error && (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-xs text-rose-300 flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
