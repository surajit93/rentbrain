from __future__ import annotations

import json
from pathlib import Path

from .common import ROOT, load_json, now_iso


class AuthorityContentEngine:
    def run(self):
        cities = load_json("data/city_index.json").get("cities", [])
        outputs = []
        for city in cities:
            slug = f"rent-benchmark-{city['city'].lower()}"
            dataset = {
                "city": city["city"],
                "state": city["state"],
                "median_rent": city["median_rent"],
                "median_salary": city["median_salary"],
            }
            doc = {
                "slug": slug,
                "title": f"{city['city']} rent benchmark and affordability dataset",
                "sections": [
                    "Methodology",
                    "Income vs Rent Ratio",
                    "Scenario Analysis",
                    "Risk Benchmarks",
                ],
                "dataset": dataset,
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
            outputs.append(doc)
            Path(ROOT / "authority_pages" / f"{slug}.json").write_text(json.dumps(doc, indent=2))
        return outputs
