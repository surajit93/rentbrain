from __future__ import annotations

from .common import load_json, save_json, now_iso


class BacklinkEngine:
    def run(self):
        distribution = load_json("logs/distribution_plan.json")
        posts = distribution.get("posts", [])
        feedback = distribution.get("feedback", {})

        channel_links = {}
        for p in posts:
            channel = p.get("channel", "unknown")
            channel_links.setdefault(channel, []).append(p.get("link"))

        leaderboard = []
        for channel, stats in feedback.items():
            leaderboard.append(
                {
                    "channel": channel,
                    "impressions": stats.get("impressions", 0),
                    "clicks": stats.get("clicks", 0),
                    "ctr": stats.get("ctr", 0.0),
                    "links": len(channel_links.get(channel, [])),
                }
            )
        leaderboard.sort(key=lambda r: (r.get("impressions", 0), r.get("ctr", 0)), reverse=True)

        out = {
            "updated_at": now_iso(),
            "strategy": "platform_tuned_outreach",
            "channels": sorted(channel_links.keys()),
            "target_weekly_outreach": max(10, len(posts) // 3),
            "channel_leaderboard": leaderboard,
            "winning_distribution_channel": leaderboard[0]["channel"] if leaderboard else "unknown",
        }
        save_json("indexes/internal_link_index.json", {**load_json("indexes/internal_link_index.json"), "backlink_feedback": out})
        return out
