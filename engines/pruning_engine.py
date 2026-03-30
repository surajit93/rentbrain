from __future__ import annotations

from datetime import datetime, timezone


class PruningEngine:
    def _age_days(self, created_at: str) -> int:
        if not created_at:
            return 0
        try:
            dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            return (datetime.now(timezone.utc) - dt).days
        except Exception:
            return 0

    def run(self, pages: list[dict], perf: dict, prune_days: int = 60):
        perf_by_slug = {p["slug"]: p for p in perf.get("pages", [])}
        kept = []
        removed = []
        seen_keys = set()
        for page in pages:
            key = (page["city"], page["scenario"], int(page["rent"]), int(page["salary"]))
            metrics = perf_by_slug.get(page["slug"], {})
            age_days = self._age_days(page.get("created_at", ""))
            zero_impr = metrics.get("impressions", 0) == 0 and age_days >= prune_days
            low_ctr = metrics.get("ctr", 0) < 0.02 and metrics.get("impressions", 0) > 25
            duplicate = key in seen_keys
            if zero_impr or low_ctr or duplicate:
                removed.append(page["slug"])
                continue
            seen_keys.add(key)
            kept.append(page)
        return kept, removed
