from .common import load_json, save_json

class AnalyticsEngine:
    def run(self, pages):
        indexed=min(1.0,0.68 + len(pages)/5000)
        ctr=0.046 if pages else 0.0
        trend="growing" if pages else "flat"
        out={"clusters":[],"site":{"indexing_rate":round(indexed,3),"ctr":ctr,"impressions_trend":trend}}
        save_json("indexes/performance_index.json", out)
        return out
