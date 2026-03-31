from __future__ import annotations

from .common import now_iso, save_json
from .serp_google_engine import compute_difficulty_score, extract_features, fetch_google_serp
from .serp_intelligence_engine import SerpIntelligenceEngine


def merge_with_existing_serp(ddg_results: list[dict], google_results: list[dict]) -> list[dict]:
    google_by_query = {r.get("query"): r for r in google_results}
    merged: list[dict] = []
    for row in ddg_results:
        query = row.get("query")
        g = google_by_query.get(query, {})
        g_rows = g.get("results", []) if isinstance(g, dict) else []
        g_features = extract_features(g_rows) if g_rows else {}
        g_difficulty = compute_difficulty_score(g_rows) if g_rows else row.get("serp_difficulty")
        merged.append(
            {
                **row,
                "google_provider": g.get("provider", "none"),
                "google_source_status": g.get("source_status", "missing"),
                "google_result_count": g_features.get("result_count", 0),
                "google_forum_ratio": g_features.get("forum_ratio", 0.0),
                "google_authority_count": g_features.get("authority_count", 0),
                "google_has_calculator": g_features.get("has_calculator", False),
                "serp_difficulty_v2": g_difficulty,
                "serp_difficulty_blended": round(((row.get("serp_difficulty") or 1.0) * 0.5 + (g_difficulty if g_difficulty is not None else (row.get("serp_difficulty") or 1.0)) * 0.5), 3),
            }
        )
    return merged


def normalize_signals(row: dict) -> dict:
    blended = row.get("serp_difficulty_blended", row.get("serp_difficulty", 1.0))
    forum = row.get("google_forum_ratio", row.get("forum_ratio", 0.0))
    authority = row.get("google_authority_count", row.get("high_authority_count", 0))
    normalized = dict(row)
    normalized["difficulty_normalized"] = round(min(1.0, max(0.0, float(blended or 0.0))), 3)
    normalized["forum_ratio_normalized"] = round(min(1.0, max(0.0, float(forum or 0.0))), 3)
    normalized["authority_count_normalized"] = int(max(0, authority or 0))
    return normalized


class SerpMergedEngine:
    def __init__(self):
        self.legacy = SerpIntelligenceEngine()

    def run(self, queries: list[dict]) -> list[dict]:
        ddg = self.legacy.run(queries)
        google = [fetch_google_serp((q if isinstance(q, str) else q.get("query", ""))) for q in queries]
        merged = [normalize_signals(r) for r in merge_with_existing_serp(ddg, google)]
        save_json("indexes/serp_index_v2.json", {"updated_at": now_iso(), "provider": "ddg+google", "queries": merged})
        return merged
