from __future__ import annotations


class TemplateEngine:
    VARIANTS = [
        {"name": "decision_heavy", "sections": ["summary", "risk", "survivability", "actions"]},
        {"name": "data_heavy", "sections": ["dataset", "model", "comparison", "recommendations"]},
        {"name": "narrative", "sections": ["persona", "cashflow", "tradeoffs", "next_steps"]},
    ]

    def run(self, clusters: list[dict]):
        out = []
        for i, cluster in enumerate(clusters):
            variant = self.VARIANTS[(i + len(cluster.get("intent", ""))) % len(self.VARIANTS)]
            c = dict(cluster)
            c["template"] = variant["name"]
            c["layout"] = variant["sections"]
            out.append(c)
        return out
