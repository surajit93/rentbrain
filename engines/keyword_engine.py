from .common import load_json, save_json

class KeywordEngine:
    def run(self, serp_queries):
        cities=load_json("data/city_index.json").get("cities",[])
        intents=["affordability","survivability","salary_sufficiency"]
        kws=[]
        for c in cities:
            for intent in intents:
                rent=c["median_rent"]
                salary=c["median_salary"]
                q=f"can i afford ${rent} rent in {c['city']} on ${salary} salary after tax"
                kws.append({"query":q,"city":c["city"],"state":c["state"],"salary":salary,"rent":rent,"intent":intent,"fragmentation_score":0.8})
        save_json("indexes/keyword_index.json", {"keywords":kws})
        return kws
