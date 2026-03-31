from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote_plus, urlparse
from urllib.request import Request, urlopen

from .common import now_iso


@dataclass
class GoogleSerpRecord:
    query: str
    results: list[dict[str, Any]]
    provider: str
    source_status: str
    fetch_error: str | None
    fetched_at: str


def _normalize_items(items: list[dict[str, Any]]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for row in items:
        url = row.get("link") or row.get("url") or ""
        title = row.get("title") or row.get("snippet") or ""
        if url:
            normalized.append({"title": str(title), "url": str(url)})
    return normalized[:10]


def fetch_google_serp(query: str) -> dict[str, Any]:
    api_key = os.getenv("SERPAPI_KEY", "").strip()
    cx = os.getenv("GOOGLE_CSE_CX", "").strip()
    cse_key = os.getenv("GOOGLE_CSE_API_KEY", "").strip()
    provider = "none"
    try:
        if api_key:
            provider = "serpapi"
            url = f"https://serpapi.com/search.json?engine=google&q={quote_plus(query)}&num=10&api_key={api_key}"
            req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=15) as resp:
                payload = json.loads(resp.read().decode("utf-8", errors="ignore"))
            items = payload.get("organic_results", [])
            rows = _normalize_items(items)
            return GoogleSerpRecord(query=query, results=rows, provider=provider, source_status="ok", fetch_error=None, fetched_at=now_iso()).__dict__

        if cx and cse_key:
            provider = "google_cse"
            url = f"https://www.googleapis.com/customsearch/v1?q={quote_plus(query)}&cx={cx}&key={cse_key}&num=10"
            req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=15) as resp:
                payload = json.loads(resp.read().decode("utf-8", errors="ignore"))
            rows = _normalize_items(payload.get("items", []))
            return GoogleSerpRecord(query=query, results=rows, provider=provider, source_status="ok", fetch_error=None, fetched_at=now_iso()).__dict__

        return GoogleSerpRecord(query=query, results=[], provider=provider, source_status="missing_api", fetch_error="missing SERPAPI_KEY or GOOGLE_CSE credentials", fetched_at=now_iso()).__dict__
    except Exception as exc:  # failure-safe fallback
        return GoogleSerpRecord(query=query, results=[], provider=provider, source_status="error", fetch_error=str(exc), fetched_at=now_iso()).__dict__


def extract_features(results: list[dict[str, Any]]) -> dict[str, Any]:
    domains = [urlparse(r.get("url", "")).netloc.lower().replace("www.", "") for r in results if r.get("url")]
    domains = [d for d in domains if d]
    forum_hits = sum(1 for d in domains if d in {"reddit.com", "quora.com"} or "forum" in d)
    authority_hits = sum(1 for d in domains if d in {"zillow.com", "bankrate.com", "nerdwallet.com", "apartments.com", "realtor.com"})
    return {
        "top_domains": domains,
        "forum_ratio": round(forum_hits / max(len(domains), 1), 3),
        "authority_count": authority_hits,
        "has_calculator": any("calculator" in str(r.get("title", "")).lower() for r in results),
        "result_count": len(domains),
    }


def compute_difficulty_score(results: list[dict[str, Any]]) -> float:
    features = extract_features(results)
    authority_component = min(features["authority_count"] / 4, 1)
    forum_component = 1 - features["forum_ratio"]
    calculator_component = 0.15 if features["has_calculator"] else 0.0
    return round(min(1.0, 0.55 * authority_component + 0.35 * forum_component + calculator_component), 3)
