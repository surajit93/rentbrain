from __future__ import annotations

import csv
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any

from .common import ROOT, load_json, now_iso, save_json


class AnalyticsRealEngine:
    def fetch_gsc_data(self, site_url: str) -> dict[str, Any]:
        del site_url
        export_path = os.getenv("GSC_EXPORT_PATH", "logs/gsc_export.json")
        p = ROOT / export_path
        if not p.exists():
            return {"source_status": "missing", "rows": [], "path": str(p)}
        if p.suffix.lower() == ".csv":
            with p.open("r", encoding="utf-8", errors="ignore") as fh:
                rows = list(csv.DictReader(fh))
            return {"source_status": "ok", "rows": rows, "path": str(p)}
        try:
            payload = json.loads(p.read_text(encoding="utf-8", errors="ignore"))
            rows = payload.get("pages", []) if isinstance(payload, dict) else []
            return {"source_status": "ok", "rows": rows, "path": str(p)}
        except Exception as exc:
            return {"source_status": "error", "rows": [], "error": str(exc), "path": str(p)}

    def normalize_gsc_data(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        out = []
        for row in rows:
            slug = row.get("slug") or Path(str(row.get("page", "")).strip("/")).stem
            out.append(
                {
                    "slug": slug,
                    "query": row.get("query", ""),
                    "impressions": int(float(row.get("impressions", 0) or 0)),
                    "clicks": int(float(row.get("clicks", 0) or 0)),
                    "position": float(row.get("position", 0) or 0),
                    "ctr": float(row.get("ctr", 0) or 0),
                }
            )
        return [r for r in out if r.get("slug")]

    def map_page_performance(self, normalized: list[dict[str, Any]]) -> dict[str, Any]:
        agg: dict[str, dict[str, Any]] = defaultdict(lambda: {"impressions": 0, "clicks": 0, "positions": [], "queries": 0})
        for row in normalized:
            rec = agg[row["slug"]]
            rec["impressions"] += row["impressions"]
            rec["clicks"] += row["clicks"]
            if row.get("position"):
                rec["positions"].append(row["position"])
            rec["queries"] += 1
        mapped = []
        for slug, rec in agg.items():
            impr = rec["impressions"]
            clk = rec["clicks"]
            mapped.append(
                {
                    "slug": slug,
                    "impressions": impr,
                    "clicks": clk,
                    "ctr": round(clk / impr, 4) if impr else 0.0,
                    "avg_position": round(sum(rec["positions"]) / len(rec["positions"]), 2) if rec["positions"] else None,
                    "query_count": rec["queries"],
                }
            )
        return {"updated_at": now_iso(), "pages": sorted(mapped, key=lambda x: x["impressions"], reverse=True)}

    def run(self, site_url: str) -> dict[str, Any]:
        fetched = self.fetch_gsc_data(site_url)
        normalized = self.normalize_gsc_data(fetched.get("rows", [])) if fetched.get("source_status") == "ok" else []
        performance = self.map_page_performance(normalized)
        output = {
            "updated_at": now_iso(),
            "site_url": site_url,
            "source_status": fetched.get("source_status"),
            "source_path": fetched.get("path"),
            "rows": len(normalized),
            "pages": performance.get("pages", []),
        }
        save_json("logs/gsc_enriched.json", output)
        return output
