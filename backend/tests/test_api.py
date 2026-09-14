def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_list_incidents(client):
    resp = client.get("/api/incidents")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0
    assert "category" in data[0]
    assert "severity" in data[0]


def test_filter_incidents_by_category(client):
    resp = client.get("/api/incidents", params={"category": "gas_leak"})
    assert resp.status_code == 200
    data = resp.json()
    assert all(row["category"] == "gas_leak" for row in data)


def test_incidents_pagination_and_total_count_header(client):
    resp = client.get("/api/incidents", params={"limit": 5, "offset": 0})
    assert resp.status_code == 200
    assert len(resp.json()) == 5
    total = int(resp.headers["X-Total-Count"])
    assert total >= 200  # 210 synthetic incidents seeded

    resp2 = client.get("/api/incidents", params={"limit": 5, "offset": 5})
    ids_page1 = {row["id"] for row in resp.json()}
    ids_page2 = {row["id"] for row in resp2.json()}
    assert ids_page1.isdisjoint(ids_page2)


def test_incidents_limit_is_capped(client):
    resp = client.get("/api/incidents", params={"limit": 10000})
    assert resp.status_code == 200
    assert len(resp.json()) <= 100


def test_incidents_filter_by_min_severity(client):
    resp = client.get("/api/incidents", params={"min_severity": 5, "limit": 100})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0
    assert all(row["severity"] >= 5 for row in data)


def test_incidents_search(client):
    resp = client.get("/api/incidents", params={"search": "hot work", "limit": 100})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0
    assert all("hot work" in row["description"].lower() for row in data)


def test_incidents_by_explicit_ids_preserves_order(client):
    resp = client.get("/api/incidents", params={"ids": "5,1,3"})
    assert resp.status_code == 200
    data = resp.json()
    assert [row["id"] for row in data] == [5, 1, 3]
    assert resp.headers["X-Total-Count"] == "3"


def test_x_total_count_is_cors_exposed(client):
    # Regression test: a browser's fetch() hides all response headers except
    # a small "safe" allowlist during a cross-origin request UNLESS the
    # server explicitly lists them in Access-Control-Expose-Headers. This
    # bit the frontend silently -- curl could see X-Total-Count, but the
    # browser could not, so pagination looked broken with no error anywhere.
    # Simulating a cross-origin request (an Origin header present) is what
    # makes CORSMiddleware add the expose-headers response header at all.
    resp = client.get(
        "/api/incidents",
        params={"limit": 5},
        headers={"Origin": "http://localhost:5173"},
    )
    assert resp.status_code == 200
    exposed = resp.headers.get("access-control-expose-headers", "")
    assert "X-Total-Count" in exposed


def test_get_incident_not_found(client):
    resp = client.get("/api/incidents/999999")
    assert resp.status_code == 404


def test_create_incident(client):
    payload = {
        "category": "hot_work",
        "category_label": "Hot Work / Ignition Source",
        "location": "Test Plant",
        "description": "Test incident created by pytest.",
        "severity": 2,
        "outcome": "Near miss - no injury",
        "days_ago": 0,
    }
    resp = client.post("/api/incidents", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["location"] == "Test Plant"
    assert body["id"] is not None


def test_ask_returns_grounded_answer_with_citations(client):
    resp = client.post("/api/ask", json={
        "question": "What atmosphere tests are required before confined space entry?",
        "top_k": 3,
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["mode"] in ("extractive", "generative (openai)")
    assert len(body["citations"]) == 3
    assert len(body["retrieved"]) == 3
    # The known-relevant regulation should be in the retrieved set for this query.
    doc_ids = [r["doc_id"] for r in body["retrieved"]]
    assert "OISD-STD-105-4.2" in doc_ids


def test_ask_rejects_empty_question(client):
    resp = client.post("/api/ask", json={"question": "   "})
    assert resp.status_code == 400


def test_top_risks_endpoint(client):
    resp = client.get("/api/analytics/top-risks")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 6  # 6 incident categories in the synthetic dataset
    scores = [row["priority_score"] for row in data]
    assert scores == sorted(scores, reverse=True)  # sorted descending
    assert max(scores) == 100.0  # normalized


def test_hotspots_endpoint(client):
    resp = client.get("/api/analytics/hotspots")
    assert resp.status_code == 200
    assert len(resp.json()) > 0


def test_regulations_endpoint(client):
    resp = client.get("/api/regulations")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 8
    assert all("source" in r for r in data)
