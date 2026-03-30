from .common import save_json

class EntityEngine:
    def run(self, pages):
        entities=[]
        for p in pages:
            entities.append({"slug":p["slug"],"entities":[p["city"],p["state"],str(p["salary"]),str(p["rent"]),p["scenario"]]})
        save_json("indexes/entity_index.json", {"entities":entities})
        return entities
