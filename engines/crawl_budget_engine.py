from __future__ import annotations

from .common import load_json, save_json, now_iso


class CrawlBudgetEngine:
    def run(self):
        cfg = load_json("config.json")
        perf_doc = load_json("indexes/performance_index.json")
        perf = perf_doc.get("site", {})
        indexing = perf.get("indexing_rate", 0)
        trend = perf.get("impressions_trend", "unknown")
        data_status = perf_doc.get("data_status", "missing")
        min_scale = cfg.get("constraints", {}).get("min_indexing_rate_to_scale", 0.7)
        stop_index = cfg.get("constraints", {}).get("stop_indexing_rate", 0.65)

        if data_status != "ok":
            status = "throttle"
            daily = 0
            segment = "sitemap-observe-only.xml"
            reason = "no_analytics_data"
        elif indexing < stop_index or trend == "declining":
            status = "throttle"
            daily = 2
            segment = "sitemap-low-priority.xml"
            reason = "indexing_or_trend_risk"
        elif indexing < min_scale or trend == "flat":
            status = "hold"
            daily = 8
            segment = "sitemap-experiments.xml"
            reason = "below_scale_threshold"
        else:
            status = "scale"
            daily = 24
            segment = "sitemap-growth.xml"
            reason = "healthy"

        out = {
            "updated_at": now_iso(),
            "indexing_rate": indexing,
            "impressions_trend": trend,
            "status": status,
            "reason": reason,
            "target_new_pages_per_day": daily,
            "sitemap_segment": segment,
        }
        save_json("indexes/crawl_budget_index.json", out)
        return out
