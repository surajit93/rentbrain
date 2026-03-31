from __future__ import annotations

import json
from pathlib import Path

from .common import ROOT, load_json, now_iso
from .seo_intent_engine import build_city_context, insight_blocks, meta_for_page


class ContentDifferentiationEngine:
    def _city_lookup(self) -> dict[str, dict]:
        cities = load_json("data/city_index.json").get("cities", [])
        return {str(c.get("city", "")).lower(): c for c in cities}

    def _enrich_page(self, page: dict, city_index: list[dict], city_lookup: dict[str, dict], page_kind: str) -> dict:
        city_name = str(page.get("city") or "")
        row = city_lookup.get(city_name.lower())
        if not row:
            return page
        context = build_city_context(row, city_index)
        enriched = dict(page)
        enriched.setdefault("insight_blocks", insight_blocks(context, page_kind))
        enriched.setdefault("meta", meta_for_page(context, str(page.get("title", city_name)), page_kind if page_kind != "benchmark" else "benchmark"))
        enriched.setdefault(
            "heading_hierarchy",
            {
                "h1": str(page.get("title", f"{city_name} housing overview")),
                "h2": ["City snapshot", "Affordability insight", "National comparison", "Related pages"],
            },
        )
        enriched["updated_at"] = now_iso()
        return enriched

    def run(self) -> dict:
        cities = load_json("data/city_index.json").get("cities", [])
        city_lookup = self._city_lookup()

        page_files = sorted((ROOT / "pages").glob("*.json"))
        authority_files = sorted((ROOT / "authority_pages").glob("*.json"))
        updated = {"pages": 0, "authority_pages": 0}

        for file in page_files:
            page = json.loads(file.read_text())
            page_kind = str(page.get("intent", "affordability"))
            enriched = self._enrich_page(page, cities, city_lookup, page_kind)
            if enriched != page:
                file.write_text(json.dumps(enriched, indent=2))
                updated["pages"] += 1

        for file in authority_files:
            page = json.loads(file.read_text())
            city_name = str(page.get("city", ""))
            if not city_name and str(page.get("slug", "")).startswith("rent-benchmark-"):
                city_name = str(page.get("slug", "")).replace("rent-benchmark-", "").replace("-", " ").title()
            kind = str(page.get("intent_type", "benchmark"))
            enriched = self._enrich_page({**page, "city": city_name}, cities, city_lookup, kind)
            if enriched != page:
                file.write_text(json.dumps(enriched, indent=2))
                updated["authority_pages"] += 1

        return {"updated_at": now_iso(), "updated": updated}
