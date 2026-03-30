class UniquenessEngine:
    def score(self, city, salary, rent, scenario, template):
        base=0.55
        numeric=0.15 if salary and rent else 0
        structure=0.10 if template else 0
        entity=0.10 if city else 0
        intent=0.15 if scenario else 0
        return min(1.0, round(base+numeric+structure+entity+intent,2))
