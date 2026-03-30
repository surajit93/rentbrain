from .common import load_json, save_json

class SerpEligibilityEngine:
    def run(self, candidates):
        cfg=load_json("config.json")
        allow_terms={"reddit","quora","forum","weak_blog"}
        block_domains=set(cfg["serp_rules"]["high_authority_domains"])
        out=[]
        for c in candidates:
            features=set(c.get("features",[]))
            domains=set(c.get("top_domains",[]))
            allow=bool(features & allow_terms) and len(domains & block_domains) < 2 and not c.get("google_native",False) and not c.get("strong_calculator",False)
            c["allow"]=allow
            out.append(c)
        save_json("indexes/serp_index.json", {"queries":out})
        return [x for x in out if x["allow"]]
