import { useEffect, useState, useCallback } from "react";
import { getIncidents, getTopRisks, getHotspots } from "./api";

const PAGE_SIZE = 10;

function severityClass(sev) {
  if (sev >= 4) return "sev-high";
  if (sev === 3) return "sev-mid";
  return "sev-low";
}

export default function IncidentBrowser({ relatedIds, onClearRelated }) {
  const [categories, setCategories] = useState([]);
  const [locations, setLocations] = useState([]);

  const [category, setCategory] = useState("");
  const [location, setLocation] = useState("");
  const [minSeverity, setMinSeverity] = useState("");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);

  const [incidents, setIncidents] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const isRelatedView = relatedIds && relatedIds.length > 0;

  useEffect(() => {
    getTopRisks().then((rows) => setCategories(rows)).catch(() => {});
    getHotspots().then((rows) => setLocations(rows)).catch(() => {});
  }, []);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    const filters = isRelatedView
      ? { ids: relatedIds }
      : {
          category: category || undefined,
          location: location || undefined,
          minSeverity: minSeverity || undefined,
          search: search || undefined,
          limit: PAGE_SIZE,
          offset: page * PAGE_SIZE,
        };
    getIncidents(filters)
      .then(({ data, total }) => {
        setIncidents(data);
        setTotal(total);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [isRelatedView, relatedIds, category, location, minSeverity, search, page]);

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [category, location, minSeverity, search, page, relatedIds]);

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  function resetToFirstPage(setter) {
    return (e) => {
      setter(e.target.value);
      setPage(0);
    };
  }

  return (
    <section className="card">
      <h2>Incident reports</h2>

      {isRelatedView ? (
        <div className="related-banner">
          <span>
            Showing {relatedIds.length} report{relatedIds.length !== 1 ? "s" : ""} cited
            in your last answer.
          </span>
          <button type="button" className="link-button" onClick={onClearRelated}>
            Clear filter — browse all {total > 0 ? total : ""} reports
          </button>
        </div>
      ) : (
        <div className="filter-bar">
          <select value={category} onChange={resetToFirstPage(setCategory)}>
            <option value="">All categories</option>
            {categories.map((c) => (
              <option key={c.category} value={c.category}>
                {c.category_label}
              </option>
            ))}
          </select>

          <select value={location} onChange={resetToFirstPage(setLocation)}>
            <option value="">All locations</option>
            {locations.map((l) => (
              <option key={l.location} value={l.location}>
                {l.location}
              </option>
            ))}
          </select>

          <select value={minSeverity} onChange={resetToFirstPage(setMinSeverity)}>
            <option value="">Any severity</option>
            <option value="3">Severity 3+</option>
            <option value="4">Severity 4+</option>
            <option value="5">Severity 5 only</option>
          </select>

          <input
            type="text"
            placeholder="Search description…"
            value={search}
            onChange={resetToFirstPage(setSearch)}
          />
        </div>
      )}

      {error && <p className="error">Error loading incidents: {error}</p>}

      {loading ? (
        <div className="skeleton-list">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="skeleton-card" />
          ))}
        </div>
      ) : (
        <>
          <div className="incident-grid">
            {incidents.map((inc) => (
              <article key={inc.id} className="incident-card">
                <div className="incident-card-top">
                  <span className={`severity-badge ${severityClass(inc.severity)}`}>
                    Severity {inc.severity}
                  </span>
                  <span className="incident-id">#{inc.id}</span>
                </div>
                <h3>{inc.category_label}</h3>
                <p className="incident-desc">{inc.description}</p>
                <div className="incident-meta">
                  <span>📍 {inc.location}</span>
                  <span>{inc.outcome}</span>
                  <span>{inc.days_ago === 0 ? "today" : `${inc.days_ago}d ago`}</span>
                </div>
              </article>
            ))}
            {incidents.length === 0 && <p className="empty-state">No incidents match these filters.</p>}
          </div>

          {!isRelatedView && total > PAGE_SIZE && (
            <div className="pagination">
              <button type="button" disabled={page === 0} onClick={() => setPage((p) => p - 1)}>
                ← Prev
              </button>
              <span>
                Page {page + 1} of {totalPages} ({total} reports)
              </span>
              <button
                type="button"
                disabled={page >= totalPages - 1}
                onClick={() => setPage((p) => p + 1)}
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}
    </section>
  );
}
