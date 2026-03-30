from .common import save_json

class InternalLinkingEngine:
    def run(self, pages):
        links=[]
        by_city={}
        for p in pages:
            by_city.setdefault(p["city"],[]).append(p)
        for city, plist in by_city.items():
            for i,p in enumerate(plist):
                for t in plist[max(0,i-2):i]:
                    links.append({"from":p["slug"],"to":t["slug"],"reason":"city_cluster"})
        save_json("indexes/internal_link_index.json", {"links":links})
        return links
