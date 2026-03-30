class QueryClassifierEngine:
    def run(self, keywords):
        for k in keywords:
            q = k["query"].lower()
            if "surviv" in q:
                k["intent"] = "survivability"
            elif "risk" in q or "too high" in q:
                k["intent"] = "risk"
            elif "salary" in q:
                k["intent"] = "salary_sufficiency"
            else:
                k["intent"] = k.get("intent", "affordability")
        return keywords
