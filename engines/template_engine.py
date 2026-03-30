from .common import load_json

class TemplateEngine:
    def run(self, clusters):
        variants=load_json("instructions/template_instructions.json").get("variants",[])
        for i,c in enumerate(clusters):
            c["template"]=variants[i % len(variants)] if variants else "decision_heavy"
        return clusters
