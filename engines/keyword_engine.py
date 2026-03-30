from __future__ import annotations

from .common import load_json, save_json, now_iso


class KeywordEngine:
    def run(self, allowed_serps: list[dict]) -> list[dict]:
        cities = {c["city"]: c for c in load_json("data/city_index.json").get("cities", [])}
        intents = ["affordability", "survivability", "salary_sufficiency", "risk"]
        out = []
        for serp in allowed_serps:
            matched_city = next((city for city in cities if city.lower() in serp["query"].lower()), None)
            if not matched_city:
                continue
            c = cities[matched_city]
            for intent in intents:
                out.append(
                    {
                        "query": f"{intent} check for ${c['median_rent']} rent in {c['city']} at ${c['median_salary']} income",
                        "city": c["city"],
                        "state": c["state"],
                        "salary": c["median_salary"],
                        "rent": c["median_rent"],
                        "intent": intent,
                        "serp_difficulty": serp.get("serp_difficulty", 1),
                        "forum_ratio": serp.get("forum_ratio", 0),
                        "source_query": serp["query"],
                    }
                )
        save_json("indexes/keyword_index.json", {"keywords": out, "updated_at": now_iso()})
        return out
