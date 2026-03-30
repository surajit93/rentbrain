from __future__ import annotations

from .common import load_json, save_json, now_iso


class CrawlBudgetEngine:
    def run(self):
        cfg = load_json("config.json")
        perf = load_json("indexes/performance_index.json").get("site", {})
        indexing = perf.get("indexing_rate", 0)
        trend = perf.get("impressions_trend", "flat")
        min_scale = cfg.get("constraints", {}).get("min_indexing_rate_to_scale", 0.7)
        stop_index = cfg.get("constraints", {}).get("stop_indexing_rate", 0.65)

        if indexing < stop_index or trend == "declining":
            status = "throttle"
            daily = 2
            segment = "sitemap-low-priority.xml"
        elif indexing < min_scale or trend == "flat":
            status = "hold"
            daily = 8
            segment = "sitemap-experiments.xml"
        else:
            status = "scale"
            daily = 24
            segment = "sitemap-growth.xml"

        out = {
            "updated_at": now_iso(),
            "indexing_rate": indexing,
            "impressions_trend": trend,
            "status": status,
            "target_new_pages_per_day": daily,
            "sitemap_segment": segment,
        }
        save_json("indexes/crawl_budget_index.json", out)
        return out
