import { useState, useCallback } from 'react';
import { getRecommendations } from './api/recommend';
import { FILTER_OPTIONS } from './constants/filterOptions';
import type { RecommendationItem } from './types';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [jdUrl, setJdUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    job_family: [] as string[],
    job_level: [] as string[],
    industry: [] as string[],
    language: [] as string[],
    job_category: [] as string[],
  });

  const fetchJdText = useCallback(async (url: string): Promise<string> => {
    const res = await fetch(url, { mode: 'cors' });
    if (!res.ok) throw new Error('Could not fetch URL');
    const html = await res.text();
    const doc = new DOMParser().parseFromString(html, 'text/html');
    const text = doc.body?.textContent?.replace(/\s+/g, ' ').trim() ?? '';
    return text.slice(0, 4000);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    let q = query.trim();
    if (jdUrl.trim()) {
      try {
        const jdText = await fetchJdText(jdUrl.trim());
        q = q ? `${q}\n\n${jdText.slice(0, 2000)}` : jdText;
      } catch {
        setError('Could not fetch job description URL. Using query only.');
      }
    }
    if (!q) {
      setError('Please enter a query.');
      return;
    }
    setLoading(true);
    try {
      const payload = {
        query: q,
        top_k: 10,
        job_family: filters.job_family.length ? filters.job_family : undefined,
        job_level: filters.job_level.length ? filters.job_level : undefined,
        industry: filters.industry.length ? filters.industry : undefined,
        language: filters.language.length ? filters.language : undefined,
        job_category: filters.job_category.length ? filters.job_category : undefined,
      };
      const recs = await getRecommendations(payload);
      setRecommendations(recs);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get recommendations.');
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-brand">
          <a href="https://www.shl.com" target="_blank" rel="noopener noreferrer" className="logo-link">
            <img src="/shl-logo.png" alt="SHL" className="logo" />
          </a>
          <span className="header-tagline">From assessment to intelligence</span>
        </div>
        <h1>Assessment Recommendation</h1>
        <p className="subtitle">Enter a job query or description to get recommended SHL assessments.</p>
      </header>

      <form onSubmit={handleSubmit} className="form">
        <div className="form-two-col">
          <div className="form-col form-col-left">
            <label className="label">
              Query
              <textarea
                className="textarea"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., I am hiring for Java developers who can collaborate..."
                rows={5}
              />
            </label>
          </div>
          <div className="form-col form-col-right">
            <label className="label">
              Job description URL (optional)
              <input
                type="url"
                className="input"
                value={jdUrl}
                onChange={(e) => setJdUrl(e.target.value)}
                placeholder="https://..."
              />
            </label>
            <div className="filters-section">
              <button
                type="button"
                className="filters-toggle"
                onClick={() => setShowFilters((v) => !v)}
                aria-expanded={showFilters}
              >
                {showFilters ? '▼' : '▶'} Filters (Job Family, Level, Industry, etc.)
              </button>
              {showFilters && (
                <div className="filters-grid">
                  {(['job_family', 'job_level', 'industry', 'language', 'job_category'] as const).map(
                    (key) => (
                      <div key={key} className="filter-group">
                        <span className="filter-label">
                          {key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                        </span>
                        <select
                          multiple
                          className="filter-select"
                          value={filters[key]}
                          onChange={(e) => {
                            const opts = Array.from(e.target.selectedOptions, (o) => o.value);
                            setFilters((prev) => ({ ...prev, [key]: opts }));
                          }}
                        >
                          {FILTER_OPTIONS[key].map((opt) => (
                            <option key={opt} value={opt}>
                              {opt}
                            </option>
                          ))}
                        </select>
                      </div>
                    )
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
        <div className="form-actions">
          <button type="submit" className="submit" disabled={loading}>
            {loading ? 'Fetching…' : 'Get Recommendations'}
          </button>
        </div>
      </form>

      {error && <div className="error" role="alert">{error}</div>}

      {recommendations.length > 0 && (
        <section className="results">
          <h2>Recommendations</h2>
          <ol className="result-list">
            {recommendations.map((r, i) => (
              <li key={`${r.assessment_url}-${i}`} className="result-item">
                <div className="result-title">
                  <strong>{i + 1}. {r.assessment_name}</strong>
                  {r.score != null && (
                    <span className="score"> Score: {r.score.toFixed(3)}</span>
                  )}
                </div>
                {r.test_type?.length > 0 && (
                  <div className="result-meta">Test type: {r.test_type.join(', ')}</div>
                )}
                <a href={r.assessment_url} target="_blank" rel="noopener noreferrer" className="result-link">
                  {r.assessment_url}
                </a>
              </li>
            ))}
          </ol>
        </section>
      )}
    </div>
  );
}

export default App;
