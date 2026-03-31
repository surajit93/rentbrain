from __future__ import annotations

from .analytics_real_engine import AnalyticsRealEngine
from .authority_growth_engine import AuthorityGrowthEngine
from .cluster_semantic_engine import ClusterSemanticEngine
from .common import load_json, now_iso, save_json
from .content_intelligence_engine import ContentIntelligenceEngine
from .content_uniqueness_engine import ContentUniquenessEngine
from .internal_linking_engine import InternalLinkingEngine
from .learning_loop_engine import LearningLoopEngine
from .serp_merged_engine import SerpMergedEngine
from .strategy_controller_engine import StrategyControllerEngine
from .strategy_engine import StrategyEngine


class EnhancedSystemEngine:
    def _load_mode(self) -> str:
        mode_doc = load_json("config/system_mode.json")
        mode = mode_doc.get("mode", "legacy") if isinstance(mode_doc, dict) else "legacy"
        return mode if mode in {"legacy", "enhanced"} else "legacy"

    def run(self, cycles: int = 2) -> dict:
        mode = self._load_mode()
        legacy_state = StrategyEngine().run(cycles=cycles)
        if mode != "enhanced":
            return {"updated_at": now_iso(), "mode": "legacy", "legacy": legacy_state}

        seed_queries = StrategyEngine()._seed_queries()
        serp_v2 = SerpMergedEngine().run(seed_queries)
        keywords = load_json("indexes/keyword_index.json").get("keywords", [])
        clusters = load_json("indexes/cluster_index.json").get("clusters", [])
        controller = StrategyControllerEngine().run(serp_v2, clusters)
        semantic_clusters = ClusterSemanticEngine().build_cluster_index_v2(keywords)
        gsc = AnalyticsRealEngine().run(site_url="sc-domain:example.com")
        learning_engine = LearningLoopEngine()
        learning = learning_engine.update_strategy_inputs()
        learning_history = learning_engine.store_performance_history()
        authority_engine = AuthorityGrowthEngine()
        authority = authority_engine.track_backlinks()
        authority_score = authority_engine.compute_domain_score()
        velocity = authority_engine.track_growth_velocity()
        pages = load_json("indexes/page_index.json").get("pages", [])
        perf = load_json("indexes/performance_index.json")
        link_graph = InternalLinkingEngine().build_link_graph(pages, perf)
        optimized_pages = InternalLinkingEngine().optimize_internal_links(pages, link_graph)
        intelligence_engine = ContentIntelligenceEngine()
        adaptations = []
        for kw in keywords[:100]:
            serp_row = next((s for s in serp_v2 if s.get("query") == kw.get("query")), {})
            adaptations.append(intelligence_engine.adapt_content_structure(kw, serp_row))
        uniqueness_engine = ContentUniquenessEngine()
        uniqueness = []
        for page in optimized_pages[:100]:
            uniqueness.append(
                {
                    "slug": page.get("slug"),
                    **uniqueness_engine.block_duplicate_generation(page, [p for p in optimized_pages if p.get("slug") != page.get("slug")], threshold=0.75),
                }
            )
        pipeline = {
            "stage_1_serp": len(serp_v2),
            "stage_2_keyword_scoring": len(controller.get("allocation", {}).get("selected", [])),
            "stage_3_content": len(adaptations),
            "stage_4_index": len(load_json("indexes/page_index.json").get("pages", [])),
            "stage_5_traffic": len(gsc.get("pages", [])),
            "stage_6_analytics": gsc.get("source_status"),
            "stage_7_learning": learning.get("scale_bias"),
            "stage_8_strategy": controller.get("allocation", {}).get("status"),
            "stage_9_next_generation": controller.get("expansion", {}).get("winner_clusters", 0),
        }
        out = {
            "updated_at": now_iso(),
            "mode": "enhanced",
            "legacy": legacy_state,
            "enhanced": {
                "serp_v2_count": len(serp_v2),
                "controller": controller,
                "semantic_clusters": semantic_clusters.get("clusters", [])[:20],
                "gsc_source": gsc.get("source_status"),
                "learning": learning,
                "learning_history_size": len(learning_history.get("history", [])),
                "authority": authority,
                "authority_score": authority_score,
                "velocity": velocity,
                "internal_link_graph": {"nodes": link_graph.get("nodes", 0), "edges": link_graph.get("edges", 0)},
                "content_adaptations": adaptations[:20],
                "uniqueness": uniqueness[:20],
                "pipeline": pipeline,
            },
        }
        save_json("indexes/system_run_v2.json", out)
        save_json("indexes/page_index_v2.json", {"updated_at": now_iso(), "pages": optimized_pages})
        return out
