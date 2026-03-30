class RegressionEngine:
    def run(self, perf):
        site = perf.get("site", {})
        regressions = []
        if not perf.get("decision_allowed", False):
            regressions.append("analytics_missing")
        if site.get("indexing_rate", 0) < 0.65:
            regressions.append("indexing_critical")
        if site.get("ctr", 0) < 0.045:
            regressions.append("ctr_critical")
        if site.get("impressions_trend") not in {"growing", "improving"}:
            regressions.append("impressions_stagnant")
        return regressions
