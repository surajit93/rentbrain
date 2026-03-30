from __future__ import annotations

from .common import load_json


class BacklinkEngine:
    def run(self):
        posts = load_json("logs/distribution_plan.json").get("posts", [])
        channels = sorted({p.get("channel") for p in posts if p.get("channel")})
        return {
            "strategy": "embed_and_answer_outreach",
            "channels": channels,
            "target_weekly_outreach": max(10, len(posts) // 3),
        }
