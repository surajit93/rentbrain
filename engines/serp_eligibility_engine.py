from __future__ import annotations

from .common import load_json


class SerpEligibilityEngine:
    def run(self, serp_rows: list[dict]) -> list[dict]:
        cfg = load_json("config.json")
        blocked_domains = set(cfg.get("serp_rules", {}).get("high_authority_domains", []))
        allowed = []
        for row in serp_rows:
            if row.get("source_status") != "ok":
                row["eligibility"] = "BLOCK"
                continue
            if row.get("classification") == "unknown":
                row["eligibility"] = "BLOCK"
                continue
            if row.get("result_count", 0) < 5:
                row["eligibility"] = "BLOCK"
                continue
            domains = set(row.get("top_domains", []))
            authority_count = sum(1 for d in domains if d in blocked_domains)
            forum_ratio = row.get("forum_ratio", 0)
            has_calculator = row.get("has_calculator", False)
            if authority_count >= 2 or has_calculator:
                row["eligibility"] = "BLOCK"
                continue
            if row.get("classification") != "weak":
                row["eligibility"] = "BLOCK"
                continue
            if forum_ratio < 0.2:
                row["eligibility"] = "BLOCK"
                continue
            row["eligibility"] = "ALLOW"
            allowed.append(row)
        return allowed
