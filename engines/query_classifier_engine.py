class QueryClassifierEngine:
    def run(self, keywords):
        for k in keywords:
            q=k["query"]
            if "survive" in q:
                k["intent"]="survivability"
            elif "salary" in q:
                k["intent"]="salary_sufficiency"
            else:
                k["intent"]=k.get("intent","affordability")
        return keywords
