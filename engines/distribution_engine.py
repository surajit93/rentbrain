from .common import save_json

class DistributionEngine:
    def run(self, pages):
        posts=[]
        for p in pages[:30]:
            posts.append({"channel":"reddit","title":f"Help: {p['title']}","link":f"/pages/{p['slug']}.json"})
            posts.append({"channel":"quora","title":p['title'],"link":f"/pages/{p['slug']}.json"})
        save_json("logs/distribution_plan.json", {"posts":posts})
        return posts
