class SerpIntelligenceEngine:
    def run(self, queries):
        for q in queries:
            q["fragmentation_score"]=round((1 if "reddit" in q.get("features",[]) else 0)+ (1 if "weak_blog" in q.get("features",[]) else 0) + 0.5*(1 if "forum" in q.get("features",[]) else 0),2)
        return queries
