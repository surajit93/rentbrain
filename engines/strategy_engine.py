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
from .data_quality_engine import DataQualityEngine


class StrategyEngine:
    def __init__(self):
        self.cfg = load_json("config.json")

    def _seed_queries(self):
        cities = load_json("data/city_index.json").get("cities", [])
        queries = []
        for c in cities[:40]:
            queries.append({"query": f"can i afford {c['median_rent']} rent in {c['city']} on {c['median_salary']} salary", "city": c["city"], "state": c["state"]})
            queries.append({"query": f"{c['city']} rent calculator reddit", "city": c["city"], "state": c["state"]})
        return queries

    def _expand_winners(self, clusters: list[dict], perf: dict):
        if not perf.get("decision_allowed"):
            return [], []
        by_slug = {p["slug"]: p for p in perf.get("pages", [])}
        winners = []
        for c in clusters:
            cid = c["cluster_id"]
            cluster_pages = [s for s in by_slug if cid.split("-")[0] in s]
            if not cluster_pages:
                continue
            avg_ctr = sum(by_slug[s].get("ctr", 0) for s in cluster_pages) / max(len(cluster_pages), 1)
            avg_impr = sum(by_slug[s].get("impressions", 0) for s in cluster_pages) / max(len(cluster_pages), 1)
            indexed_ratio = sum(1 for s in cluster_pages if by_slug[s].get("indexed")) / max(len(cluster_pages), 1)
            if avg_ctr >= 0.04 and avg_impr >= 20 and indexed_ratio >= 0.6:
                winners.append(c)
        expansions = []
        for winner in winners:
            for i in range(6):
                exp = dict(winner)
                exp["salary"] = winner["salary"] + (i * 1200)
                exp["rent"] = winner["rent"] + (i * 35)
                expansions.append(exp)
        return winners, expansions

    def _enforce(self, action: str, context: dict) -> tuple[bool, str]:
        if action == "generate_pages" and not context.get("analytics_decision_allowed", False):
            return False, "blocked_no_analytics_data"
        if action == "expand_winners" and not context.get("analytics_decision_allowed", False):
            return False, "blocked_no_analytics_data"
        if action == "expand_winners" and context.get("budget_status") != "scale":
            return False, "blocked_budget_not_scale"
        if action == "serp_allow" and context.get("source_status") != "ok":
            return False, "blocked_serp_unknown"
        return True, "approved"

    def run(self, cycles: int = 2):
        state = {"version": 3, "started_at": now_iso(), "cycles": []}

        data_quality = DataQualityEngine().run()
        if not data_quality.get("valid"):
            state["status"] = "blocked_data_quality"
            state["data_quality"] = data_quality
            state["last_run"] = now_iso()
            save_json("indexes/strategy.json", state)
            return state

        pages = load_json("indexes/page_index.json").get("pages", [])
        perf_baseline = AnalyticsEngine().run(pages)
        control = {
            "block_fake_signals": True,
            "block_scale_without_analytics": True,
            "min_uniqueness": self.cfg.get("constraints", {}).get("min_uniqueness", 0.75),
        }

        for iteration in range(cycles):
            serp_raw = SerpIntelligenceEngine().run(self._seed_queries())
            serp_allowed = SerpEligibilityEngine().run(serp_raw)
            if not serp_allowed:
                state["cycles"].append(
                    {
                        "iteration": iteration + 1,
                        "time": now_iso(),
                        "blocked": True,
                        "reason": "no_eligible_serp_entries",
                        "serp_candidates": len(serp_raw),
                        "serp_allowed": 0,
                    }
                )
                continue

            keywords = KeywordEngine().run(serp_allowed)
            classified = QueryClassifierEngine().run(keywords)
            clusters = ClusterPriorityEngine().run(classified)
            templated = TemplateEngine().run(clusters)

            perf_before = perf_baseline
            budget = CrawlBudgetEngine().run()
            approved_generation, generation_reason = self._enforce(
                "generate_pages",
                {"analytics_decision_allowed": perf_before.get("decision_allowed", False)},
            )
            if budget["status"] == "throttle":
                max_pages = 0
            elif budget["status"] == "hold":
                max_pages = 20
            else:
                max_pages = 60

            if approved_generation and max_pages > 0:
                generated = PageGeneratorEngine().run(templated, max_pages=max_pages)
                generated = CtrOptimizationEngine().run(generated)
            else:
                generated = []
            perf = AnalyticsEngine().run(generated)
            regressions = RegressionEngine().run(perf)
            pages, removed = PruningEngine().run(generated, perf, self.cfg["constraints"]["prune_zero_impressions_days"])

            winners, expansions = self._expand_winners(clusters, perf)
            approved_expansion, expansion_reason = self._enforce(
                "expand_winners",
                {
                    "analytics_decision_allowed": perf.get("decision_allowed", False),
                    "budget_status": budget["status"],
                },
            )
            if approved_expansion and expansions:
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
                    "control": control,
                    "entities": len(entities),
                    "links": len(links),
                    "authority_pages": len(authority),
                    "distribution_posts": len(distribution),
                    "embed_assets": len(embeds),
                    "backlink_strategy": backlinks,
                    "pre_cycle_decision_allowed": perf_before.get("decision_allowed", False),
                    "post_cycle_decision_allowed": perf.get("decision_allowed", False),
                    "approvals": {
                        "generate_pages": {"approved": approved_generation, "reason": generation_reason},
                        "expand_winners": {"approved": approved_expansion, "reason": expansion_reason},
                    },
                }
            )
            perf_baseline = perf

        last_budget = CrawlBudgetEngine().run()
        state["status"] = "active" if last_budget["status"] != "throttle" else "constrained"
        state["last_run"] = now_iso()
        state["scale_allowed"] = last_budget["status"] == "scale"
        state["data_quality"] = data_quality
        save_json("indexes/strategy.json", state)
        return state


if __name__ == "__main__":
    print(StrategyEngine().run())
