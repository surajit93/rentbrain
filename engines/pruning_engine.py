class PruningEngine:
    def run(self, pages):
        kept=[p for p in pages if p.get("impressions",1)>0 and p.get("ctr",0.05)>=0.03]
        removed=len(pages)-len(kept)
        return kept, removed
