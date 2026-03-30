from __future__ import annotations

from .common import load_json, save_json, now_iso


class ClusterPriorityEngine:
    def run(self, keywords: list[dict]):
        perf = load_json("indexes/performance_index.json")
        historical_ctr = perf.get("site", {}).get("ctr", 0)
        clusters = []
        for kw in keywords:
            opportunity = (1 - kw.get("serp_difficulty", 1)) * 0.5 + kw.get("forum_ratio", 0) * 0.3 + (0.2 if historical_ctr > 0.03 else 0.05)
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
                }
            )
        clusters.sort(key=lambda x: x["priority_score"], reverse=True)
        save_json("indexes/cluster_index.json", {"updated_at": now_iso(), "clusters": clusters})
        return clusters
