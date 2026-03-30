from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import quote_plus, urlparse
from urllib.request import Request, urlopen

from .common import now_iso, save_json


AUTHORITY_DOMAINS = {
    "zillow.com",
    "bankrate.com",
    "nerdwallet.com",
    "apartments.com",
    "realtor.com",
    "rocketmortgage.com",
}
FORUM_DOMAINS = {"reddit.com", "quora.com"}


class _DuckResultParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results = []
        self._in_link = False
        self._href = None

    def handle_starttag(self, tag, attrs):
        attrs_map = dict(attrs)
        if tag == "a" and "result-link" in attrs_map.get("class", ""):
            self._in_link = True
            self._href = attrs_map.get("href", "")

    def handle_endtag(self, tag):
        if tag == "a":
            self._in_link = False

    def handle_data(self, data):
        if self._in_link and self._href and data.strip():
            self.results.append({"title": data.strip(), "url": self._href})
            self._href = None


@dataclass
class SerpEvaluation:
    query: str
    top_domains: list[str]
    features: list[str]
    authority_count: int
    forum_ratio: float
    has_calculator: bool
    weak_signal_score: float
    serp_difficulty: float | None
    classification: str
    eligibility: str
    fetched_at: str
    source_status: str
    fetch_error: str | None
    result_count: int


class SerpIntelligenceEngine:
    def _fetch_duckduckgo(self, query: str) -> list[dict]:
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=12) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        parser = _DuckResultParser()
        parser.feed(html)
        return parser.results[:10]

    def _root_domain(self, url: str) -> str:
        return urlparse(url).netloc.lower().replace("www.", "")

    def _analyze(self, query: str, rows: list[dict], source_status: str, fetch_error: str | None) -> SerpEvaluation:
        domains = [self._root_domain(r.get("url", "")) for r in rows if r.get("url")]
        domains = [d for d in domains if d]
        authority = sum(1 for d in domains if d in AUTHORITY_DOMAINS)
        forum_hits = sum(1 for d in domains if d in FORUM_DOMAINS or "forum" in d)
        forum_ratio = forum_hits / max(len(domains), 1)
        titles = " ".join(r.get("title", "").lower() for r in rows)
        has_calculator = "calculator" in titles or "estimate" in titles

        features = []
        if any("reddit.com" in d for d in domains):
            features.append("reddit")
        if any("quora.com" in d for d in domains):
            features.append("quora")
        if forum_hits:
            features.append("forum")
        if has_calculator:
            features.append("calculator")
        if domains and authority == 0:
            features.append("weak_blog")

        if source_status != "ok":
            classification = "unknown"
            difficulty = None
            weak_signal = 0.0
            eligibility = "BLOCK"
        elif not domains:
            classification = "unknown"
            difficulty = None
            weak_signal = 0.0
            eligibility = "BLOCK"
        else:
            weak_signal = min(1.0, 0.55 * forum_ratio + 0.45 * (1 - min(authority / 4, 1)))
            difficulty = min(1.0, 0.6 * min(authority / 4, 1) + 0.4 * (1 - forum_ratio))
            if difficulty < 0.35:
                classification = "weak"
            elif difficulty < 0.65:
                classification = "mixed"
            else:
                classification = "strong"
            eligibility = "ALLOW" if classification == "weak" and not has_calculator else "BLOCK"

        return SerpEvaluation(
            query=query,
            top_domains=domains,
            features=features,
            authority_count=authority,
            forum_ratio=round(forum_ratio, 3),
            has_calculator=has_calculator,
            weak_signal_score=round(weak_signal, 3),
            serp_difficulty=round(difficulty, 3) if difficulty is not None else None,
            classification=classification,
            eligibility=eligibility,
            fetched_at=now_iso(),
            source_status=source_status,
            fetch_error=fetch_error,
            result_count=len(domains),
        )

    def run(self, queries: list[dict]) -> list[dict]:
        evaluated = []
        for item in queries:
            query = item["query"] if isinstance(item, dict) else str(item)
            source_status = "ok"
            err = None
            try:
                rows = self._fetch_duckduckgo(query)
            except Exception as ex:
                rows = []
                source_status = "error"
                err = str(ex)
            record = self._analyze(query, rows, source_status, err)
            payload = record.__dict__
            if isinstance(item, dict):
                payload.update({k: v for k, v in item.items() if k != "query"})
            evaluated.append(payload)

        save_json("indexes/serp_index.json", {"queries": evaluated, "updated_at": now_iso(), "provider": "duckduckgo_html"})
        return evaluated
