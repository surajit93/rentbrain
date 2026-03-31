from __future__ import annotations


def get_domains(keyword: str, serp_record: dict | None = None) -> list[str]:
    """Safely derive domain hints for a keyword from optional SERP record metadata."""
    if isinstance(serp_record, dict):
        domains = serp_record.get("domains", [])
        if isinstance(domains, list):
            return [str(d) for d in domains]
    return []


def is_weak_serp(domains):
    strong_domains = ["zillow.com", "apartments.com", "nerdwallet.com", "bankrate.com"]
    strong_count = sum([1 for d in domains[:5] if any(sd in d for sd in strong_domains)])
    return strong_count <= 2
