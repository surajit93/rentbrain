from __future__ import annotations

from .common import load_json, save_json, now_iso
from . import serp_fetcher


class KeywordEngine:
    def run(self, allowed_serps: list[dict]) -> list[dict]:
        cities = {c["city"]: c for c in load_json("data/city_index.json").get("cities", [])}
        intents = ["affordability", "survivability", "salary_sufficiency", "risk"]
        scenario_map = {"affordability": "alone", "survivability": "roommates", "salary_sufficiency": "family", "risk": "alone"}
        out = []
        for serp in allowed_serps:
            matched_city = next((city for city in cities if city.lower() in serp["query"].lower()), None)
            if not matched_city:
                continue
            try:
                domains = serp_fetcher.get_domains(serp["query"], serp_record=serp)
                if not serp_fetcher.is_weak_serp(domains):
                    continue
            except Exception:
                pass
            c = cities[matched_city]
            for intent in intents:
                keyword = f"{intent} check for ${c['median_rent']} rent in {c['city']} at ${c['median_salary']} income"
                variants = [
                    keyword,
                    f"{keyword} guide",
                    f"{keyword} tips",
                    f"{keyword} examples",
                    f"{keyword} breakdown",
                ]
                for v in variants:
                    out.append(
                        {
                            "query": v,
                            "city": c["city"],
                            "state": c["state"],
                            "salary": c["median_salary"],
                            "rent": c["median_rent"],
                            "intent": intent,
                            "scenario": scenario_map.get(intent, "alone"),
                            "serp_difficulty": serp.get("serp_difficulty", 1),
                            "forum_ratio": serp.get("forum_ratio", 0),
                            "source_query": serp["query"],
                            "eligibility": serp.get("eligibility", "BLOCK"),
                        }
                    )
        save_json("indexes/keyword_index.json", {"keywords": out, "updated_at": now_iso()})
        return out
