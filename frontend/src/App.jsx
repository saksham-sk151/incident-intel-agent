import { useEffect, useState } from "react";
import { askQuestion, getTopRisks } from "./api";
import RiskBarChart from "./RiskBarChart";
import IncidentBrowser from "./IncidentBrowser";
import Spinner from "./Spinner";
import { useTheme } from "./useTheme";
import "./App.css";

const SAMPLE_QUESTIONS = [
  "What atmosphere tests are required before confined space entry?",
  "Can hot work be permitted near a gas leak?",
  "How should electrical isolation be confirmed before work begins?",
  "Who is allowed to remove a lockout-tagout lock?",
];

function relatedIncidentIds(result) {
  if (!result) return [];
  return result.retrieved
    .filter((r) => r.doc_type === "incident")
    .map((r) => parseInt(r.doc_id.replace("incident-", ""), 10))
    .filter((n) => !Number.isNaN(n));
}

export default function App() {
  const { theme, toggleTheme } = useTheme();
  const [activeTab, setActiveTab] = useState("ask");

  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [risks, setRisks] = useState([]);
  const [risksError, setRisksError] = useState(null);

  const [relatedIds, setRelatedIds] = useState(null);

  useEffect(() => {
    getTopRisks().then(setRisks).catch((e) => setRisksError(e.message));
  }, []);

  async function handleAsk(e) {
    e.preventDefault();
    if (!question.trim() || loading) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await askQuestion(question, 5);
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  function viewRelatedReports() {
    setRelatedIds(relatedIncidentIds(result));
    setActiveTab("incidents");
  }

  const related = relatedIncidentIds(result);

  return (
    <div className="app">
      <header>
        <div className="header-row">
          <div>
            <h1>Industrial Incident Pattern Intelligence</h1>
            <p className="subtitle">
              RAG-powered Q&amp;A over synthetic near-miss reports and safety
              regulations (OISD / Factories Act) — with cited sources.
            </p>
          </div>
          <button
            type="button"
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
            title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
          >
            {theme === "dark" ? "☀️" : "🌙"}
          </button>
        </div>
      </header>

      <nav className="tabs">
        <button
          type="button"
          className={activeTab === "ask" ? "tab active" : "tab"}
          onClick={() => setActiveTab("ask")}
        >
          Ask
        </button>
        <button
          type="button"
          className={activeTab === "incidents" ? "tab active" : "tab"}
          onClick={() => {
            setRelatedIds(null);
            setActiveTab("incidents");
          }}
        >
          Incident reports
        </button>
      </nav>

      {activeTab === "ask" && (
        <>
          <section className="card">
            <h2>Ask a safety question</h2>
            <form onSubmit={handleAsk}>
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="e.g. What atmosphere tests are required before confined space entry?"
                disabled={loading}
              />
              <button type="submit" disabled={loading}>
                {loading ? "Asking…" : "Ask"}
              </button>
            </form>
            <div className="sample-questions">
              {SAMPLE_QUESTIONS.map((q) => (
                <button
                  key={q}
                  className="chip"
                  onClick={() => setQuestion(q)}
                  type="button"
                  disabled={loading}
                >
                  {q}
                </button>
              ))}
            </div>

            {loading && <Spinner />}

            {error && <p className="error">Error: {error} (is the backend running on :8000?)</p>}

            {result && !loading && (
              <div className="answer-block fade-in">
                <p className="mode-tag">
                  mode: {result.mode} · {result.latency_ms} ms
                </p>
                <p className="answer-text">{result.answer}</p>

                {related.length > 0 && (
                  <button type="button" className="related-cta" onClick={viewRelatedReports}>
                    View {related.length} related incident report{related.length !== 1 ? "s" : ""} →
                  </button>
                )}

                <h3>Sources</h3>
                <ul className="citation-list">
                  {result.retrieved.map((r) => (
                    <li key={r.doc_id}>
                      <span className={`doc-type ${r.doc_type}`}>{r.doc_type}</span>{" "}
                      <strong>{r.source}</strong> (score {r.score})
                      <div className="passage-text">{r.text}</div>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </section>

          <section className="card">
            <h2>Top recurring risk categories</h2>
            <p className="subtitle">
              Severity- and recency-weighted priority score across 210
              synthetic near-miss reports (see README for the scoring
              formula).
            </p>
            {risksError && <p className="error">Error loading analytics: {risksError}</p>}
            <RiskBarChart data={risks} />
          </section>
        </>
      )}

      {activeTab === "incidents" && (
        <IncidentBrowser relatedIds={relatedIds} onClearRelated={() => setRelatedIds(null)} />
      )}

      <footer>
        <p>
          All incident data is synthetic and illustrative — see the project
          README for full data provenance.
        </p>
      </footer>
    </div>
  );
}
