from __future__ import annotations

from .common import load_json, save_json, now_iso


class ClusterPriorityEngine:
    def _cluster_key(self, kw: dict) -> str:
        rent_band = int(kw.get("rent", 0) // 250 * 250)
        salary_band = int(kw.get("salary", 0) // 10000 * 10000)
        return f"{kw.get('city','').lower()}|{salary_band}|{rent_band}|{kw.get('intent','unknown')}"

    def _aggregate_perf(self, cluster: dict, pages: list[dict], perf_map: dict) -> dict:
        city = cluster.get("city")
        intent = cluster.get("intent")
        matching = [p for p in pages if p.get("city") == city and p.get("intent") == intent]
        if not matching:
            return {"impressions": 0, "clicks": 0, "ctr": 0.0, "indexing_rate": 0.0, "observations": 0}

        impressions = 0
        clicks = 0
        indexed = 0
        for page in matching:
            m = perf_map.get(page.get("slug", ""), {})
            impressions += int(m.get("impressions", 0))
            clicks += int(m.get("clicks", 0))
            indexed += 1 if m.get("indexed") else 0

        ctr = (clicks / impressions) if impressions else 0.0
        return {
            "impressions": impressions,
            "clicks": clicks,
            "ctr": round(ctr, 4),
            "indexing_rate": round(indexed / max(len(matching), 1), 4),
            "observations": len(matching),
        }

    def run(self, keywords: list[dict]):
        perf = load_json("indexes/performance_index.json")
        page_index = load_json("indexes/page_index.json")
        perf_map = {p.get("slug"): p for p in perf.get("pages", [])}
        historical_ctr = perf.get("site", {}).get("ctr", 0)
        has_analytics = perf.get("decision_allowed", False)

        clusters_by_key = {}
        for kw in keywords:
            if kw.get("eligibility") == "BLOCK":
                continue
            key = self._cluster_key(kw)
            salary_band = int(kw.get("salary", 0) // 10000 * 10000)
            rent_band = int(kw.get("rent", 0) // 250 * 250)
            if key not in clusters_by_key:
                clusters_by_key[key] = {
                    "cluster_id": key,
                    "city": kw["city"],
                    "state": kw["state"],
                    "scenario": kw.get("intent", "unknown"),
                    "intent": kw["intent"],
                    "salary": kw["salary"],
                    "salary_band": salary_band,
                    "rent": kw["rent"],
                    "rent_band": rent_band,
                    "query": kw["query"],
                    "serp_difficulty": [],
                    "forum_ratio": [],
                    "queries": [],
                }
            rec = clusters_by_key[key]
            rec["serp_difficulty"].append(kw.get("serp_difficulty", 1))
            rec["forum_ratio"].append(kw.get("forum_ratio", 0))
            rec["queries"].append(kw.get("query"))

        clusters = []
        for rec in clusters_by_key.values():
            avg_difficulty = sum(rec["serp_difficulty"]) / max(len(rec["serp_difficulty"]), 1)
            avg_forum = sum(rec["forum_ratio"]) / max(len(rec["forum_ratio"]), 1)
            serp_component = (1 - avg_difficulty) * 0.45 + avg_forum * 0.35
            ctr_component = 0.2 if (has_analytics and historical_ctr > 0.03) else 0.0
            perf_agg = self._aggregate_perf(rec, page_index.get("pages", []), perf_map)
            performance_component = min(0.25, perf_agg["ctr"] * 1.5 + perf_agg["indexing_rate"] * 0.08)
            opportunity = serp_component + ctr_component + performance_component
            loser = perf_agg["observations"] > 0 and (perf_agg["impressions"] < 10 or perf_agg["ctr"] < 0.01)

            clusters.append(
                {
                    "cluster_id": rec["cluster_id"],
                    "city": rec["city"],
                    "state": rec["state"],
                    "intent": rec["intent"],
                    "scenario": rec["scenario"],
                    "salary": rec["salary"],
                    "salary_band": rec["salary_band"],
                    "rent": rec["rent"],
                    "rent_band": rec["rent_band"],
                    "query": rec["query"],
                    "priority_score": round(opportunity, 4),
                    "decision_context": "analytics_backed" if has_analytics else "serp_only",
                    "performance": perf_agg,
                    "eligible_for_expansion": perf_agg["ctr"] >= 0.04 and perf_agg["impressions"] >= 20 and perf_agg["indexing_rate"] >= 0.6,
                    "suppressed": loser,
                }
            )

        clusters.sort(key=lambda x: x["priority_score"], reverse=True)
        save_json("indexes/cluster_index.json", {"updated_at": now_iso(), "clusters": clusters})
        return clusters
