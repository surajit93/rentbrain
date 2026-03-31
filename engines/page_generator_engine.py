from __future__ import annotations

import json
from pathlib import Path

from .common import ROOT, load_json, save_json, now_iso
from .decision_engine import DecisionEngine
from .data_realism_engine import DataRealismEngine
from .uniqueness_engine import UniquenessEngine
from .seo_intent_engine import build_city_context, build_intent_links, insight_blocks, meta_for_page


class PageGeneratorEngine:
    SCENARIOS = [("alone", 0), ("roommates", 0), ("family", 350), ("alone", 450)]

    def _city_profile(self, state: str, city: str) -> dict:
        state_doc = load_json(f"data/states/{state}.json")
        for c in state_doc.get("cities", []):
            if c.get("name", "").lower() == city.lower():
                return c
        return {}

    def run(self, clusters: list[dict], max_pages: int = 100) -> list[dict]:
        cfg = load_json("config.json")
        threshold = cfg.get("constraints", {}).get("min_uniqueness", 0.75)
        decision = DecisionEngine()
        uniq = UniquenessEngine()
        realism = DataRealismEngine()
        pages = []
        all_slugs = []

        for c in clusters:
            if c.get("suppressed"):
                continue
            preferred = c.get("scenario")
            scenario_plan = [s for s in self.SCENARIOS if s[0] == preferred] + [s for s in self.SCENARIOS if s[0] != preferred]
            for scenario, debt_payment in scenario_plan:
                if len(pages) >= max_pages:
                    break
                salary = c["salary"]
                rent = c["rent"]
                slug = f"{c['city'].lower()}-{scenario}-rent-{int(rent)}-salary-{int(salary)}-{c['intent']}"
                title = f"{c['city']} {scenario} affordability for ${int(rent)} rent on ${int(salary)} salary"
                try:
                    from .title_engine import optimize_title

                    title = optimize_title(title)
                except Exception:
                    pass
                city_costs = self._city_profile(c["state"], c["city"])
                try:
                    from .intent_engine import classify

                    intent_class = classify(c.get("query", ""))
                except Exception:
                    intent_class = "general"
                try:
                    from .internal_linking_engine import generate_links

                    links = generate_links(slug, all_slugs)
                except Exception:
                    links = []
                city_index = load_json("data/city_index.json").get("cities", [])
                city_row = next((row for row in city_index if row.get("city") == c["city"] and row.get("state") == c["state"]), {"city": c["city"], "state": c["state"], "median_rent": rent, "median_salary": salary})
                context = build_city_context(city_row, city_index)
                page = {
                    "slug": slug,
                    "city": c["city"],
                    "state": c["state"],
                    "salary": salary,
                    "rent": rent,
                    "scenario": scenario,
                    "intent": c["intent"],
                    "template": c.get("template", "decision_heavy"),
                    "layout": c.get("layout", []),
                    "title": title,
                    "intent_class": intent_class,
                    "links": links,
                    "source_query": c.get("query"),
                    "calculator": decision.evaluate(salary, rent, scenario=scenario, debt_payment=debt_payment, city_costs=city_costs),
                    "cluster_id": c.get("cluster_id"),
                    "city_costs": city_costs,
                    "meta": meta_for_page(context, title, c.get("intent", "affordability")),
                    "heading_hierarchy": {
                        "h1": title,
                        "h2": ["Affordability summary", "Risk signal", "Trend and comparison insights", "Related housing pages"],
                    },
                    "insight_blocks": insight_blocks(context, c.get("intent", "affordability")),
                    "internal_links_v2": build_intent_links(city_row, city_index),
                    "created_at": now_iso(),
                }
                realism_check = realism.validate_candidate({"salary": salary, "rent": rent, "city_costs": city_costs})
                page["realism"] = realism_check
                if not realism_check["allowed"]:
                    continue
                uniq_eval = uniq.evaluate(page, pages)
                page["uniqueness_score"] = uniq_eval["score"]
                page["uniqueness"] = uniq_eval
                if uniq_eval["blocked"] or page["uniqueness_score"] < threshold or uniq_eval.get("intent_variance", 0) < 0.15:
                    continue
                try:
                    from .similarity_engine import is_duplicate

                    existing_contents = [p.get("title", "") for p in pages]
                    new_content = page.get("title", "")
                    if is_duplicate(new_content, existing_contents):
                        continue
                except Exception:
                    pass
                pages.append(page)
                all_slugs.append(slug)
                Path(ROOT / "pages" / f"{slug}.json").write_text(json.dumps(page, indent=2))

        save_json("indexes/page_index.json", {"pages": pages, "updated_at": now_iso()})
        uniq.save_memory(pages)
        return pages
