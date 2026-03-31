from __future__ import annotations

from .common import load_json, now_iso, save_json


class StrategyControllerEngine:
    def prioritize_keywords(self, keywords: list[dict]) -> list[dict]:
        ranked = []
        for kw in keywords:
            difficulty = kw.get("serp_difficulty_blended", kw.get("serp_difficulty", 1)) or 1
            forum = kw.get("google_forum_ratio", kw.get("forum_ratio", 0)) or 0
            score = round((1 - difficulty) * 0.6 + forum * 0.25 + (0.15 if kw.get("eligibility") == "ALLOW" else 0), 4)
            ranked.append({**kw, "priority_score_v2": score})
        return sorted(ranked, key=lambda x: x.get("priority_score_v2", 0), reverse=True)

    def allocate_content_budget(self, prioritized_keywords: list[dict]) -> dict:
        budget = load_json("indexes/crawl_budget_index.json")
        status = budget.get("status", "throttle")
        max_new = 0 if status == "throttle" else (20 if status == "hold" else 80)
        selected = prioritized_keywords[:max_new]
        return {"status": status, "max_new_pages": max_new, "selected_keywords": len(selected), "selected": selected}

    def decide_cluster_expansion(self, clusters: list[dict]) -> dict:
        winners = [c for c in clusters if c.get("eligible_for_expansion")]
        return {
            "updated_at": now_iso(),
            "winner_clusters": len(winners),
            "expansion_recommended": len(winners) > 0,
            "top_winners": sorted(winners, key=lambda x: x.get("priority_score", 0), reverse=True)[:15],
        }

    def run(self, keywords: list[dict], clusters: list[dict]) -> dict:
        prioritized = self.prioritize_keywords(keywords)
        allocation = self.allocate_content_budget(prioritized)
        expansion = self.decide_cluster_expansion(clusters)
        out = {"updated_at": now_iso(), "allocation": allocation, "expansion": expansion}
        save_json("indexes/strategy_controller_v2.json", out)
        return out
