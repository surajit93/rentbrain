from __future__ import annotations


class TemplateEngine:
    VARIANTS = [
        {"name": "decision_heavy", "sections": ["summary", "risk", "survivability", "actions"]},
        {"name": "data_heavy", "sections": ["dataset", "model", "comparison", "recommendations"]},
        {"name": "narrative", "sections": ["persona", "cashflow", "tradeoffs", "next_steps"]},
    ]

    def run(self, clusters: list[dict], learning: dict | None = None):
        learning = learning or {}
        template_rank = learning.get("template_rank", {})
        winning_templates = set(learning.get("patterns", {}).get("winning_templates", []))
        ordered = sorted(self.VARIANTS, key=lambda v: template_rank.get(v["name"], 0), reverse=True)
        variant_pool = ordered if any(template_rank.values()) else self.VARIANTS

        out = []
        for i, cluster in enumerate(clusters):
            if winning_templates:
                prioritized = [v for v in variant_pool if v["name"] in winning_templates]
                fallback = [v for v in variant_pool if v["name"] not in winning_templates]
                local_pool = (prioritized + fallback) or variant_pool
            else:
                local_pool = variant_pool
            variant = local_pool[(i + len(cluster.get("intent", ""))) % len(local_pool)]
            c = dict(cluster)
            c["template"] = variant["name"]
            c["layout"] = variant["sections"]
            out.append(c)
        return out
