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

    def _load_learning(self) -> dict:
        prior = load_json("indexes/strategy.json")
        memory = prior.get("learning", {}) if isinstance(prior, dict) else {}
        memory.setdefault("template_rank", {})
        memory.setdefault("cluster_rank", {})
        memory.setdefault("high_ctr_structures", {})
        memory.setdefault("history", [])
        return memory

    def _update_learning(self, learning: dict, pages: list[dict], perf: dict) -> dict:
        by_slug = {p.get("slug"): p for p in perf.get("pages", [])}
        for page in pages:
            slug = page.get("slug")
            m = by_slug.get(slug, {})
            ctr = float(m.get("ctr", 0))
            impr = int(m.get("impressions", 0))
            if impr < 5:
                continue

            template = page.get("template", "unknown")
            learning["template_rank"][template] = round(learning["template_rank"].get(template, 0.0) * 0.8 + ctr * 0.2, 4)

            cluster = page.get("cluster_id") or f"{page.get('city')}|{page.get('intent')}"
            learning["cluster_rank"][cluster] = round(learning["cluster_rank"].get(cluster, 0.0) * 0.75 + ctr * 0.25, 4)

            layout_key = "|".join(page.get("layout", [])) or "none"
            learning["high_ctr_structures"][layout_key] = round(learning["high_ctr_structures"].get(layout_key, 0.0) * 0.7 + ctr * 0.3, 4)

        learning["history"].append({"at": now_iso(), "site_ctr": perf.get("site", {}).get("ctr", 0), "indexing_rate": perf.get("site", {}).get("indexing_rate", 0)})
        learning["history"] = learning["history"][-50:]
        return learning

    def _approve_action(self, action: str, context: dict) -> tuple[bool, str]:
        if context.get("signal_state") in {"unknown", "missing", "error"}:
            return False, "blocked_unknown_signal"
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
            allow = context.get("analytics_decision_allowed", False) and context.get("budget_status") in {"hold", "scale"}
            return allow, "approved" if allow else "blocked_generation_constraints"
        if action == "expand_winners":
            allow = context.get("budget_status") == "scale" and context.get("winner_clusters", 0) > 0 and context.get("analytics_decision_allowed", False)
            return allow, "approved" if allow else "blocked_expansion_constraints"
        if action in {"prune", "optimize_ctr", "entity_index", "internal_linking", "distribution", "backlink", "authority_content", "embed"}:
            return context.get("generated_pages", 0) > 0, "approved" if context.get("generated_pages", 0) > 0 else "blocked_no_pages"
        return False, "blocked_unknown_action"

    def _winner_expansions(self, clusters: list[dict], learning: dict) -> tuple[list[dict], list[dict]]:
        winners = [c for c in clusters if c.get("eligible_for_expansion") and not c.get("suppressed")]
        winners.sort(key=lambda c: c.get("priority_score", 0), reverse=True)
        winners = winners[:10]

        expansions = []
        bias = learning.get("cluster_rank", {})
        for winner in winners:
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
        learning = self._load_learning()

        data_quality = DataQualityEngine().run()
        if not data_quality.get("decision_allowed"):
            state["status"] = "blocked_data_quality"
            state["data_quality"] = data_quality
            state["last_run"] = now_iso()
            state["learning"] = learning
            save_json("indexes/strategy.json", state)
            return state

        pages = load_json("indexes/page_index.json").get("pages", [])
        perf_baseline = AnalyticsEngine().run(pages)

        for iteration in range(cycles):
            cycle = {"iteration": iteration + 1, "time": now_iso(), "approvals": {}}

            approve_serp, reason_serp = self._approve_action("serp_intelligence", {"signal_state": "ok"})
            cycle["approvals"]["serp_intelligence"] = {"approved": approve_serp, "reason": reason_serp}
            serp_raw = SerpIntelligenceEngine().run(self._seed_queries()) if approve_serp else []

            serp_source_ok = any(r.get("source_status") == "ok" for r in serp_raw)
            approve_eligibility, reason_eligibility = self._approve_action("serp_eligibility", {"signal_state": "ok" if serp_source_ok else "unknown", "serp_source_ok": serp_source_ok})
            cycle["approvals"]["serp_eligibility"] = {"approved": approve_eligibility, "reason": reason_eligibility}
            serp_allowed = SerpEligibilityEngine().run(serp_raw) if approve_eligibility else []

            approve_kw, reason_kw = self._approve_action("keyword_generation", {"signal_state": "ok" if serp_allowed else "unknown", "serp_allowed": len(serp_allowed)})
            cycle["approvals"]["keyword_generation"] = {"approved": approve_kw, "reason": reason_kw}
            keywords = KeywordEngine().run(serp_allowed) if approve_kw else []
            classified = QueryClassifierEngine().run(keywords) if keywords else []

            approve_clusters, reason_clusters = self._approve_action("cluster_build", {"signal_state": "ok" if classified else "unknown", "keywords": len(classified)})
            cycle["approvals"]["cluster_build"] = {"approved": approve_clusters, "reason": reason_clusters}
            clusters = ClusterPriorityEngine().run(classified) if approve_clusters else []

            approve_templates, reason_templates = self._approve_action("template_select", {"signal_state": "ok" if clusters else "unknown", "clusters": len(clusters)})
            cycle["approvals"]["template_select"] = {"approved": approve_templates, "reason": reason_templates}
            templated = TemplateEngine().run(clusters, learning=learning) if approve_templates else []

            budget = CrawlBudgetEngine().run()
            generate_ok, generate_reason = self._approve_action(
                "generate_pages",
                {
                    "signal_state": "ok" if perf_baseline.get("decision_allowed") else "unknown",
                    "analytics_decision_allowed": perf_baseline.get("decision_allowed", False),
                    "budget_status": budget.get("status"),
                },
            )
            cycle["approvals"]["generate_pages"] = {"approved": generate_ok, "reason": generate_reason}

            max_pages = 0 if budget["status"] == "throttle" else 20 if budget["status"] == "hold" else 60
            generated = PageGeneratorEngine().run(templated, max_pages=max_pages) if generate_ok else []

            optimize_ok, optimize_reason = self._approve_action("optimize_ctr", {"signal_state": "ok" if generated else "unknown", "generated_pages": len(generated)})
            cycle["approvals"]["optimize_ctr"] = {"approved": optimize_ok, "reason": optimize_reason}
            if optimize_ok:
                generated = CtrOptimizationEngine().run(generated)

            perf = AnalyticsEngine().run(generated)
            regressions = RegressionEngine().run(perf)

            winners, expansions = self._winner_expansions(clusters, learning)
            expand_ok, expand_reason = self._approve_action(
                "expand_winners",
                {
                    "signal_state": "ok" if perf.get("decision_allowed") else "unknown",
                    "analytics_decision_allowed": perf.get("decision_allowed", False),
                    "budget_status": budget.get("status"),
                    "winner_clusters": len(winners),
                },
            )
            cycle["approvals"]["expand_winners"] = {"approved": expand_ok, "reason": expand_reason}
            if expand_ok and expansions:
                generated.extend(PageGeneratorEngine().run(TemplateEngine().run(expansions, learning=learning), max_pages=min(30, len(expansions))))

            prune_ok, prune_reason = self._approve_action("prune", {"signal_state": "ok" if generated else "unknown", "generated_pages": len(generated)})
            cycle["approvals"]["prune"] = {"approved": prune_ok, "reason": prune_reason}
            pages, removed = PruningEngine().run(generated, perf, self.cfg["constraints"]["prune_zero_impressions_days"]) if prune_ok else (generated, [])

            entities = EntityEngine().run(pages) if self._approve_action("entity_index", {"signal_state": "ok" if pages else "unknown", "generated_pages": len(pages)})[0] else []
            links = InternalLinkingEngine().run(pages, perf) if self._approve_action("internal_linking", {"signal_state": "ok" if pages else "unknown", "generated_pages": len(pages)})[0] else []
            authority = AuthorityContentEngine().run() if self._approve_action("authority_content", {"signal_state": "ok" if pages else "unknown", "generated_pages": len(pages)})[0] else []
            distribution = DistributionEngine().run(pages, perf=perf) if self._approve_action("distribution", {"signal_state": "ok" if pages else "unknown", "generated_pages": len(pages)})[0] else []
            embeds = EmbedEngine().run() if self._approve_action("embed", {"signal_state": "ok" if pages else "unknown", "generated_pages": len(pages)})[0] else []
            backlinks = BacklinkEngine().run() if self._approve_action("backlink", {"signal_state": "ok" if pages else "unknown", "generated_pages": len(pages)})[0] else {}

            learning = self._update_learning(learning, pages, perf)

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
                    "distribution_posts": len(distribution),
                    "embed_assets": len(embeds),
                    "backlink_strategy": backlinks,
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
