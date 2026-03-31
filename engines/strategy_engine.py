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
from .data_realism_engine import DataRealismEngine
from .learning_engine import LearningEngine
from .content_differentiation_engine import ContentDifferentiationEngine


def is_dead(page):
    return page.get("impressions", 0) == 0


class StrategyEngine:
    def __init__(self):
        self.cfg = load_json("config.json")
        self.learning_engine = LearningEngine()

    def _seed_queries(self):
        cities = load_json("data/city_index.json").get("cities", [])
        queries = []
        for c in cities[:40]:
            queries.append({"query": f"can i afford {c['median_rent']} rent in {c['city']} on {c['median_salary']} salary", "city": c["city"], "state": c["state"]})
            queries.append({"query": f"{c['city']} rent calculator reddit", "city": c["city"], "state": c["state"]})
        return queries

    def _approve_action(self, action: str, context: dict) -> tuple[bool, str]:
        if context.get("signal_state") in {"unknown", "missing", "error"}:
            return False, "blocked_unknown_signal"
        if action in {"data_quality", "analytics_baseline", "crawl_budget"}:
            return True, "approved"
        if action == "serp_intelligence":
            return True, "approved"
        if action == "serp_eligibility":
            return context.get("serp_source_ok", False), "approved" if context.get("serp_source_ok", False) else "blocked_serp_source"
        if action == "keyword_generation":
            return context.get("serp_allowed", 0) > 0, "approved" if context.get("serp_allowed", 0) > 0 else "blocked_no_serp_allow"
        if action == "cluster_build":
            return context.get("keywords", 0) > 0, "approved" if context.get("keywords", 0) > 0 else "blocked_no_keywords"
        if action == "template_select":
            return context.get("clusters", 0) > 0, "approved" if context.get("clusters", 0) > 0 else "blocked_no_clusters"
        if action == "generate_pages":
            allow = (
                context.get("analytics_decision_allowed", False)
                and context.get("budget_status") in {"hold", "scale"}
                and context.get("cluster_ready", False)
            )
            return allow, "approved" if allow else "blocked_generation_constraints"
        if action == "expand_winners":
            allow = context.get("budget_status") == "scale" and context.get("winner_clusters", 0) > 0 and context.get("analytics_decision_allowed", False)
            return allow, "approved" if allow else "blocked_expansion_constraints"
        if action in {"prune", "optimize_ctr", "entity_index", "internal_linking", "distribution", "backlink", "authority_content", "embed", "content_differentiation"}:
            return context.get("generated_pages", 0) > 0, "approved" if context.get("generated_pages", 0) > 0 else "blocked_no_pages"
        return False, "blocked_unknown_action"

    def _execute_if_approved(self, cycle: dict, action: str, context: dict, fn):
        approved, reason = self._approve_action(action, context)
        cycle["approvals"][action] = {"approved": approved, "reason": reason}
        return fn() if approved else None

    def _winner_expansions(self, clusters: list[dict], learning: dict) -> tuple[list[dict], list[dict]]:
        winners = [c for c in clusters if c.get("eligible_for_expansion") and not c.get("suppressed")]
        winners.sort(key=lambda c: c.get("priority_score", 0), reverse=True)
        winners = winners[:10]

        expansions = []
        bias = learning.get("cluster_rank", {})
        for winner in winners:
            try:
                if is_dead(winner):
                    continue
            except Exception:
                pass
            rank_boost = 1 if bias.get(winner.get("cluster_id", ""), 0) >= 0.04 else 0
            expansion_steps = 3 + rank_boost
            for i in range(expansion_steps):
                exp = dict(winner)
                exp["salary"] = winner["salary"] + (i * 1500)
                exp["rent"] = winner["rent"] + (i * 50)
                exp["query"] = f"{winner['city']} {winner['intent']} {int(exp['rent'])} rent {int(exp['salary'])} salary"
                expansions.append(exp)
        return winners, expansions

    def run(self, cycles: int = 2):
        state = {"version": 4, "started_at": now_iso(), "cycles": []}
        learning = self.learning_engine.load()
        boot_cycle = {"iteration": 0, "time": now_iso(), "approvals": {}}
        data_quality = self._execute_if_approved(
            boot_cycle,
            "data_quality",
            {"signal_state": "ok"},
            lambda: DataQualityEngine().run(),
        ) or {"decision_allowed": False, "reason": "data_quality_not_executed"}
        if not data_quality.get("decision_allowed"):
            state["status"] = "blocked_data_quality"
            state["data_quality"] = data_quality
            state["last_run"] = now_iso()
            state["learning"] = learning
            state["cycles"].append(boot_cycle)
            save_json("indexes/strategy.json", state)
            return state

        pages = load_json("indexes/page_index.json").get("pages", [])
        perf_baseline = self._execute_if_approved(
            boot_cycle,
            "analytics_baseline",
            {"signal_state": "ok"},
            lambda: AnalyticsEngine().run(pages),
        ) or {"decision_allowed": False, "source": "analytics_not_executed", "site": {}}
        state["cycles"].append(boot_cycle)

        for iteration in range(cycles):
            cycle = {"iteration": iteration + 1, "time": now_iso(), "approvals": {}}

            serp_raw = self._execute_if_approved(cycle, "serp_intelligence", {"signal_state": "ok"}, lambda: SerpIntelligenceEngine().run(self._seed_queries())) or []

            serp_source_ok = any(r.get("source_status") == "ok" for r in serp_raw)
            serp_allowed = self._execute_if_approved(
                cycle,
                "serp_eligibility",
                {"signal_state": "ok" if serp_source_ok else "unknown", "serp_source_ok": serp_source_ok},
                lambda: SerpEligibilityEngine().run(serp_raw),
            ) or []

            keywords = self._execute_if_approved(
                cycle, "keyword_generation", {"signal_state": "ok" if serp_allowed else "unknown", "serp_allowed": len(serp_allowed)}, lambda: KeywordEngine().run(serp_allowed)
            ) or []
            try:
                from .gsc_engine import load_gsc
                from . import winner_engine

                gsc_data = load_gsc()
                winners = winner_engine.get_winners(gsc_data)
                for w in winners:
                    new_keywords = winner_engine.generate_support_keywords(w.get("query", ""))
                    for new_keyword in new_keywords:
                        if not new_keyword:
                            continue
                        keywords.append(
                            {
                                "query": new_keyword,
                                "city": w.get("city", ""),
                                "state": w.get("state", ""),
                                "salary": w.get("salary", 0),
                                "rent": w.get("rent", 0),
                                "intent": w.get("intent", "general"),
                                "scenario": w.get("scenario", "alone"),
                                "serp_difficulty": 1,
                                "forum_ratio": 0,
                                "source_query": w.get("query", ""),
                                "eligibility": "ALLOW",
                            }
                        )
            except Exception:
                pass
            classified = QueryClassifierEngine().run(keywords) if keywords else []

            clusters = self._execute_if_approved(
                cycle, "cluster_build", {"signal_state": "ok" if classified else "unknown", "keywords": len(classified)}, lambda: ClusterPriorityEngine().run(classified)
            ) or []

            templated = self._execute_if_approved(
                cycle, "template_select", {"signal_state": "ok" if clusters else "unknown", "clusters": len(clusters)}, lambda: TemplateEngine().run(clusters, learning=learning)
            ) or []

            budget = self._execute_if_approved(
                cycle,
                "crawl_budget",
                {"signal_state": "ok"},
                lambda: CrawlBudgetEngine().run(),
            ) or {"status": "throttle", "reason": "budget_not_executed"}
            max_pages = 0 if budget["status"] == "throttle" else 20 if budget["status"] == "hold" else 60
            generated = self._execute_if_approved(
                cycle,
                "generate_pages",
                {
                    "signal_state": "ok" if perf_baseline.get("decision_allowed") else "unknown",
                    "analytics_decision_allowed": perf_baseline.get("decision_allowed", False),
                    "budget_status": budget.get("status"),
                    "cluster_ready": bool(clusters),
                },
                lambda: PageGeneratorEngine().run(templated, max_pages=max_pages),
            ) or []

            realism = DataRealismEngine().run(generated)
            if not realism.get("decision_allowed"):
                generated = [p for p in generated if not any(b.get("slug") == p.get("slug") for b in realism.get("blocked", []))]

            optimized = self._execute_if_approved(
                cycle, "optimize_ctr", {"signal_state": "ok" if generated else "unknown", "generated_pages": len(generated)}, lambda: CtrOptimizationEngine().run(generated)
            )
            if optimized is not None:
                generated = optimized

            perf = AnalyticsEngine().run(generated)
            regressions = RegressionEngine().run(perf)

            winners, expansions = self._winner_expansions(clusters, learning)
            expanded = self._execute_if_approved(
                cycle,
                "expand_winners",
                {
                    "signal_state": "ok" if perf.get("decision_allowed") else "unknown",
                    "analytics_decision_allowed": perf.get("decision_allowed", False),
                    "budget_status": budget.get("status"),
                    "winner_clusters": len(winners),
                },
                lambda: PageGeneratorEngine().run(TemplateEngine().run(expansions, learning=learning), max_pages=min(30, len(expansions))),
            )
            if expanded:
                generated.extend(expanded)

            pruned = self._execute_if_approved(
                cycle, "prune", {"signal_state": "ok" if generated else "unknown", "generated_pages": len(generated)}, lambda: PruningEngine().run(generated, perf, self.cfg["constraints"]["prune_zero_impressions_days"])
            )
            pages, removed = pruned if pruned is not None else (generated, [])

            entities = self._execute_if_approved(cycle, "entity_index", {"signal_state": "ok" if pages else "unknown", "generated_pages": len(pages)}, lambda: EntityEngine().run(pages)) or []
            links = self._execute_if_approved(cycle, "internal_linking", {"signal_state": "ok" if pages else "unknown", "generated_pages": len(pages)}, lambda: InternalLinkingEngine().run(pages, perf)) or []
            authority = self._execute_if_approved(cycle, "authority_content", {"signal_state": "ok" if pages else "unknown", "generated_pages": len(pages)}, lambda: AuthorityContentEngine().run()) or []
            differentiation = self._execute_if_approved(cycle, "content_differentiation", {"signal_state": "ok" if pages else "unknown", "generated_pages": len(pages)}, lambda: ContentDifferentiationEngine().run()) or {}
            distribution = self._execute_if_approved(cycle, "distribution", {"signal_state": "ok" if pages else "unknown", "generated_pages": len(pages)}, lambda: DistributionEngine().run(pages, perf=perf)) or []
            embeds = self._execute_if_approved(cycle, "embed", {"signal_state": "ok" if pages else "unknown", "generated_pages": len(pages)}, lambda: EmbedEngine().run()) or []
            backlinks = self._execute_if_approved(cycle, "backlink", {"signal_state": "ok" if pages else "unknown", "generated_pages": len(pages)}, lambda: BacklinkEngine().run()) or {}

            dist_feedback = load_json("logs/distribution_plan.json").get("feedback", {})
            learning = self.learning_engine.update(
                learning,
                pages,
                perf,
                clusters,
                distribution_feedback=dist_feedback,
                controller_context={
                    "budget_status": budget.get("status"),
                    "serp_allowed": len(serp_allowed),
                    "generated": len(generated),
                    "winner_clusters": len(winners),
                },
            )
            self.learning_engine.save_snapshot(learning)

            cycle.update(
                {
                    "serp_candidates": len(serp_raw),
                    "serp_allowed": len(serp_allowed),
                    "keywords": len(keywords),
                    "clusters": len(clusters),
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
                    "differentiation_updates": differentiation.get("updated", {}),
                    "distribution_posts": len(distribution),
                    "embed_assets": len(embeds),
                    "backlink_strategy": backlinks,
                    "data_realism": realism,
                    "pre_cycle_decision_allowed": perf_baseline.get("decision_allowed", False),
                    "post_cycle_decision_allowed": perf.get("decision_allowed", False),
                }
            )
            state["cycles"].append(cycle)
            perf_baseline = perf

        last_budget = CrawlBudgetEngine().run()
        state["status"] = "active" if last_budget["status"] != "throttle" else "constrained"
        state["last_run"] = now_iso()
        state["scale_allowed"] = last_budget["status"] == "scale"
        state["data_quality"] = data_quality
        state["learning"] = learning
        state["controller"] = {"global_authority": True, "unknown_signal_policy": "block"}
        save_json("indexes/strategy.json", state)
        return state


if __name__ == "__main__":
    print(StrategyEngine().run())
