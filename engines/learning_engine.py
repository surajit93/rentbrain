from __future__ import annotations

from .common import load_json, save_json, now_iso


class LearningEngine:
    def load(self) -> dict:
        prior_strategy = load_json("indexes/strategy.json")
        prior_learning = load_json("indexes/learning_index.json")
        learning = prior_learning.get("learning", {}) if isinstance(prior_learning, dict) and prior_learning.get("learning") else (
            prior_strategy.get("learning", {}) if isinstance(prior_strategy, dict) else {}
        )
        learning.setdefault("template_rank", {})
        learning.setdefault("cluster_rank", {})
        learning.setdefault("structure_rank", {})
        learning.setdefault("distribution_rank", {})
        learning.setdefault("history", [])
        learning.setdefault("patterns", {})
        learning.setdefault("controller_profiles", [])
        return learning

    def update(
        self,
        learning: dict,
        pages: list[dict],
        perf: dict,
        clusters: list[dict],
        distribution_feedback: dict | None = None,
        controller_context: dict | None = None,
    ) -> dict:
        distribution_feedback = distribution_feedback or {}
        controller_context = controller_context or {}
        by_slug = {p.get("slug"): p for p in perf.get("pages", [])}
        for page in pages:
            slug = page.get("slug")
            m = by_slug.get(slug, {})
            impressions = int(m.get("impressions", 0))
            ctr = float(m.get("ctr", 0))
            if impressions < 5:
                continue

            template = page.get("template", "unknown")
            learning["template_rank"][template] = round(learning["template_rank"].get(template, 0.0) * 0.8 + ctr * 0.2, 4)

            cluster = page.get("cluster_id") or "unknown"
            learning["cluster_rank"][cluster] = round(learning["cluster_rank"].get(cluster, 0.0) * 0.75 + ctr * 0.25, 4)

            layout = "|".join(page.get("layout", [])) or "none"
            learning["structure_rank"][layout] = round(learning["structure_rank"].get(layout, 0.0) * 0.7 + ctr * 0.3, 4)

        for channel, stats in distribution_feedback.items():
            ctr = float(stats.get("ctr", 0.0))
            impressions = int(stats.get("impressions", 0))
            if impressions < 5:
                continue
            learning["distribution_rank"][channel] = round(learning["distribution_rank"].get(channel, 0.0) * 0.7 + ctr * 0.3, 4)

        cluster_scores = sorted(learning["cluster_rank"].items(), key=lambda kv: kv[1], reverse=True)
        template_scores = sorted(learning["template_rank"].items(), key=lambda kv: kv[1], reverse=True)
        learning["patterns"] = {
            "winning_clusters": [k for k, _ in cluster_scores[:15]],
            "winning_templates": [k for k, _ in template_scores[:5]],
            "high_ctr_threshold": round(max([s for _, s in cluster_scores[:10]] + [0.04]), 4),
            "observed_cluster_count": len(clusters),
            "winning_structures": [k for k, _ in sorted(learning["structure_rank"].items(), key=lambda kv: kv[1], reverse=True)[:5]],
            "distribution_winners": [k for k, _ in sorted(learning["distribution_rank"].items(), key=lambda kv: kv[1], reverse=True)[:3]],
        }

        learning["history"].append(
            {
                "at": now_iso(),
                "site_ctr": perf.get("site", {}).get("ctr", 0),
                "indexing_rate": perf.get("site", {}).get("indexing_rate", 0),
                "impressions": perf.get("site", {}).get("impressions", 0),
            }
        )
        learning["history"] = learning["history"][-100:]

        learning["controller_profiles"].append(
            {
                "at": now_iso(),
                "budget_status": controller_context.get("budget_status", "unknown"),
                "serp_allowed": int(controller_context.get("serp_allowed", 0)),
                "generated": int(controller_context.get("generated", 0)),
                "winner_clusters": int(controller_context.get("winner_clusters", 0)),
                "site_ctr": perf.get("site", {}).get("ctr", 0),
                "indexing_rate": perf.get("site", {}).get("indexing_rate", 0),
            }
        )
        learning["controller_profiles"] = learning["controller_profiles"][-120:]
        return learning

    def save_snapshot(self, learning: dict):
        save_json("indexes/learning_index.json", {"updated_at": now_iso(), "learning": learning})
