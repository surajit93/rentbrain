
from __future__ import annotations
from .common import load_json, save_json, now_iso
from .serp_eligibility_engine import SerpEligibilityEngine
from .serp_intelligence_engine import SerpIntelligenceEngine
from .keyword_engine import KeywordEngine
from .cluster_priority_engine import ClusterPriorityEngine
from .query_classifier_engine import QueryClassifierEngine
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

    def run(self):
        serp_candidates=[
            {"query":"can i afford 1800 rent in austin on 72k","features":["reddit","weak_blog"],"top_domains":["reddit.com","smallblog.example"]},
            {"query":"rent affordability austin","features":["authority"],"top_domains":["zillow.com","bankrate.com"],"strong_calculator":True}
        ]
        allowed = SerpEligibilityEngine().run(serp_candidates)
        intel = SerpIntelligenceEngine().run(allowed)
        keywords = KeywordEngine().run(intel)
        classified = QueryClassifierEngine().run(keywords)
        clusters = ClusterPriorityEngine().run(classified)
        templated = TemplateEngine().run(clusters)
        pages = PageGeneratorEngine().run(templated, max_pages=self.cfg["constraints"]["initial_pages_range"][0])
        pages = CtrOptimizationEngine().run(pages)
        perf = AnalyticsEngine().run(pages)
        regressions = RegressionEngine().run(perf)
        pages, removed = PruningEngine().run(pages)
        entities = EntityEngine().run(pages)
        links = InternalLinkingEngine().run(pages)
        crawl = CrawlBudgetEngine().run()
        authority = AuthorityContentEngine().run()
        embeds = EmbedEngine().run()
        backlinks = BacklinkEngine().run()
        distribution = DistributionEngine().run(pages)

        scale_allowed = perf["site"]["indexing_rate"] >= self.cfg["constraints"]["min_indexing_rate_to_scale"] and perf["site"]["ctr"] >= self.cfg["constraints"]["min_ctr_to_scale"] and perf["site"]["impressions_trend"] == "growing"
        strategy_state={"version":1,"status":"active","last_run":now_iso(),"scale_allowed":scale_allowed,"removed_pages":removed,"regressions":regressions,
                        "counts":{"allowed_serp":len(allowed),"keywords":len(keywords),"clusters":len(clusters),"pages":len(pages),"authority_pages":len(authority),"distribution_posts":len(distribution),"entities":len(entities),"links":len(links)},
                        "crawl_budget":crawl,"embeds":embeds,"backlink_strategy":backlinks}
        save_json("indexes/strategy.json", strategy_state)
        return strategy_state

if __name__ == "__main__":
    print(StrategyEngine().run())
