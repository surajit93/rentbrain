from __future__ import annotations

from .common import load_json, save_json, now_iso


class DistributionEngine:
    def run(self, pages: list[dict], perf: dict | None = None):
        perf = perf or {}
        prior = load_json("logs/distribution_plan.json")
        by_slug = {p.get("slug"): p for p in perf.get("pages", [])}
        posts = []
        feedback = {"reddit": {"impressions": 0, "clicks": 0}, "quora": {"impressions": 0, "clicks": 0}}

        for p in pages[:30]:
            res = p.get("calculator", {})
            metric = by_slug.get(p.get("slug"), {})
            persona = "single renter" if p.get("scenario") == "alone" else ("household" if p.get("scenario") == "family" else "shared housing")

            reddit = {
                "channel": "reddit",
                "style": "discussion",
                "tone": "peer-to-peer",
                "title": f"Trying to make ${int(p['salary'])} work in {p['city']} — is ${int(p['rent'])} too high?",
                "body": (
                    f"I am a {persona} in {p['city']}. After tax monthly net is ${res.get('monthly_net', 0)}, "
                    f"post-rent cash is ${res.get('post_rent_cash', 0)}, risk score {res.get('risk_score', 0)}. "
                    "What tradeoffs did you make in this scenario?"
                ),
                "link": f"/pages/{p['slug']}.json?utm_source=reddit",
                "slug": p["slug"],
                "observed_feedback": {
                    "impressions": metric.get("impressions", 0),
                    "clicks": metric.get("clicks", 0),
                },
            }
            quora = {
                "channel": "quora",
                "style": "expert-answer",
                "tone": "advisory",
                "title": f"Can you afford ${int(p['rent'])} rent in {p['city']} on ${int(p['salary'])}?",
                "body": (
                    f"Model output for {persona}: affordability is {res.get('affordability', 'unknown')}. "
                    f"Stability is {res.get('stability', 'unknown')} with survivability {res.get('survivability_months', 0)} months."
                ),
                "link": f"/pages/{p['slug']}.json?utm_source=quora",
                "slug": p["slug"],
                "observed_feedback": {
                    "impressions": metric.get("impressions", 0),
                    "clicks": metric.get("clicks", 0),
                },
            }
            posts.extend([reddit, quora])
            for channel in ["reddit", "quora"]:
                feedback[channel]["impressions"] += metric.get("impressions", 0)
                feedback[channel]["clicks"] += metric.get("clicks", 0)

        for channel in feedback:
            impr = feedback[channel]["impressions"]
            clk = feedback[channel]["clicks"]
            feedback[channel]["ctr"] = round(clk / impr, 4) if impr else 0.0

        history = prior.get("history", [])
        history.append({"at": now_iso(), "feedback": feedback})
        history = history[-30:]
        save_json("logs/distribution_plan.json", {"updated_at": now_iso(), "posts": posts, "feedback": feedback, "history": history})
        return posts
