from __future__ import annotations

import os

from .common import load_json, save_json, now_iso


class AnalyticsEngine:
    def _load_gsc_export(self) -> dict:
        gsc_file = os.getenv("GSC_EXPORT_PATH", "logs/gsc_export.json")
        return load_json(gsc_file) if gsc_file else {}

    def run(self, pages: list[dict]) -> dict:
        gsc = self._load_gsc_export()
        gsc_pages = gsc.get("pages", []) if isinstance(gsc, dict) else []
        by_slug = {row.get("slug"): row for row in gsc_pages if row.get("slug")}

        page_metrics = []
        indexed_count = 0
        total_impr = 0
        total_clicks = 0
        for p in pages:
            m = by_slug.get(p["slug"], {})
            impressions = int(m.get("impressions", 0))
            clicks = int(m.get("clicks", 0))
            indexed = bool(m.get("indexed", False))
            ctr = (clicks / impressions) if impressions else 0.0
            total_impr += impressions
            total_clicks += clicks
            indexed_count += 1 if indexed else 0
            page_metrics.append(
                {
                    "slug": p["slug"],
                    "indexed": indexed,
                    "impressions": impressions,
                    "clicks": clicks,
                    "ctr": round(ctr, 4),
                }
            )

        indexing_rate = indexed_count / max(len(pages), 1)
        site_ctr = total_clicks / max(total_impr, 1)
        has_real_data = bool(gsc_pages)
        trend = gsc.get("impressions_trend", "unknown") if has_real_data else "unknown"
        out = {
            "updated_at": now_iso(),
            "source": "gsc_export" if has_real_data else "no_gsc_data",
            "data_status": "ok" if has_real_data else "missing",
            "decision_allowed": has_real_data,
            "pages": page_metrics,
            "site": {
                "indexing_rate": round(indexing_rate, 3),
                "impressions": total_impr,
                "clicks": total_clicks,
                "ctr": round(site_ctr, 4),
                "impressions_trend": trend,
            },
        }
        save_json("indexes/performance_index.json", out)
        return out
