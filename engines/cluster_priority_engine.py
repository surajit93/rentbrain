from __future__ import annotations

from .common import load_json, save_json, now_iso


class ClusterPriorityEngine:
    def run(self, keywords: list[dict]):
        perf = load_json("indexes/performance_index.json")
        historical_ctr = perf.get("site", {}).get("ctr", 0)
        has_analytics = perf.get("decision_allowed", False)
        clusters = []
        for kw in keywords:
            if kw.get("eligibility") == "BLOCK":
                continue
            serp_component = (1 - kw.get("serp_difficulty", 1)) * 0.5 + kw.get("forum_ratio", 0) * 0.35
            ctr_component = 0.15 if (has_analytics and historical_ctr > 0.03) else 0.03
            opportunity = serp_component + ctr_component
            clusters.append(
                {
                    "cluster_id": f"{kw['city'].lower()}-{kw['intent']}",
                    "city": kw["city"],
                    "state": kw["state"],
                    "intent": kw["intent"],
                    "salary": kw["salary"],
                    "rent": kw["rent"],
                    "query": kw["query"],
                    "priority_score": round(opportunity, 3),
                    "decision_context": "analytics_backed" if has_analytics else "serp_only",
                }
            )
        clusters.sort(key=lambda x: x["priority_score"], reverse=True)
        save_json("indexes/cluster_index.json", {"updated_at": now_iso(), "clusters": clusters})
        return clusters
