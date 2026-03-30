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
        ordered = sorted(self.VARIANTS, key=lambda v: template_rank.get(v["name"], 0), reverse=True)
        variant_pool = ordered if any(template_rank.values()) else self.VARIANTS

        out = []
        for i, cluster in enumerate(clusters):
            variant = variant_pool[(i + len(cluster.get("intent", ""))) % len(variant_pool)]
            c = dict(cluster)
            c["template"] = variant["name"]
            c["layout"] = variant["sections"]
            out.append(c)
        return out
