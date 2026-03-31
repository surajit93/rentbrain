from __future__ import annotations

import json
from pathlib import Path

from .common import ROOT, load_json, now_iso, save_json
from .seo_intent_engine import INTENT_PAGE_TYPES, build_city_context, build_intent_links, insight_blocks, meta_for_page


class AuthorityContentEngine:
    def _benchmark_doc(self, city: dict, context, all_cities: list[dict]) -> dict:
        slug = f"rent-benchmark-{context.city_slug}"
        links = build_intent_links(city, all_cities)
        title = f"{context.city} rent benchmark and affordability dataset"
        return {
            "slug": slug,
            "title": title,
            "sections": [
                "Methodology",
                "Income vs Rent Ratio",
                "Scenario Analysis",
                "Risk Benchmarks",
            ],
            "heading_hierarchy": {
                "h1": title,
                "h2": ["Methodology", "Income vs Rent Ratio", "Scenario Analysis", "Risk Benchmarks", "Related Local Housing Pages"],
            },
            "dataset": {
                "city": city["city"],
                "state": city["state"],
                "median_rent": city["median_rent"],
                "median_salary": city["median_salary"],
            },
            "meta": meta_for_page(context, title, "benchmark"),
            "cluster": "Rent",
            "insight_blocks": insight_blocks(context, "benchmark"),
            "internal_links": links,
            "structured_data": {
                "@context": "https://schema.org",
                "@type": "Dataset",
                "name": slug,
                "dateModified": now_iso(),
            },
            "citations": [
                "https://www.bls.gov/",
                "https://www.census.gov/",
            ],
            "word_count_target": 1800,
            "updated_at": now_iso(),
        }

    def _intent_doc(self, city: dict, context, all_cities: list[dict], page_kind: str) -> dict:
        page_def = INTENT_PAGE_TYPES[page_kind]
        slug = page_def["slug"].format(city_slug=context.city_slug)
        title = page_def["title"].format(city=context.city, state=context.state, year=2026)
        links = build_intent_links(city, all_cities)
        return {
            "slug": slug,
            "title": title,
            "city": context.city,
            "state": context.state,
            "cluster": page_def["cluster"],
            "intent_type": page_kind,
            "heading_hierarchy": {
                "h1": title,
                "h2": [
                    f"{context.city} rent snapshot",
                    f"{context.city} affordability context",
                    f"How {context.city} compares nationally",
                    "Related local housing pages",
                ],
            },
            "meta": meta_for_page(context, title, page_kind),
            "insight_blocks": insight_blocks(context, page_kind),
            "internal_links": {
                "intent_pages": [link for link in links["intent_pages"] if not link.endswith(slug)],
                "benchmark_page": links["benchmark_page"],
                "related_city_pages": links["related_city_pages"],
            },
            "structured_data": {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": title,
                "about": ["rent", "cost of living", "housing affordability"],
                "dateModified": now_iso(),
                "inLanguage": "en-US",
            },
            "city_metrics": {
                "median_rent": context.median_rent,
                "median_salary": context.median_salary,
                "annual_rent_to_income": round(context.ratio, 4),
                "national_median_rent": round(context.national_rent, 2),
                "national_median_salary": round(context.national_salary, 2),
                "national_rent_to_income": round(context.national_ratio, 4),
            },
            "updated_at": now_iso(),
        }

    def run(self):
        cities = load_json("data/city_index.json").get("cities", [])
        outputs = []
        clusters: dict[str, list[str]] = {"Rent": [], "Cost of Living": [], "Trends": [], "Affordability": []}

        for city in cities:
            context = build_city_context(city, cities)
            benchmark_doc = self._benchmark_doc(city, context, cities)
            outputs.append(benchmark_doc)
            clusters["Rent"].append(benchmark_doc["slug"])
            Path(ROOT / "authority_pages" / f"{benchmark_doc['slug']}.json").write_text(json.dumps(benchmark_doc, indent=2))

            for page_kind in INTENT_PAGE_TYPES:
                doc = self._intent_doc(city, context, cities, page_kind)
                outputs.append(doc)
                clusters[doc["cluster"]].append(doc["slug"])
                Path(ROOT / "authority_pages" / f"{doc['slug']}.json").write_text(json.dumps(doc, indent=2))

        hubs = {
            "updated_at": now_iso(),
            "clusters": [
                {
                    "name": cluster_name,
                    "hub_slug": f"hub-{cluster_name.lower().replace(' ', '-')}",
                    "spokes": slugs,
                }
                for cluster_name, slugs in clusters.items()
            ],
        }
        save_json("indexes/topical_cluster_index.json", hubs)
        return outputs
