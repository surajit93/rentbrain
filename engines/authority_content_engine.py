from pathlib import Path
import json
from .common import ROOT

class AuthorityContentEngine:
    def run(self):
        out=[]
        for i in range(1,21):
            slug=f"rent-benchmark-{i:02d}"
            data={"slug":slug,"title":f"US Rent Benchmark Report #{i}","structured_data":{"@type":"Report","name":slug},"citations":["BLS","Census"],"analysis_depth":"high"}
            out.append(data)
            (ROOT/"authority_pages"/f"{slug}.json").write_text(json.dumps(data,indent=2))
        return out
