from .common import save_json

class ClusterPriorityEngine:
    def run(self, keywords):
        clusters=[]
        for k in keywords:
            priority=0.5 + 0.2*(k.get("intent") in {"affordability","survivability","salary_sufficiency"}) + 0.3*min(k.get("fragmentation_score",0),1)
            clusters.append({"cluster_id":f"{k['city'].lower()}-{k['intent']}","city":k["city"],"intent":k["intent"],"priority_score":round(priority,3),"query":k["query"]})
        clusters=sorted(clusters,key=lambda x:x["priority_score"],reverse=True)
        save_json("indexes/cluster_index.json", {"clusters":clusters})
        return clusters
