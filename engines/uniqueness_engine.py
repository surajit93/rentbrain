from __future__ import annotations

import math
from collections import Counter


class UniquenessEngine:
    def _embed(self, text: str) -> Counter:
        tokens = [t.strip(".,$-!?():;'").lower() for t in text.split() if t.strip()]
        return Counter(t for t in tokens if len(t) > 2)

    def _cosine(self, a: Counter, b: Counter) -> float:
        keys = set(a) | set(b)
        dot = sum(a[k] * b[k] for k in keys)
        na = math.sqrt(sum(v * v for v in a.values()))
        nb = math.sqrt(sum(v * v for v in b.values()))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)

    def score(self, candidate: dict, existing_pages: list[dict]) -> float:
        candidate_text = f"{candidate['title']} {candidate['city']} {candidate['state']} {candidate['scenario']} {candidate['rent']} {candidate['salary']}"
        cvec = self._embed(candidate_text)

        max_similarity = 0.0
        for page in existing_pages:
            ptxt = f"{page.get('title','')} {page.get('city','')} {page.get('state','')} {page.get('scenario','')} {page.get('rent','')} {page.get('salary','')}"
            sim = self._cosine(cvec, self._embed(ptxt))
            max_similarity = max(max_similarity, sim)

        structural_diversity = 1.0 if candidate.get("template") not in {p.get("template") for p in existing_pages} else 0.7
        numeric_variance = 1.0 if not any(abs(candidate["rent"] - p.get("rent", 0)) < 50 for p in existing_pages) else 0.75
        entity_delta = 1.0 if not any(candidate["city"] == p.get("city") and candidate["scenario"] == p.get("scenario") for p in existing_pages) else 0.7
        uniqueness = (1 - max_similarity) * 0.5 + structural_diversity * 0.2 + numeric_variance * 0.15 + entity_delta * 0.15
        return round(max(0.0, min(1.0, uniqueness)), 3)
