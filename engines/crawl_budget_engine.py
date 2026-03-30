from .common import load_json, save_json

class CrawlBudgetEngine:
    def run(self):
        perf=load_json("indexes/performance_index.json").get("site",{})
        rate=perf.get("indexing_rate",0)
        daily=20 if rate>=0.7 else 8 if rate>=0.65 else 2
        status="scale" if rate>=0.7 else "hold" if rate>=0.65 else "throttle"
        out={"target_new_pages_per_day":daily,"status":status}
        save_json("indexes/crawl_budget_index.json", out)
        return out
