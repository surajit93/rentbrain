from __future__ import annotations

from .analytics_real_engine import AnalyticsRealEngine
from .authority_growth_engine import AuthorityGrowthEngine
from .cluster_semantic_engine import ClusterSemanticEngine
from .common import load_json, now_iso, save_json
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
        learning = LearningLoopEngine().adjust_strategy_signals()
        LearningLoopEngine().store_historical_performance()
        authority = AuthorityGrowthEngine().track_backlinks()
        authority_score = AuthorityGrowthEngine().compute_authority_score()
        velocity = AuthorityGrowthEngine().track_link_velocity()
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
                "authority": authority,
                "authority_score": authority_score,
                "velocity": velocity,
            },
        }
        save_json("indexes/system_run_v2.json", out)
        return out
