from __future__ import annotations

from .common import load_json, now_iso, save_json


class AuthorityGrowthEngine:
    def track_backlinks(self) -> dict:
        plan = load_json("logs/distribution_plan.json")
        posts = plan.get("posts", [])
        backlinks = []
        for p in posts:
            backlinks.append({"channel": p.get("channel"), "slug": p.get("slug"), "link": p.get("link")})
        doc = {"updated_at": now_iso(), "backlinks": backlinks}
        save_json("indexes/backlinks_v2.json", doc)
        return doc

    def compute_authority_score(self) -> dict:
        backlinks = load_json("indexes/backlinks_v2.json").get("backlinks", [])
        domains = {b.get("channel") for b in backlinks if b.get("channel")}
        score = round(min(100.0, len(backlinks) * 0.2 + len(domains) * 4), 2)
        out = {"updated_at": now_iso(), "authority_score": score, "link_count": len(backlinks), "source_diversity": len(domains)}
        save_json("indexes/authority_score_v2.json", out)
        return out

    def compute_domain_score(self) -> dict:
        return self.compute_authority_score()

    def track_link_velocity(self) -> dict:
        score = load_json("indexes/authority_score_v2.json")
        prior = load_json("indexes/link_velocity_v2.json")
        history = prior.get("history", []) if isinstance(prior, dict) else []
        history.append({"at": now_iso(), "links": score.get("link_count", 0), "authority_score": score.get("authority_score", 0)})
        history = history[-90:]
        if len(history) >= 2:
            velocity = history[-1]["links"] - history[-2]["links"]
        else:
            velocity = 0
        out = {"updated_at": now_iso(), "velocity": velocity, "history": history}
        save_json("indexes/link_velocity_v2.json", out)
        return out

    def track_growth_velocity(self) -> dict:
        return self.track_link_velocity()
