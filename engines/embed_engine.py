from __future__ import annotations

from pathlib import Path

from .common import ROOT


class EmbedEngine:
    def run(self):
        widgets = {
            "rent-affordability-widget.html": "<div class='rb-widget compact' data-widget='affordability'></div>",
            "rent-risk-widget.html": "<div class='rb-widget card' data-widget='risk'></div>",
            "rent-survivability-widget.html": "<div class='rb-widget table' data-widget='survivability'></div>",
        }
        embeds = []
        for name, body in widgets.items():
            code = f"{body}<script src='https://cdn.rentbrain.local/widgets.js' async></script>"
            Path(ROOT / "embeds" / name).write_text(code)
            embeds.append({"name": name, "embed_code": code})
        return embeds
