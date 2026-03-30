from __future__ import annotations

import json
from pathlib import Path

from .common import ROOT, load_json, save_json, now_iso
from .decision_engine import DecisionEngine
from .uniqueness_engine import UniquenessEngine


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
        pages = []

        for c in clusters:
            if c.get("suppressed"):
                continue
            for scenario, debt_payment in self.SCENARIOS:
                if len(pages) >= max_pages:
                    break
                salary = c["salary"]
                rent = c["rent"]
                slug = f"{c['city'].lower()}-{scenario}-rent-{int(rent)}-salary-{int(salary)}-{c['intent']}"
                title = f"{c['city']} {scenario} affordability for ${int(rent)} rent on ${int(salary)} salary"
                city_costs = self._city_profile(c["state"], c["city"])
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
                    "source_query": c.get("query"),
                    "calculator": decision.evaluate(salary, rent, scenario=scenario, debt_payment=debt_payment, city_costs=city_costs),
                    "cluster_id": c.get("cluster_id"),
                    "created_at": now_iso(),
                }
                uniq_eval = uniq.evaluate(page, pages)
                page["uniqueness_score"] = uniq_eval["score"]
                page["uniqueness"] = uniq_eval
                if uniq_eval["blocked"] or page["uniqueness_score"] < threshold:
                    continue
                pages.append(page)
                Path(ROOT / "pages" / f"{slug}.json").write_text(json.dumps(page, indent=2))

        save_json("indexes/page_index.json", {"pages": pages, "updated_at": now_iso()})
        return pages
