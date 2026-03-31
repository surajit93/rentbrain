from __future__ import annotations


class ContentIntelligenceEngine:
    def detect_search_intent(self, query: str) -> str:
        q = query.lower()
        if "risk" in q or "too high" in q:
            return "risk"
        if "surviv" in q or "make it work" in q:
            return "survivability"
        if "salary" in q:
            return "salary_sufficiency"
        return "affordability"

    def match_serp_pattern(self, serp_row: dict) -> str:
        if serp_row.get("google_has_calculator") or serp_row.get("has_calculator"):
            return "calculator_heavy"
        if (serp_row.get("google_forum_ratio") or serp_row.get("forum_ratio", 0)) >= 0.4:
            return "ugc_forum"
        return "mixed_informational"

    def analyze_serp_structure(self, serp_row: dict) -> dict:
        pattern = self.match_serp_pattern(serp_row)
        features = {
            "pattern": pattern,
            "forum_ratio": serp_row.get("google_forum_ratio", serp_row.get("forum_ratio", 0.0)),
            "authority_count": serp_row.get("google_authority_count", 0),
            "has_calculator": bool(serp_row.get("google_has_calculator") or serp_row.get("has_calculator")),
        }
        return features

    def generate_content_variations(self, keyword: dict, serp_row: dict | None = None) -> list[dict]:
        serp_row = serp_row or {}
        intent = self.detect_search_intent(keyword.get("query", ""))
        pattern = self.match_serp_pattern(serp_row)
        base = {
            "intent": intent,
            "pattern": pattern,
            "city": keyword.get("city"),
            "salary": keyword.get("salary"),
            "rent": keyword.get("rent"),
        }
        return [
            {**base, "variant": "decision_heavy", "angle": "calculator + recommendation"},
            {**base, "variant": "data_heavy", "angle": "dataset + comparisons"},
            {**base, "variant": "narrative", "angle": "persona + tradeoff story"},
        ]

    def adapt_content_structure(self, keyword: dict, serp_row: dict | None = None) -> dict:
        serp_row = serp_row or {}
        analysis = self.analyze_serp_structure(serp_row)
        variants = self.generate_content_variations(keyword, serp_row)
        selected = variants[0] if variants else {}
        if analysis["pattern"] == "ugc_forum" and len(variants) > 1:
            selected = variants[1]
        elif analysis["pattern"] == "mixed_informational" and len(variants) > 2:
            selected = variants[2]
        return {"analysis": analysis, "selected_variant": selected, "variants": variants}
