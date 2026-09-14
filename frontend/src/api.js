const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const resp = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!resp.ok) {
    const body = await resp.text();
    throw new Error(`${resp.status} ${resp.statusText}: ${body}`);
  }
  return resp.json();
}

// Like request(), but also returns the X-Total-Count header -- needed for
// pagination in the incident browser, where the response body is only the
// current page.
async function requestWithCount(path, options = {}) {
  const resp = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!resp.ok) {
    const body = await resp.text();
    throw new Error(`${resp.status} ${resp.statusText}: ${body}`);
  }
  const data = await resp.json();
  const total = Number(resp.headers.get("X-Total-Count") ?? data.length);
  return { data, total };
}

export function askQuestion(question, topK = 5) {
  return request("/api/ask", {
    method: "POST",
    body: JSON.stringify({ question, top_k: topK }),
  });
}

export function getTopRisks() {
  return request("/api/analytics/top-risks");
}

export function getHotspots() {
  return request("/api/analytics/hotspots");
}

export function getRegulations() {
  return request("/api/regulations");
}

/**
 * filters: { category, location, minSeverity, search, ids, limit, offset }
 * ids, when provided, is an array of incident ids -- the backend returns
 * exactly those rows (in that order) and ignores the other filters, which
 * is what powers "view the reports that were cited in this answer".
 */
export function getIncidents(filters = {}) {
  const params = new URLSearchParams();
  if (filters.category) params.set("category", filters.category);
  if (filters.location) params.set("location", filters.location);
  if (filters.minSeverity) params.set("min_severity", filters.minSeverity);
  if (filters.search) params.set("search", filters.search);
  if (filters.ids && filters.ids.length > 0) params.set("ids", filters.ids.join(","));
  params.set("limit", filters.limit ?? 20);
  params.set("offset", filters.offset ?? 0);
  return requestWithCount(`/api/incidents?${params.toString()}`);
}
