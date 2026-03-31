from __future__ import annotations

from .common import save_json, now_iso


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
        for page in pages:
            if page["slug"] in losers:
                continue
            for winner in winners[:4]:
                if winner != page["slug"]:
                    links.append({"from": page["slug"], "to": winner, "weight": round(scores.get(winner, 0.01) + 0.1, 3)})

        save_json("indexes/internal_link_index.json", {"updated_at": now_iso(), "links": links, "winner_slugs": winners, "suppressed": list(losers)})
        return links


    def build_link_graph(self, pages: list[dict], perf: dict | None = None) -> dict:
        perf = perf or {"pages": []}
        links = self.run(pages, perf)
        adjacency = {}
        for row in links:
            adjacency.setdefault(row["from"], []).append({"to": row["to"], "weight": row.get("weight", 0.1)})
        return {"nodes": len(pages), "edges": len(links), "adjacency": adjacency}

    def inject_internal_links(self, pages: list[dict], link_graph: dict) -> list[dict]:
        adjacency = link_graph.get("adjacency", {}) if isinstance(link_graph, dict) else {}
        enriched = []
        for page in pages:
            p = dict(page)
            p["internal_links_v2"] = adjacency.get(page.get("slug"), [])[:8]
            enriched.append(p)
        return enriched

    def optimize_internal_links(self, pages: list[dict], link_graph: dict) -> list[dict]:
        return self.inject_internal_links(pages, link_graph)
