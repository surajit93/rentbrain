from __future__ import annotations

from .common import load_json, save_json, now_iso
from .serp_intelligence_engine import SerpIntelligenceEngine
from .serp_eligibility_engine import SerpEligibilityEngine
from .keyword_engine import KeywordEngine
from .query_classifier_engine import QueryClassifierEngine
from .cluster_priority_engine import ClusterPriorityEngine
from .template_engine import TemplateEngine
from .page_generator_engine import PageGeneratorEngine
from .analytics_engine import AnalyticsEngine
from .regression_engine import RegressionEngine
from .pruning_engine import PruningEngine
from .ctr_optimization_engine import CtrOptimizationEngine
from .authority_content_engine import AuthorityContentEngine
from .distribution_engine import DistributionEngine
from .entity_engine import EntityEngine
from .internal_linking_engine import InternalLinkingEngine
from .crawl_budget_engine import CrawlBudgetEngine
from .embed_engine import EmbedEngine
from .backlink_engine import BacklinkEngine


class StrategyEngine:
    def __init__(self):
        self.cfg = load_json("config.json")

    def _seed_queries(self):
        cities = load_json("data/city_index.json").get("cities", [])
        queries = []
        for c in cities:
            queries.append({"query": f"can i afford {c['median_rent']} rent in {c['city']} on {c['median_salary']} salary"})
            queries.append({"query": f"{c['city']} rent calculator reddit"})
        return queries

    def _expand_winners(self, clusters: list[dict], perf: dict):
        by_slug = {p["slug"]: p for p in perf.get("pages", [])}
        winners = []
        for c in clusters:
            cid = c["cluster_id"]
            cluster_pages = [s for s in by_slug if cid.split("-")[0] in s]
            if not cluster_pages:
                continue
            avg_ctr = sum(by_slug[s].get("ctr", 0) for s in cluster_pages) / max(len(cluster_pages), 1)
            if avg_ctr >= 0.04:
                winners.append(c)
        expansions = []
        for winner in winners:
            for i in range(10):
                exp = dict(winner)
                exp["salary"] = winner["salary"] + (i * 1000)
                exp["rent"] = winner["rent"] + (i * 25)
                expansions.append(exp)
        return winners, expansions

    def run(self, cycles: int = 2):
        state = {"version": 2, "started_at": now_iso(), "cycles": []}
        pages = load_json("indexes/page_index.json").get("pages", [])

        for iteration in range(cycles):
            serp_raw = SerpIntelligenceEngine().run(self._seed_queries())
            serp_allowed = SerpEligibilityEngine().run(serp_raw)
            keywords = KeywordEngine().run(serp_allowed)
            classified = QueryClassifierEngine().run(keywords)
            clusters = ClusterPriorityEngine().run(classified)
            templated = TemplateEngine().run(clusters)

            budget = CrawlBudgetEngine().run()
            if budget["status"] == "throttle":
                max_pages = 5
            elif budget["status"] == "hold":
                max_pages = 20
            else:
                max_pages = 60

            generated = PageGeneratorEngine().run(templated, max_pages=max_pages)
            generated = CtrOptimizationEngine().run(generated)
            perf = AnalyticsEngine().run(generated)
            regressions = RegressionEngine().run(perf)
            pages, removed = PruningEngine().run(generated, perf, self.cfg["constraints"]["prune_zero_impressions_days"])

            winners, expansions = self._expand_winners(clusters, perf)
            if budget["status"] == "scale" and expansions:
                expanded_pages = PageGeneratorEngine().run(TemplateEngine().run(expansions), max_pages=min(30, len(expansions)))
                pages.extend(expanded_pages)

            entities = EntityEngine().run(pages)
            links = InternalLinkingEngine().run(pages, perf)
            authority = AuthorityContentEngine().run()
            distribution = DistributionEngine().run(pages)
            embeds = EmbedEngine().run()
            backlinks = BacklinkEngine().run()

            state["cycles"].append(
                {
                    "iteration": iteration + 1,
                    "time": now_iso(),
                    "serp_candidates": len(serp_raw),
                    "serp_allowed": len(serp_allowed),
                    "keywords": len(keywords),
                    "pages_generated": len(generated),
                    "pages_kept": len(pages),
                    "removed": removed,
                    "winners": [w["cluster_id"] for w in winners],
                    "expansion_count": len(expansions),
                    "regressions": regressions,
                    "budget": budget,
                    "entities": len(entities),
                    "links": len(links),
                    "authority_pages": len(authority),
                    "distribution_posts": len(distribution),
                    "embed_assets": len(embeds),
                    "backlink_strategy": backlinks,
                }
            )

        last_budget = CrawlBudgetEngine().run()
        state["status"] = "active" if last_budget["status"] != "throttle" else "constrained"
        state["last_run"] = now_iso()
        state["scale_allowed"] = last_budget["status"] == "scale"
        save_json("indexes/strategy.json", state)
        return state


if __name__ == "__main__":
    print(StrategyEngine().run())
