from __future__ import annotations

from .common import save_json, now_iso
from .seo_intent_engine import build_intent_links, city_slug


def generate_links(current_slug, all_slugs):
    related = [s for s in all_slugs if s != current_slug][:3]
    parents = all_slugs[:2]
    return parents + related


class InternalLinkingEngine:
    def run(self, pages: list[dict], perf: dict):
        metrics = {p["slug"]: p for p in perf.get("pages", [])}
        scores = {}
        for page in pages:
            m = metrics.get(page["slug"], {})
            scores[page["slug"]] = 0.4 * m.get("ctr", 0) + 0.6 * (m.get("impressions", 0) / 500)

        links = []
        winners = sorted(scores, key=lambda s: scores[s], reverse=True)[: max(3, len(scores) // 5)]
        losers = {slug for slug, val in scores.items() if val < 0.03}
        city_rows = [
            {
                "city": p.get("city"),
                "state": p.get("state"),
                "median_rent": p.get("rent", 0),
                "median_salary": p.get("salary", 0),
            }
            for p in pages
            if p.get("city") and p.get("state")
        ]

        for page in pages:
            if page["slug"] in losers:
                continue
            for winner in winners[:4]:
                if winner != page["slug"]:
                    links.append({"from": page["slug"], "to": winner, "weight": round(scores.get(winner, 0.01) + 0.1, 3), "reason": "performance_hub"})

            local_row = {
                "city": page.get("city"),
                "state": page.get("state"),
                "median_rent": page.get("rent", 0),
                "median_salary": page.get("salary", 0),
            }
            city_intent = build_intent_links(local_row, city_rows)
            for link in city_intent["intent_pages"]:
                links.append({"from": page["slug"], "to": link.lstrip("/"), "weight": 0.16, "reason": "city_intent"})
            links.append({"from": page["slug"], "to": city_intent["benchmark_page"].lstrip("/"), "weight": 0.19, "reason": "benchmark_reference"})

        save_json(
            "indexes/internal_link_index.json",
            {
                "updated_at": now_iso(),
                "links": links,
                "winner_slugs": winners,
                "suppressed": list(losers),
                "topical_clusters": ["Rent", "Cost of Living", "Trends", "Affordability"],
            },
        )
        return links

    def build_link_graph(self, pages: list[dict], perf: dict | None = None) -> dict:
        perf = perf or {"pages": []}
        links = self.run(pages, perf)
        adjacency = {}
        for row in links:
            adjacency.setdefault(row["from"], []).append({"to": row["to"], "weight": row.get("weight", 0.1), "reason": row.get("reason", "contextual")})
        return {"nodes": len(pages), "edges": len(links), "adjacency": adjacency}

    def inject_internal_links(self, pages: list[dict], link_graph: dict) -> list[dict]:
        adjacency = link_graph.get("adjacency", {}) if isinstance(link_graph, dict) else {}
        enriched = []
        for page in pages:
            p = dict(page)
            p["internal_links_v2"] = adjacency.get(page.get("slug"), [])[:8]
            p.setdefault("cluster", "Affordability")
            enriched.append(p)
        return enriched

    def optimize_internal_links(self, pages: list[dict], link_graph: dict) -> list[dict]:
        return self.inject_internal_links(pages, link_graph)

    def build_city_to_intent_links(self, city_rows: list[dict]) -> list[dict]:
        links = []
        for row in city_rows:
            base = city_slug(str(row.get("city", "")))
            links.extend(
                [
                    {"from": f"rent-benchmark-{base}", "to": f"average-rent-in-{base}", "reason": "intent_spoke"},
                    {"from": f"rent-benchmark-{base}", "to": f"cost-of-living-{base}", "reason": "intent_spoke"},
                    {"from": f"rent-benchmark-{base}", "to": f"rent-trends-{base}", "reason": "intent_spoke"},
                    {"from": f"rent-benchmark-{base}", "to": f"rent-vs-income-{base}", "reason": "intent_spoke"},
                ]
            )
        return links
