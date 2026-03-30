from __future__ import annotations

from .common import save_json, now_iso


class DistributionEngine:
    def run(self, pages: list[dict]):
        posts = []
        for p in pages[:30]:
            res = p.get("calculator", {})
            reddit = {
                "channel": "reddit",
                "style": "discussion",
                "title": f"Trying to make ${int(p['salary'])} work in {p['city']} — is ${int(p['rent'])} too high?",
                "body": f"Scenario: {p['scenario']}. Post-rent cash is ${res.get('post_rent_cash', 0)} and risk score is {res.get('risk_score', 0)}. What would you cut first?",
                "link": f"/pages/{p['slug']}.json",
            }
            quora = {
                "channel": "quora",
                "style": "expert-answer",
                "title": f"Can you afford ${int(p['rent'])} rent in {p['city']} on ${int(p['salary'])}?",
                "body": f"Short answer: {res.get('affordability', 'unknown')}. The monthly net estimate is ${res.get('monthly_net', 0)} with stability {res.get('stability', 'unknown')}.",
                "link": f"/pages/{p['slug']}.json",
            }
            posts.extend([reddit, quora])
        save_json("logs/distribution_plan.json", {"updated_at": now_iso(), "posts": posts})
        return posts
