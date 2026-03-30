from pathlib import Path
import json
from .common import ROOT, save_json
from .decision_engine import DecisionEngine
from .uniqueness_engine import UniquenessEngine

class PageGeneratorEngine:
    def run(self, clusters, max_pages=400):
        dec=DecisionEngine()
        uq=UniquenessEngine()
        pages=[]
        for c in clusters[:max_pages]:
            city=c["city"]; state="NA"
            salary=72000 if city=="Austin" else 68000
            rent=1800 if city=="Austin" else 1650
            scenario=c["intent"]
            slug=f"can-i-afford-{rent}-rent-in-{city.lower()}-{salary}-salary-{scenario}"
            res=dec.decision(salary,rent)
            score=uq.score(city,salary,rent,scenario,c.get("template"))
            if score < 0.75:
                continue
            page={"slug":slug,"city":city,"state":state,"salary":salary,"rent":rent,"scenario":scenario,"title":"","calculator":res,"uniqueness_score":score,"ctr":0.05,"impressions":5}
            pages.append(page)
            (ROOT/"pages"/f"{slug}.json").write_text(json.dumps(page,indent=2))
        save_json("indexes/page_index.json", {"pages":pages})
        return pages
